function onOpen() {
  var ui = SpreadsheetApp.getUi();

  var subMenu_pr = ui.createMenu('Periodic Review')
    .addSubMenu(
      ui.createMenu('Notification')
        .addItem('T60/30_Report', 'send_3060')
    )
    .addSeparator()
    .addSubMenu(
      ui.createMenu('Reminder List')
        .addItem('T60 Block List Update', 'transferPR_T60')
        .addItem('T30 Alert List Replace', 'transferPR_T30')
    );

  var subMenu_mt = ui.createMenu('Material Trigger')
    .addSubMenu(
      ui.createMenu('Notification')
        .addItem('T30/20_Report', 'send_2030')
    )
    .addSeparator()
    .addSubMenu(
      ui.createMenu('Reminder List')
        .addItem('T30 Block List Update', 'transferMT_T30')
    );

  ui.createMenu('🐢 SmartFunctions')
    .addSubMenu(subMenu_pr)
    .addSeparator()
    .addSubMenu(subMenu_mt)
    .addSeparator()
    .addItem('How to use', 'instruction')
    .addToUi();
}
