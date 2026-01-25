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
onEdit(e) 是一个“简单触发器”

Google Sheets 内置两种触发器：
  简单触发器（Simple Trigger）
  名字必须是 onEdit
  不能改名
  不能手动运行
  不能传参
  只有用户编辑表格时才会自动触发

Google Sheets 会自动传入一个事件对象 e，里面包含：
  e.range → 被编辑的单元格
  e.value → 新值
  e.oldValue → 旧值
  e.source → 当前 Spreadsheet
  e.user → 编辑者

你不需要传参，Google 会自动传。
*/
