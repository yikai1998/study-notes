function updateAllTables(url) {
  var body = DocumentApp.openByUrl(url).getBody();
  var ab_info = ab_extractDetails()
  var tables = body.getTables();
  for (var t = 0; t < tables.length; t++) {
    var table = tables[t];
    for (var r = 0; r < table.getNumRows(); r++) {
      var row = table.getRow(r);
      for (var c = 0; c < row.getNumCells(); c++) {
        var cell = row.getCell(c);
        var lines = cell.getText().split('\n');
        for (var i = 0; i < lines.length - 1; i++) {
          if (lines[i] == 'Company’s full legal name:') {
            lines[i + 1] = ab_info.companyNameEn
          }
          else if (lines[i] == 'Head quarter’s address:') {
            lines[i + 1] = ab_info.streetAddressEnglish
          }
          else if (lines[i] == 'City:') {
            lines[i + 1] = ab_info.cityEnglish
          }
          else if (lines[i] == 'State/Province:') {
            lines[i + 1] = ab_info.stateEnglish
          }
          else if (lines[i] == 'Country:') {
            lines[i + 1] = ab_info.countryCode
          }
          else if (lines[i] == 'Postal Code:') {
            lines[i + 1] = ab_info.postcode
          }
          else if (lines[i] == 'Business Phone #:') {
            lines[i + 1] = ab_info.phoneNumber
          }
          else if (lines[i] == 'Government Tax I.D. or local equivalent:') {
            lines[i + 1] = ab_info.businessRegistrationNumber
          }
          else if (lines[i] == 'Web Address:') {
            lines[i + 1] = ab_info.verifiedUrl
          }
          else if (lines[i] == 'Business model:') {
            lines[i + 1] = ab_info.descriptionOfGoodsOrServices
          }
          else if (lines[i] == 'Name of Company') {
            lines[i] = `Name of Company  _ ${ab_info.companyNameEn} _`
          }


          cell.setText(lines.join('\n'));
        }

        Logger.log('表格%d 行%d 列%d 内容: %s', t+1, r+1, c+1, row.getCell(c).getText());
      }
    }
  }
}
