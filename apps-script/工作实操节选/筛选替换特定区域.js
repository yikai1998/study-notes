function transferPR_T30() {
  const sourceSheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('Workpaper-A');
  const targetSheet = SpreadsheetApp
    .openByUrl('xxxx')
    .getSheetByName('Periodical Review (PR)');

  const reason = 'PR Reminder: over 30 days no RFI responce';
  const today = Utilities.formatDate(new Date(), 'GMT+8', 'yyyy-MM-dd');

  const sourceData = sourceSheet
    .getRange(`A2:O${getLastRow(sourceSheet, 'A:A')}`)
    .getDisplayValues();

  const newReminderList = sourceData
    .filter(r => [' [T+30]', ' [T+45]'].includes(r[9]))
    .map(r => [
      r[2],                    // summary
      r[1],                    // legalEntityId
      reason,
      r[13],                   // accountOwner
      r[11],                   // customerSegment
      r[12],                   // org_L2
      `Added on ${today}`
    ]);

  const existingList = targetSheet
    .getRange(`A2:G${getLastRow(targetSheet, 'B:B')}`)
    .getDisplayValues()
    .filter(r => r[2] !== reason);

  const finalList = existingList.concat(newReminderList);

  targetSheet.getRange('A2:G').clearContent();

  if (finalList.length) {
    targetSheet
      .getRange(2, 1, finalList.length, finalList[0].length)
      .setValues(finalList);
  }

  Browser.msgBox('🍻Reminder list is updated successfully!');
}
