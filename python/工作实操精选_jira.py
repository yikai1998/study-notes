# coding = utf-8
import requests
from requests.auth import HTTPBasicAuth
from jira import JIRA
import time
import certifi


# 基本config
jira_server = 'https://airwallex.atlassian.net'
jira_url = 'https://airwallex.atlassian.net/rest/api/3/search'
jira_username = 'you jira account mail'
jira_token = 'your jira account token'
jira_basic_auth = HTTPBasicAuth(username=jira_username, password=jira_token)  # 给 requests 传的登录凭证
jira_client = JIRA(server=jira_server, basic_auth=(jira_username, jira_token))  # Jira SDK client，对 Jira API 的封装入口。这是 jira Python 库的客户端对象。不是单纯“认证信息”，而是一个已经登录好的 Jira client。
jira_headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}


# 用jql搜tickets
jql_query = "PROJECT IN (CEOPS) AND issuetype in ('CN Inbound File Upload','Multiple GA') AND updated >= -5d ORDER BY created ASC"
def jql_search(jql, batch_size: int = 100, limit: int = 1000):
    all_tickets = []
    next_token = None
    url = 'https://airwallex.atlassian.net/rest/api/3/search/jql'
    while True:
        payload = {
            'fields': ['summary','status', 'assignee', 'issuetype', 'customfield_11507'],
            'fieldsByKeys': True,  # 告诉 Jira：我这里传的是 key，请按 key 理解
            'jql': jql,
            'maxResults': batch_size,
            # 'startAt': begin  # 新版接口已不再用 startAt 分页，而是用 nextPageToken - 20250918
        }
        if next_token:
            payload['nextPageToken'] = next_token
        response = requests.post(url=url, json=payload, headers=jira_headers, auth=jira_basic_auth)
        response.raise_for_status()
        r = response.json()
        tickets = r.get('issues', [])
        next_token = r.get('nextPageToken', None)
        all_tickets.extend(tickets)
        if len(all_tickets) >= limit:
            all_tickets = all_tickets[:limit]
            break
        if not next_token:
            break

    return all_tickets


# 通过key搜索该ticket的status transition history
# 法1
def get_status_change_history(issue_key):
    url = f"{jira_server}/rest/api/3/issue/{issue_key}?expand=changelog"
    response = requests.get(url, headers=jira_headers, auth=jira_basic_auth)
    if response.status_code == 200:
        # Parse the JSON response
        issue_data = response.json()
        changelog = issue_data.get('changelog', {})
        histories = changelog.get('histories', [])
        # Iterate through the histories to find status changes
        for history in histories:
            author_email = history.get('author', {}).get('emailAddress', 'Unknown Email')
            for item in history.get('items', []):
                if item['field'] == 'status':
                    created_date = history['created']
                    from_status = item['fromString']
                    to_status = item['toString']
                    print(f"Operator: {author_email}, Date: {created_date}, From: {from_status}, To: {to_status}")
    else:
        print(f"Failed to retrieve issue changelog: {response.status_code}")
        print(response.text)

# 法2
def jira_transitions(key):
    logs = jira_client.issue(key, expand='changelog').changelog.histories
    logs = [
        [(log.created,act.fromString,act.toString) for act in log.items if act.field == 'status']
        for log in logs
    ]
    logs = [log for log in logs if log]
    return logs


# update jira ticket status， 好像也可以同时comment，暂未研究
jira_client.transition_issue(key, 'Ask for URL/Doc')  # transition (str): ID or name of the transition to perform


# 评论ticket
def comment_ticket(key, wording):
    url = f'https://airwallex.atlassian.net/rest/api/latest/issue/{key}/comment'
    options = {
        "body": wording,
        "properties": [{
            "key": "sd.public.comment",
            "value": {
                "internal": True  # 是否设定为internal comment
            }
        }]
    }
    r = requests.post(url=url, json=options, headers=jira_headers, verify=certifi.where(), allow_redirects=False, auth=jira_basic_auth)
    r.raise_for_status()
    r = r.json()
    return r


# update jira fields, e.g.priority
def jira_update(key, assignee_id, reporter_id, participants_field_id, new_participants_ids, level='1'):
    url = f'https://airwallex.atlassian.net/rest/api/3/issue/{key}'
    payload = {
        'fields': {
            'priority': {
                'id': level,  # 1 by default, means HIGHEST
            },
            # 'customfield_12707': 'account_id_test1',
            # 'description': description_adf,
            'assignee': {
              'id': assignee_id
            },
            'reporter': {
                'id': reporter_id
            },
            participants_field_id: [
                {'accountId': accountId} for accountId in new_participants_ids
            ]
        }
    }
    r = requests.put(url, json=payload, headers=jira_headers, auth=jira_basic_auth)
    r.raise_for_status()  # 204 means fields updated successfully
    return r.status_code
'''
the previous message will replace the current list of participants with the new list specified in the new_participants_ids. 
If you want to add a participant without removing the existing ones, 
you would have to first get the current list of participants, 
add the new participant's ID to that list, 
and then update the field with the combined list

get_response = requests.get(
    url=f'https://airwallex.atlassian.net/rest/api/3/issue/{i}',
    headers=jira_headers,
    auth=jira_basic_auth
)
if get_response.status_code == 200:
    current_participants = get_response.json()['fields'].get(participants_field_id, [])  # 可以很方便的找到特定key ticket的相应字段值
    print(current_participants)
else:
    print(f"Failed to get current participants: {get_response.content}")
    exit()
if not any(participant['accountId'] == new_participant_id for participant in current_participants):
    current_participants.append({"accountId": new_participant_id})
'''


# update jira fields like cascading fields
payload = {
    'fields': {
        'customfield_12720': {
            'value': 'Amend KYC Profile',
            'child': {
                'value': 'Change in Country Exposure'
            }
        }
    }
}
response = requests.put(
    url=f'https://airwallex.atlassian.net/rest/api/3/issue/{i}',
    headers=headers,
    auth=auth,
    json=payload
)
if response.status_code == 204:
    print('Cascading select custom field updated successfully.')
else:
    print(f'Failed to update field: {response.status_code} - {response.text}')

# create jira ticket(s)
new_issue_dict = {
    'project': {'key': 'KYCSD'},
    'summary': 'test by ben 0523',
    'description': 'created by python 0523',
    'issuetype': {'name': 'Task'}
}
new_issue = jira_client.create_issue(fields=new_issue_dict)
# create jira tickets
# The create_issues method expects a list of dictionaries, where each dictionary represents the fields for an issue you want to create.
# The list can contain different types of issues or the same type with different data.
new_issues = jira_client.create_issues(field_list=issue_list)
