```gs
function extractRGB_withPrompt() {
  const ui = SpreadsheetApp.getUi();

  // 输入颜色范围
  const inputRangePrompt = ui.prompt(
    "输入颜色范围",
    "请输入待提取背景颜色的范围（例如：A1:C3）",
    ui.ButtonSet.OK_CANCEL
  );
  if (inputRangePrompt.getSelectedButton() != ui.Button.OK) return;
  const inputRangeA1 = inputRangePrompt.getResponseText();

  // 输入输出起点
  const outputStartPrompt = ui.prompt(
    "输入输出起点",
    "请输入输出结果的左上角单元格（例如：E1）",
    ui.ButtonSet.OK_CANCEL
  );
  if (outputStartPrompt.getSelectedButton() != ui.Button.OK) return;
  const outputStartA1 = outputStartPrompt.getResponseText();

  extractRGB(inputRangeA1, outputStartA1);
}


// 主函数：带标题行
function extractRGB(inputRangeA1, outputStartA1) {
  const sheet = SpreadsheetApp.getActiveSheet();
  const inputRange = sheet.getRange(inputRangeA1);
  const inputValues = inputRange.getBackgrounds();

  const numRows = inputValues.length;
  const numCols = inputValues[0].length;

  // ===== 构建输出数组 =====
  const output = [];

  // 标题行
  const header = [];
  for (let c = 0; c < numCols; c++) {
    header.push("R", "G", "B");
  }
  output.push(header);

  // 数据行
  for (let r = 0; r < numRows; r++) {
    const row = [];
    for (let c = 0; c < numCols; c++) {
      const hex = inputValues[r][c];
      const rgb = hexToRgb(hex);
      row.push(rgb.r, rgb.g, rgb.b);
    }
    output.push(row);
  }

  // ===== 写入输出区域 =====
  const startRange = sheet.getRange(outputStartA1);
  const outRange = sheet.getRange(
    startRange.getRow(),
    startRange.getColumn(),
    numRows + 1,
    numCols * 3
  );

  outRange.setValues(output);
}


// HEX → RGB
function hexToRgb(hex) {
  if (!hex || hex == "#ffffff" || hex == "#FFFFFF") {
    return { r: 255, g: 255, b: 255 };
  }
  return {
    r: parseInt(hex.substring(1, 3), 16),  // 标准的 HEX 颜色格式, 每两个字符表示一个 16 进制数, 最后当成 16 进制 转成十进制
    g: parseInt(hex.substring(3, 5), 16),
    b: parseInt(hex.substring(5, 7), 16)
  };
}
```
