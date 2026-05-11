function onEdit(e) { 
  var sheet = e.source.getActiveSheet(); 
  var range = e.range; 
  var currentColumn = range.getColumn(); 
  var currentRow = range.getRow(); 
  var currentSelectedOption = range.getValue(); 
  var dependentCell = sheet.getRange(currentRow, currentColumn+1); 
  
  dependentCell.clearDataValidations(); // Clear the current validation in next Column right side 

  var namedRanges = { 
    // Define the named ranges for each main option, separately maintain in gsheet tab, or directly write in here 
    "上海": sheet.getRange("Options!B2:D2"), 
    "北京": sheet.getRange("Options!B3:D3"), 
    "江苏": sheet.getRange("Options!B4:D4"), 
    "广东": ['华理', '中山', '暨南'] 
  };  

  // Check if the selected option has a corresponding named range, if no then nothing happens 
  if (namedRanges[currentSelectedOption]) { 
    // Check if the related options are from range maintained or predined list in script 
    if (Array.isArray(namedRanges[currentSelectedOption])) { 
      var optionlist = namedRanges[currentSelectedOption]; 
      var rule = SpreadsheetApp.newDataValidation().requireValueInList(optionlist, true).build(); 
      dependentCell.setDataValidation(rule); 
    } else { 
    var optionrange = namedRanges[currentSelectedOption]; 
    var rule = SpreadsheetApp.newDataValidation().requireValueInRange(optionrange, true).build(); 
    dependentCell.setDataValidation(rule); 
    } 
    
  }
  
} 

/*
onEdit(e) 是 Google Sheets 的简单触发器。

如果作为 simple trigger 使用，函数名必须叫 onEdit。

它不需要手动创建触发器。

当用户手动编辑表格单元格时，Google Sheets 会自动运行它。

Google 会自动传入事件对象 e。

常用字段包括：
e.range：被编辑的 range
e.value：新值，通常只适用于单个单元格编辑
e.oldValue：旧值，如果有的话
e.source：当前 Spreadsheet
e.user：编辑者，但不保证一定有

平时不需要自己传参。

但不能直接依赖手动 Run 测试，因为手动运行时没有真实 e 对象。
*/
