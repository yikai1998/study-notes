function instruction() {
  var htmlOutput = HtmlService
    .createHtmlOutputFromFile('how_to_use.html')
    .setWidth(900)
    .setHeight(700);

  SpreadsheetApp.getUi().showModalDialog(
    htmlOutput,
    'How to use this Gsheet to send weekly report'
  );
}
