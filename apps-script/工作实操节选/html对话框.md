```html
<!DOCTYPE html>
<html>
  <body>
    <form id="inputForm" onsubmit="handleSubmit(); return false;">
      <label for="token">Airwallex Token:</label><br>
      <input type="text" id="token" name="token" style="width:95%;" required><br><br>
      <label for="accountid">Account ID:</label><br>
      <input type="text" id="accountid" name="accountid" style="width:95%;" required><br><br>
      <label for="clientname">Client Name:</label><br>
      <input type="text" id="clientname" name="clientname" style="width:95%;" required><br><br>
      <input type="submit" value="submit">
    </form>
    <script>
      function handleSubmit() {
        var token = document.getElementById('token').value.trim();
        var accountid = document.getElementById('accountid').value.trim();
        var clientname = document.getElementById('clientname').value.trim();
        if(token && accountid && clientname) {
          google.script.run
            .withSuccessHandler(function(){google.script.host.close();})
            .infoProcess(token, accountid, clientname);
        } else {
          alert('null error!');
        }
      }
    </script>
  </body>
</html>
```


```js
function showDialog() {
  var html = HtmlService.createHtmlOutputFromFile('InfoCollection')
    .setWidth(350)
    .setHeight(240);
  DocumentApp.getUi().showModalDialog(html, 'Fill in the blanks');
}

// 处理表单内容
function infoProcess(token, accountid, clientname) {
  // 可保存到属性、全局变量等
  PropertiesService.getUserProperties().setProperty('API_TOKEN', token);
  PropertiesService.getUserProperties().setProperty('ACCOUNT_ID', accountid);
  PropertiesService.getUserProperties().setProperty('CLIENT_NAME', clientname);
  // 需要的话，此处还能做更多处理
  Logger.log('AccountId:' + accountid);
  Logger.log('ClientName:' + clientname);
  // 完成克隆
  var newTitle = PropertiesService.getUserProperties().getProperty('CLIENT_NAME');
  newTitle = `QBC DD Questionnaire - ${newTitle}`;
  var file = DriveApp.getFileById(DocumentApp.getActiveDocument().getId());
  var copiedFile = file.makeCopy(newTitle);
  var copiedUrl = copiedFile.getUrl();
  PropertiesService.getUserProperties().setProperty('COPIED_URL', copiedUrl);
}

function getHeaders(datacenter) {
  return {
    'Content-Type': 'application/json',
    'authorization': PropertiesService.getUserProperties().getProperty('API_TOKEN') || '',
    'x-data-center': datacenter
  };
}
```
