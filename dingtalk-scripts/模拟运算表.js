function runSimulation() {
    // 要求必须用Sumulation这个sheet
    const ws = getSheetByName("Simulation");  // 自定义函数 getSheetByName

    if (!ws) {
        Output.log("Cannot find sheet: Simulation");
        return;
    }

    Output.log("Using sheet: " + ws.getName());

  
    // 要求必须从 H1:H2 读取配置
    const configValues = ws.getRange("H1:H2").getValues();
    const inputRangeText = String(configValues[0][0] || "").trim();  // 已知参数存在哪个range里
    const outputRangeText = String(configValues[1][0] || "").trim();  // 输出结果存在哪个range里

    Output.log("inputRange = " + inputRangeText);
    Output.log("outputRange = " + outputRangeText);

    if (!inputRangeText) {
        Output.log("Config error: H1 input range is empty. Example: A1:A20");
        return;
    }

    if (!outputRangeText) {
        Output.log("Config error: H2 output range is empty. Example: B1:B20");
        return;
    }

    const inputRange = ws.getRange(inputRangeText);
    const outputRange = ws.getRange(outputRangeText);

    const inputValues = inputRange.getValues();
    const inputRowCount = inputValues.length;
    const outputRowCount = getRangeRowCount(outputRangeText);
    const outputColCount = getRangeColCount(outputRangeText);

    if (inputRowCount !== outputRowCount) {
        Output.log(
            `dimension mismatch: input range has ${inputRowCount} rows, while output range has ${outputRowCount} rows.`
        );
        return;
    }

    const results = [];
    Output.log("Simulation started. Total cases: " + inputRowCount);

    for (let i = 0; i < inputValues.length; i++) {
        const row = inputValues[i];  // 当前是第几行
        const result = calculateResult(row);  // 计算

        if (Array.isArray(result)) {
            results.push(result);  // 如果 calculateResult 返回数组，就作为多列输出
        } else {
            results.push([result]);  // 如果返回普通值，就作为单列输出
        }

        Output.log(
            `case ${i + 1}/${inputRowCount}: param=${param}, result=${JSON.stringify(result)}`
        );
    }

    const resultColCount = results[0] ? results[0].length : 0;
    if (resultColCount !== outputColCount) {
        Output.log(
            `column mismatch: calculation returns ${resultColCount} columns, while output range has ${outputColCount} columns.`
        );
        return;
    }

    outputRange.setValues(results);

    Output.log("Simulation completed!");
}


// 你的计算逻辑
function calculateResult(row) {
    // 如果输入是多列参数，const a = Number(row[0]); const b = Number(row[1]); ...
    return Number(row[0]) * 10;
}

// 按名称找 sheet
function getSheetByName(name) {
    const sheets = Workbook.getSheets();

    for (let i = 0; i < sheets.length; i++) {
        const sheet = sheets[i];

        if (sheet.getName() === name) {
            return sheet;
        }
    }

    return null;
}


/**
 * 获取 range 行数
 * 支持：
 * A1:A5
 * A1:B5
 * B3:D10
 * A1
 */
function getRangeRowCount(rangeText) {
    const parts = rangeText.split(":");

    if (parts.length === 1) {
        return 1;
    }

    const startRow = getRowNumberFromCell(parts[0]);
    const endRow = getRowNumberFromCell(parts[1]);

    return endRow - startRow + 1;
}


/**
 * 获取 range 列数
 * 支持：
 * A1:A5 -> 1
 * A1:B5 -> 2
 * B3:D10 -> 3
 */
function getRangeColCount(rangeText) {
    const parts = rangeText.split(":");

    if (parts.length === 1) {
        return 1;
    }

    const startCol = getColNumberFromCell(parts[0]);
    const endCol = getColNumberFromCell(parts[1]);

    return endCol - startCol + 1;
}


/**
 * 从 A1 提取行号 1
 */
function getRowNumberFromCell(cellText) {
    const match = cellText.match(/\d+/);

    if (!match) {
        throw new Error("Invalid cell address: " + cellText);
    }

    return Number(match[0]);
}


/**
 * 从 A1 提取列号
 * A -> 1
 * B -> 2
 * Z -> 26
 * AA -> 27
 */
function getColNumberFromCell(cellText) {
    const match = cellText.match(/[A-Z]+/i);

    if (!match) {
        throw new Error("Invalid cell address: " + cellText);
    }

    const letters = match[0].toUpperCase();

    let colNumber = 0;

    for (let i = 0; i < letters.length; i++) {
        colNumber = colNumber * 26 + letters.charCodeAt(i) - 64;
    }

    return colNumber;
}


runSimulation();
