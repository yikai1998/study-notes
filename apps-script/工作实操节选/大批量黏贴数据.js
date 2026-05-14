/*
如果是跨表格，而且存在实时关联的公式，最好paste to一个disconnected的中间tab，然后再自动paste arrayformula连过去，避免gsheet延迟响应
*/
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
  var batch_size = 500;
  
  // 分为 CN开头 和 非CN开头 两组
  var data_CN = [];
  var data_NonCN = [];
  
  if (if_cn) {
    for (var i = 0; i < dataRaw.length; i++) {
      var colVal = (dataRaw[i][3] || ''); // 第4列
      
      if (!colVal || ['CN', 'SG', 'MY', 'HK'].includes(colVal.substring(0, 2))) {
        data_CN.push(dataRaw[i]);
      }
    }
    
    for (var i = 0; i < data_CN.length; i += batch_size) {
      var current_batch = data_CN.slice(i, i + batch_size);
      sheetTo.getRange(destRow + i, destColumn, current_batch.length, current_batch[0].length).setValues(current_batch);
      
      Logger.log('>> batch_CN: %s', i);
      // SpreadsheetApp.flush();  // 一般不需要每批都 flush。Apps Script 会自动提交。除非你后面马上依赖表格公式计算结果
      // Utilities.sleep(1000);
    }
  } else {
    
    for (var i = 0; i < dataRaw.length; i++) {
      var colVal = (dataRaw[i][3] || ''); // 第4列
      
      // 确保 空值只进 CN
      if (colVal && !['CN', 'SG', 'MY', 'HK'].includes(colVal.substring(0, 2))) {
        data_NonCN.push(dataRaw[i]);
      }
    }
    
    for (var i = 0; i < data_NonCN.length; i += batch_size) {
      var current_batch = data_NonCN.slice(i, i + batch_size);
      sheetTo.getRange(destRow + i, destColumn, current_batch.length, current_batch[0].length).setValues(current_batch);
      
      Logger.log('>> batch_NonCN: %s', i);
      // SpreadsheetApp.flush();
      // Utilities.sleep(1000);
    }
  }

  SpreadsheetApp.flush();
}
