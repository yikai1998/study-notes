function getHolidays(ccy) {
  const sheet = SpreadsheetApp
    .openById('xxx-xxx')
    .getSheetByName('Static holiday data');

  const lastRow = sheet.getLastRow();

  const ccyValues = sheet.getRange(`B1:B${lastRow}`).getValues().flat();
  const dateValues = sheet.getRange(`F1:F${lastRow}`).getValues().flat();

  const holidayList = [];

  ccyValues.forEach((value, i) => {
    if (value === ccy && dateValues[i]) {
      const rawDate = String(dateValues[i]);

      const year = rawDate.substring(0, 4);
      const month = rawDate.substring(4, 6);
      const day = rawDate.substring(6, 8);

      holidayList.push(
        Utilities.formatDate(
          new Date(year, Number(month) - 1, day),
          'GMT+8',
          'yyyy-MM-dd'
        )
      );
    }
  });

  return holidayList;
}
