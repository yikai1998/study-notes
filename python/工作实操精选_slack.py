# search user id
from slack_sdk import WebClient
import os
import certifi
import pandas as pd
os.environ['SSL_CERT_FILE'] = certifi.where()
SLACK_USER_TOKEN = 'token'
client = WebClient(token=SLACK_USER_TOKEN)
def get_all_users():
    users = []
    cursor = None  # 用于分页的游标
    while True:  # 持续循环，直到获取所有用户
        response = client.users_list(cursor=cursor)
        if response['ok']:
            users.extend(response['members'])  # 添加当前页的用户
            # 获取下一页的 cursor
            cursor = response.get('response_metadata', {}).get('next_cursor')
            if not cursor:
                break
        else:
            break
    return users
employees = get_all_users()
# 打印用户数量
print(f'Total Users: {len(employees)}')
df_result = pd.DataFrame(columns=['slack_user_id', 'emp_name', 'emp_real_name'])
# 打印用户信息
for emp in employees[:10]:
    if not emp['deleted']:
        df_result.loc[len(df_result)] = {
            'slack_user_id': emp.get('id'),
            'emp_name':  emp.get('name'),
            'emp_real_name': emp.get('real_name'),
        }
        # 少量数据可以，大量用户时效率不高。更推荐先收集到 list，再一次性建 DataFrame：
        # rows = []; rows.append({...}); df_result = pd.DataFrame(rows);
# 输出
print(df_result)


# batch invitation
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os
import certifi
os.environ['SSL_CERT_FILE'] = certifi.where()
SLACK_BOT_TOKEN = 'token'
CHANNEL_ID = 'C08FD1U7J3H'  # Replace with your Slack channel ID
USER_IDS = ['U02KLQGEQLV']  # Replace with Slack User IDs
client = WebClient(token=SLACK_BOT_TOKEN)
def invite_users(channel_id, user_ids):
    try:
        response = client.conversations_invite(channel=channel_id, users=','.join(user_ids))
        print('Successfully invited users:', response)
    except SlackApiError as e:
        print(e)
        print(f"Error inviting users: {e.response['error']}")
# Invite Users to the Channel
invite_users(CHANNEL_ID, USER_IDS)
