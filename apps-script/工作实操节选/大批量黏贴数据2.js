function copypaste_v2(sourcelink, sourcesheet, sourcerange, destilink, destisheet, destistartcell, if_cn) {
  var ssRaw = SpreadsheetApp.openByUrl(sourcelink);
  var sheetRaw = ssRaw.getSheetByName(sourcesheet);
  var rangeRaw = sheetRaw.getRange(sourcerange);

  var ssTo = SpreadsheetApp.openByUrl(destilink);
  var sheetTo = ssTo.getSheetByName(destisheet);

  var dataRaw = rangeRaw.getDisplayValues();

  var destRange = sheetTo.getRange(destistartcell);
  var destRow = destRange.getRow();
  var destColumn = destRange.getColumn();

  var prefixes = ['CN', 'SG', 'MY', 'HK'];
  var output = [];

  for (var i = 0; i < dataRaw.length; i++) {
    var colVal = dataRaw[i][3] || '';
    var prefix = colVal.substring(0, 2);
    var isCnGroup = !colVal || prefixes.includes(prefix);

    if (if_cn ? isCnGroup : !isCnGroup) {
      output.push(dataRaw[i]);
    }
  }

  if (output.length === 0) {
    Logger.log('>> no data to paste');
    return;
  }

  var batch_size = 1000;

  // 如果目标区域是专门用来接数据的，建议写入前清空。但如果下面有别的内容，就不要这样清。
  sheetTo
  .getRange(destRow, destColumn, sheetTo.getMaxRows() - destRow + 1, rangeRaw.getNumColumns())
  .clearContent();

  for (var j = 0; j < output.length; j += batch_size) {
    var current_batch = output.slice(j, j + batch_size);

    sheetTo
      .getRange(destRow + j, destColumn, current_batch.length, current_batch[0].length)
      .setValues(current_batch);

    Logger.log('>> batch: %s', j);
  }

  SpreadsheetApp.flush();
}
