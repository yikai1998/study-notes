## get tickets queue list, with fields required
```js
function fetchJiraToSheet() {
  var sheet = SpreadsheetApp.openById('xx').getSheetById('xx');
  var jiraUrl = 'https://airwallex.atlassian.net/rest/api/3/search/jql';

  var props = PropertiesService.getScriptProperties();
  var userName = props.getProperty('JIRA_USERNAME');
  var apiToken = props.getProperty('JIRA_API_TOKEN');

  var jqlQuery = 'project = OPS_KYC and issuetype IN ("Ongoing KYC Review Request", "Periodic Review") and (updated >= "2025/01/01 00:00" or status NOT IN ("REVIEW COMPLETED - PASSED", "REVIEW COMPLETED - NO NEEDED", "CLOSED PER COMMERCIAL TEAM REQUEST", "REVIEW COMPLETED - KICKOFF OFFBOARDING")) ORDER BY created ASC';

  var pl_dic = {
    jql: jqlQuery,
    maxResults: 100,
    fields: [
      'key',
      'issuetype',
      'customfield_12706',
      'customfield_12720',
      'customfield_12711',
      'customfield_12709'
    ]
  };

  var issues = [];
  var batch = 1;

  while (true) {
    var options = {
      method: 'post',
      headers: {
        'Authorization': 'Basic ' + Utilities.base64Encode(userName + ':' + apiToken),
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      payload: JSON.stringify(pl_dic),
      muteHttpExceptions: true
    };

    var response = UrlFetchApp.fetch(jiraUrl, options);
    var code = response.getResponseCode();
    var text = response.getContentText();

    if (code < 200 || code >= 300) {
      throw new Error('Jira API error ' + code + ': ' + text);
    }

    var data = JSON.parse(text);

    if (!data.issues || data.issues.length === 0) {
      Logger.log('>> No more data');
      break;
    }

    issues = issues.concat(data.issues);
    Logger.log('>> Batch %s, issues: %s', batch, data.issues.length);

    if (data.nextPageToken) {
      pl_dic.nextPageToken = data.nextPageToken;
    } else {
      break;
    }

    batch++;
  }

  var result = [
    ['Client Legal Entity ID', 'Issue Type', 'Issue Key', 'Trigger Reason', 'Trigger Type', 'Single Pass or Not']
  ];

  issues.forEach(function(issue) {
    var f = issue.fields;

    var triggerReason = f.customfield_12720
      ? (
          f.customfield_12720.child
            ? f.customfield_12720.value + ' - ' + f.customfield_12720.child.value
            : f.customfield_12720.value + ' - NaN'
        )
      : 'NaN - NaN';

    var triggerType = f.customfield_12711
      ? f.customfield_12711.value
      : (f.issuetype.name === 'Periodic Review' ? 'Periodic Review' : 'NaN');

    var row = [
      f.customfield_12706 || 'NaN',
      f.issuetype ? f.issuetype.name : 'NaN',
      issue.key || 'NaN',
      triggerReason,
      triggerType,
      f.customfield_12709 ? f.customfield_12709.value : 'NaN'
    ];

    result.push(row);
  });

  sheet.clearContents();
  sheet.getRange(1, 1, result.length, result[0].length).setValues(result);

  Logger.log('>> Done. Total issues: %s', issues.length);
}
```

## status transition logs for single ticket
```js
function transition_records(key = ['CEOPS-24671', 'CN Inbound File Upload']) {
  var issueKey = key[0];
  var issueName = key[1];
  var jiraUrl = 'https://airwallex.atlassian.net/rest/api/3/issue/' + encodeURIComponent(issueKey) + '?expand=changelog';
  var username = 'ben.chen@airwallex.com';
  var apiToken = PropertiesService.getScriptProperties().getProperty('JIRA_API_TOKEN');

  var options = {
    method: 'get',
    headers: {
      Authorization: 'Basic ' + Utilities.base64Encode(username + ':' + apiToken),
      Accept: 'application/json'
    },
    muteHttpExceptions: true
  };

  var response = UrlFetchApp.fetch(jiraUrl, options);
  var statusCode = response.getResponseCode();

  if (statusCode < 200 || statusCode >= 300) {
    Logger.log('Jira API failed. Status: ' + statusCode);
    Logger.log(response.getContentText());
    return [];
  }

  var now = new Date();
  var cutoff = new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000);

  var data = JSON.parse(response.getContentText());
  var results = [];

  if (data.changelog) {
    var records = data.changelog.histories;

    records.forEach(record => {
      var created = new Date(record.created);
      // 如果 record.author 存在，就取 record.author.emailAddress。如果 record.author 不存在，不报错，返回 undefined。如果前面拿不到 email，就给空字符串 ''
      var authorEmail = record.author?.emailAddress || '';  

      record.items.forEach(item => {
        if (
          item.field === 'status' &&
          ['KYC Maker in review', 'WAITING FOR APPROVAL - KYC'].includes(item.fromString) &&
          created >= cutoff &&
          created <= now
        ) {
          results.push([
            issueKey,
            issueName,
            Utilities.formatDate(created, Session.getScriptTimeZone(), 'yyyy-MM-dd HH:mm:ss'),
            authorEmail,
            item.fromString,
            item.toString
          ]);
        }
      });
    });
  } else {
    Logger.log('No changelog or history data available.');
  }
  
  return results;
}
```
