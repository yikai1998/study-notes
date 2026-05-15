  // check the refresh status
  sh_accountbase.getRange('A1').activate()
  var bq_params = sh_accountbase.getCurrentCell().getDataSourceTables()[0].getStatus()

  var bq_status = bq_params.getExecutionState()
  if (bq_status != 'SUCCESS') {
    slackapp_error_alert(
      slackurl=url, 
      bq_status=bq_status, 
      error_msg=bq_params.getErrorMessage(), 
      last_refresh_time=bq_params.getLastExecutionTime(), 
      last_success_time=bq_params.getLastRefreshedTime()
    )
    return 0
  }

 // refreshDataAndContinue
  var shc = SpreadsheetApp.getActiveSpreadsheet().getSheetById('1679686918')
  shc.getRange('H2').activate()
  SpreadsheetApp.enableAllDataSourcesExecution()
  try {
    var dst = shc.getCurrentCell().getDataSourceTables()[0]
    dst.forceRefreshData()
    dst.waitForCompletion(200)
    // 刷新成功，执行后续操作
    Logger.log('数据源刷新成功')
    ... 正常操作
  } catch (error) {
    word = `数据源刷新失败: ${error.message}`
    ...
  }
