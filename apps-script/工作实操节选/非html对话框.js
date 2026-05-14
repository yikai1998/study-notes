function showOpenDialog(url) {
  var html = HtmlService.createHtmlOutput(
    "<div>Copied and Updated. Click to open the new file.<br><br>" +
    "<button onclick='window.open(\"" + url + "\", \"_blank\");google.script.host.close()'>Open New File</button></div>"
  )
  .setWidth(300)
  .setHeight(100);
  DocumentApp.getUi().showModalDialog(html, "Open New File");
}

function copyCurrentDocWithCustomTitle() {
  // 收集克隆表的基本信息
  var ui = DocumentApp.getUi();
  var response = ui.prompt('You are going to clone a new Doc', 'Please input the client name:', ui.ButtonSet.OK_CANCEL);

  if (response.getSelectedButton() != ui.Button.OK) {
    ui.alert('User cancelled.');
    return 0;
  }

  var newTitle = response.getResponseText();
  if (!newTitle) {
    ui.alert('Error! Client name should not be null.');
    return 0;
  }

  // 完成克隆
  newTitle = `QBC DD Questionnaire - ${newTitle}`;
  var file = DriveApp.getFileById(DocumentApp.getActiveDocument().getId());
  var copiedFile = file.makeCopy(newTitle);
  var copiedUrl = copiedFile.getUrl();

  // 克隆表展示
  showOpenDialog(url=copiedUrl);
}
