function getLastRow(sheet, rangeString){
  var rng = sheet.getRange(rangeString).getValues();
  var lrindex;
  
  for(var i = rng.length-1; i>=0; i--) {
    lrindex = i
    
    if(!rng[i].every( function(c) { return c == ""; } )) {
      break;
    }
  }
  
  return lrindex +1;
}
