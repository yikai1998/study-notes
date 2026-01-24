function runSimulation() {
  const ui = SpreadsheetApp.getUi();
  const ws = SpreadsheetApp.getActiveSpreadsheet().getSheetById(246538978);
  
  // 输入区范围
  const inputRangePrompt = ui.prompt(
    "the input range",
    "update the param range, e.g. A1:A20",
    ui.ButtonSet.OK_CANCEL
  );
  if (inputRangePrompt.getSelectedButton() != ui.Button.OK) return;
  let inputRange = inputRangePrompt.getResponseText();

  // 输出区范围
  const outputRangePrompt = ui.prompt(
    "the output range",
    "update the param range, e.g. B1:B20",
    ui.ButtonSet.OK_CANCEL
  );
  if (outputRangePrompt.getSelectedButton() != ui.Button.OK) return;
  let outputRange = outputRangePrompt.getResponseText();

  // 输入单元格
  const updateCellPrompt = ui.prompt(
    "the cell",
    "what is the cell to be updated from input param, e.g. F3",
    ui.ButtonSet.OK_CANCEL
  );
  if (updateCellPrompt.getSelectedButton() != ui.Button.OK) return;
  let updateCell = updateCellPrompt.getResponseText();

  // 公式单元格
  const returnCellPrompt = ui.prompt(
    "the cell",
    "what is the cell to be last result, e.g. D3",
    ui.ButtonSet.OK_CANCEL
  );
  if (returnCellPrompt.getSelectedButton() != ui.Button.OK) return;
  let returnCell = returnCellPrompt.getResponseText();

  // 读取范围
  const inputValues = ws.getRange(inputRange).getDisplayValues().flat();
  outputRange = ws.getRange(outputRange);

  // 校验输入区与输出区长度
  if (inputValues.length != outputRange.getNumRows()) {
    ui.alert(
      "dimension mismatch",
      `input range has ${inputValues.length} rows, while output range has ${outputRange.getNumRows()} rows.`,
      ui.ButtonSet.OK
    );
    return;
  }

  updateCell = ws.getRange(updateCell);
  returnCell = ws.getRange(returnCell);

  const results = [];

  // 主循环
  for (let i = 0; i < inputValues.length; i++) {
    const param = inputValues[i];

    updateCell.setValue(param);
    SpreadsheetApp.flush();

    const result = returnCell.getDisplayValue();
    results.push([result]);
  }

  // 一次性写入输出区
  outputRange.setValues(results);

  ui.alert("simulation completed !");
}
