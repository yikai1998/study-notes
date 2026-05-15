/** ----- READ ME -----
 * 
 * App: 加急Bot-II 
 * Author: yikai
 * Frequency: 30min
 * Bigquery Source: refreshed 1 hour per batch
 * Note: 企业微信机器人的markdown_v2消息有长度限制，通常是4096字节。如果消息过长，可能会被截断或发送失败
 * Date: 2025-06-19
 */

/** 用来更新标记哪些case已经被加急过了，后续就不会再掉进每次run的queue里了。只要涉及外部通知(除非是告知等候)，都会触发它 */
function add_tag(submit_time, reporter) {
  // 在form记录表中打上标记 用于区分哪些加急通知已经被完成
  var sha = SpreadsheetApp.getActiveSpreadsheet().getSheetById('2065846974');
  var ranges = sha.getRangeList(['A1:A', 'B1:B']).getRanges();
  var valuesA = ranges[0].getDisplayValues();
  var valuesB = ranges[1].getDisplayValues();
  var values = [];
  for (var i = 0; i < valuesA.length; i++) {
    values.push([
      valuesA[i][0],  // A列的值
      valuesB[i][0]  // B列的值
    ])
  }
  // 倒序遍历所有行
  for (var i = values.length - 1; i >= 0; i--) {
    // 检查A列和B列是否匹配目标值
    if (values[i][0] == submit_time && values[i][1].toLowerCase() == reporter) {
      // 找到匹配行，更新C列的值
      sha.getRange(`J${i+1}`).setValue('Y');
      break;
    }
  }
}


/** 用来存kyc同学的手机号，这样bot可以ping到他。如果不及时更新的话，会有一个参数返回提醒他们去更新手机号 */
function get_phone_list(member_list, team_tag, intl_entity=undefined) {
  var preset_mapping = {
    'ec': {'NaN': ['13302415216', '13826044260', '15622197481']},  // @wing @benny @bonnie
    'b2b': {'NaN': ['15000263110', '19186652566', '13524502262']},  // @lily @freda @piero
    'ogs': {'NaN': ['13423642298']},  // @natalie
    'intl': {
      'NaN': {
        'AIRWALLEX_MY': ['13621511377'],  // @joel
        'AIRWALLEX_HK': ['18939874070'],  // @tracy
        'AIRWALLEX_SG': ['17717929936'] // @nina
      }
    }
  }
  var kyc_list = SpreadsheetApp.getActiveSpreadsheet().getSheetById('1799752229').getRange('X:Y').getDisplayValues();  // kyc同学的名单和手机 用于企微@
  var kyc_phone_db = {};
  kyc_list.forEach(x => {
    kyc_phone_db[x[0]] = x[1].toString();
  })
  var unique_member_list = [...new Set(member_list)].filter(Boolean);  // assignee list 去重名单
  var phone_list = [];
  var not_found_members = [];  // 未在kyc_phone_db中找到的成员
  unique_member_list.forEach(x => {
    if (x == 'NaN') {
      if (team_tag == 'intl') {
        intl_entity.forEach(i => {
          phone_list.push(...preset_mapping[team_tag]['NaN'][i]);
        })
      } else {
        phone_list.push(...preset_mapping[team_tag]['NaN']);  // unassigned, 使用扩展运算符将数组元素分别添加
      }
    } 
    else if (kyc_phone_db[x]) {
      phone_list.push(kyc_phone_db[x]);
    } else {
      not_found_members.push(x);
    }
  })
  var unique_phone_list = [...new Set(phone_list)];  // 再去重一次
  var not_found_members = [...new Set(not_found_members)];

  return {
    'unique_phone_list': unique_phone_list, 
    'not_found_members': not_found_members
  }
}


/** 把form的信息和query的信息拼接起来，没有权限的bd踢掉。只看前20条。 */
function refine_data() {
  // 整理数据，以[{...}, {...}, ...]的格式呈现
  var shb = SpreadsheetApp.getActiveSpreadsheet().getSheetById('1799752229');  // [expedite bot script]
  var form_data = shb.getRange('A1:Q21').getDisplayValues(); // 企微markdown_v2对文本长度有限制，所以此处提前截止
  var bd_list = shb.getRange('U:U').getDisplayValues().flat(); // 有资格提加急的bd
  const headers = form_data[0];
  const r = [];
  for (let i = 1; i < form_data.length; i++) {
    const row = form_data[i];
    const obj = {};
    if (!bd_list.includes(row[1])) {
      Logger.log(`${row[1]} 没有权限加急。忽略。`);
      var msubject = '<NoReply> 您没有此加急渠道的申请权限 You do not have the permission to raise this KYC priority';
      var mword = '';
      mword += (`<p>您好, 我们已经收到Account ID(Jira Ticket): ${row[4]} 的加急申请。很抱歉地通知您, 为更好地管理GC, HK && SEA KYC 加急渠道，我们限制了该加急渠道的提交人员；经查询，您没有此加急渠道的申请权限。请联系您的经理确认该客户需要申请加急后, 由TA代为申请。<br>如果您希望开通加急渠道的申请权限, 请由Team Leader联系<a href="mailto:amber.deng@airwallex.com">Amber Deng</a> <br><br>`);
      mword += (`<p>Hello, we have received an KYC priority request for Account ID: ${row[4]} . We are sorry to inform you that in order to better manage the GC, HK && SEA KYC priority channel, we have limited the number of submitters for this priority channel; after checking, you do not have the permission to apply for this priority channel. Please contact your manager to confirm that the customer needs to apply for KYC priority, and then have him/her apply for the customer.<br><br>Thanks</p>`);
      MailApp.sendEmail({
        to: row[1],
        subject: msubject,
        htmlBody: mword
      });
      // 标记已发送
      add_tag(submit_time=row[0], reporter=row[1]);
      continue;
    }
    if (!row[0]) { continue }  // 跳过空行
    for (let j = 0; j < headers.length; j++) {
      obj[headers[j]] = row[j] ? row[j] : 'NaN';  // 填充空值
    }
    r.push(obj);
    Logger.log(obj);
  }

  return r
}


/** 加工信息，得知哪些case是可以被加急的 哪些是不可以的 */
function process_data_bd() {
  var raw = refine_data();
  // 区分CN和SEA
  var raw_cn = [];
  var raw_sea = [];
  raw.forEach(r => {
    if (r.sf_org_l2 == 'NaN' || r.sf_org_l2.startsWith('CN') || r.case_type == 'Ongoing Stage') {
      raw_cn.push(r);
    } else {
      raw_sea.push(r);
    }
  })
  // CN业务 - 企业微信
  var results_cn = raw_cn.map(x => {
    var conclusion = '';
    const now = new Date();
    const createTime = new Date(x.created_time.replace(' ', 'T'));
    // 1.检查有没有map到数据 总有一群臭傻逼刚创建case就来加急
    if (x.legal_entity_id == 'NaN') {
      conclusion = '无查询结果，重新提交';
    }
    // 2.检查 legal_entity_id 是否显示"暂未刷新出结果" 【区别于 未map到数据】
    else if (x.legal_entity_id == '暂未刷新出结果') {
      conclusion = '等待下轮刷新';
    }
    // 3.检查 owning_entity 是否不是 HK/SG/MY
    else if (!['AIRWALLEX_HK', 'AIRWALLEX_SG', 'AIRWALLEX_MY'].includes(x.owning_entity)) {
      conclusion = '非AWX-HK/SG/MY客户';
    }
    // 4.检查提交时间相较于case创建时间 是否小于60分钟
    else if (Math.floor((now - createTime) / (1000 * 60)) < 60) {
      conclusion = '间隔太短，重新提交';
    }
    // 5.检查 case_level 和 rfi_status
    else if ((['L1', 'L2', 'KYC L1', 'KYC L2', 'Backlog'].includes(x.case_level)) && (x.rfi_status == 'NaN' || x.rfi_status == 'CLOSED')) {
      conclusion = '已内部通知加急';
    } else {
      conclusion = '非KYC阶段';
    }
    // 标记已发送
    if (conclusion != '等待下轮刷新') {
      add_tag(submit_time=x.submit_time, reporter=x.reporter);
    }
    return {
      submit_time: x.submit_time,
      reporter: x.reporter,
      bd_owner: x.bd_owner,
      case_id_given: x.case_id_given,
      biz_name: x.biz_name,
      owning_entity: x.owning_entity,
      case_type: x.case_type,
      case_assignee: x.case_assignee,
      case_level: x.case_level,
      rfi_status: x.rfi_status,
      sf_org_l2: x.sf_org_l2,
      team_tag: x.team_tag,
      reason: x.reason,
      conclusion: conclusion
    }
  })
  //  SEA业务 - Slack
  var results_sea = raw_sea.map(x => {
    var scenario = 0; // default
    const now = new Date();
    const createTime = new Date(x.created_time.replace(' ', 'T'));
    // 1.检查有没有map到数据 - 其实会优先掉入CN
    if (x.legal_entity_id == 'NaN') {
      scenario = 1;  // 无查询结果，重新提交
    }
    // 2.检查 legal_entity_id 是否显示"暂未刷新出结果" 【区别于 未map到数据】 - 其实会优先掉入CN
    else if (x.legal_entity_id == '暂未刷新出结果') {
      scenario = 2;  // 等待下轮刷新
    }
    // 3.检查 owning_entity 是否不是 HK/SG/MY
    else if (!['AIRWALLEX_HK', 'AIRWALLEX_SG', 'AIRWALLEX_MY'].includes(x.owning_entity)) {
      scenario = 3; // 非AWX-HK/SG/MY客户
    }
    // 4.检查提交时间相较于case创建时间 是否小于60分钟
    else if (Math.floor((now - createTime) / (1000 * 60)) < 60) {
      scenario = 4; // 间隔太短，重新提交
    }
    // 5.检查 case_level 和 rfi_status
    else if (!((['L1', 'L2', 'KYC L1', 'KYC L2', 'Backlog'].includes(x.case_level)) && (x.rfi_status == 'NaN' || x.rfi_status == 'CLOSED'))) {
      scenario = 5;  // 非KYC阶段
    }
    // 标记已发送
    if (scenario != 2) {
      add_tag(submit_time=x.submit_time, reporter=x.reporter);
    }
    return {
      submit_time: x.submit_time,
      reporter: x.reporter,
      bd_owner: x.bd_owner,
      case_id_given: x.case_id_given,
      biz_name: x.biz_name,
      owning_entity: x.owning_entity,
      case_type: x.case_type,
      case_assignee: x.case_assignee,
      case_level: x.case_level,
      rfi_status: x.rfi_status,
      sf_org_l2: x.sf_org_l2,
      team_tag: x.team_tag,
      reason: x.reason,
      scenario: scenario
    }
  })
  // Logger.log(results_cn)
  return [results_cn, results_sea]
}


/** 发通知反馈给CN bd - 企业微信 summary */
function share_data_bd_cn(data) {
  // 设置每批消息包含的最大行数
  const MAX_ROWS_PER_MESSAGE = 5;
  const totalBatches = Math.ceil(data.length / MAX_ROWS_PER_MESSAGE);
  for (let batchNum = 0; batchNum < totalBatches; batchNum++) {
    const startIdx = batchNum * MAX_ROWS_PER_MESSAGE;
    const endIdx = Math.min((batchNum + 1) * MAX_ROWS_PER_MESSAGE, data.length);
    const batchData = data.slice(startIdx, endIdx);
    // 构建当前批次的消息
    let word = `### 📒 加急Bot最新批次反馈 (${batchNum + 1}/${totalBatches}) | 表格支持左右滑动\n\n`;
    word += '| Feedback | SubmitTime | Reporter | Owner | AccountId/JiraKey | ClientName | Status | RFI | Reason |\n';
    word += '| :------ | :------ | :------ | :------ | :------ | :------ | :------ | :------ | :------ |\n';
    batchData.forEach(r => {
      // 防止reason写的过于啰嗦
      var truncatedReason = r.reason.length > 10 ? r.reason.substring(0, 10) + '...' : r.reason;
      word += `| ${r.conclusion} | ${r.submit_time} | ${r.reporter} | ${r.bd_owner} | ${r.case_id_given} | ${r.biz_name} | ${r.case_level} | ${r.rfi_status} | ${truncatedReason} |\n`;
    })
    // 发送当前批次到企业微信
    var payload = {
      'msgtype': 'markdown_v2',
      'markdown_v2': {
        'content': word
      }
    }
    var options = {
      'method': 'post',
      'contentType': 'application/json',
      'payload': JSON.stringify(payload)
    }
    UrlFetchApp.fetch('https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxxx', options);  // ~cn bd群 bot url
    Utilities.sleep(1000);
  }
}


/** 发通知反馈给CN kyc - 企业微信 summary */
function share_data_kyc_cn(data) {
  var expedite_ec = data.filter(kc => kc.team_tag == 'gc-ec' && kc.case_type == 'Onboarding Stage' && kc.conclusion == '已内部通知加急')
    .sort((a, b) => {
      // 先按 case_level 升序排序
      if (a.case_level != b.case_level) {
        return a.case_level.localeCompare(b.case_level);
      }
      // 当 case_level 相同时，按 assignee 升序排序
      return (a.case_assignee || '').localeCompare(b.case_assignee || '')
    })
  var expedite_b2b = data.filter(kc => ['gc-b2b', 'uncategorised'].includes(kc.team_tag) && kc.case_type == 'Onboarding Stage' && kc.conclusion == '已内部通知加急')
    .sort((a, b) => {
      if (a.case_level != b.case_level) {
        return a.case_level.localeCompare(b.case_level)
      }
      return (a.case_assignee || '').localeCompare(b.case_assignee || '')
    })
  var expedite_ogs = data.filter(kc => kc.case_type == 'Ongoing Stage' && kc.conclusion == '已内部通知加急')
    .sort((a, b) => {
      if (a.case_level != b.case_level) {
        return a.case_level.localeCompare(b.case_level)
      }
      return (a.case_assignee || '').localeCompare(b.case_assignee || '')
    })
  var bot_url = {
    'ec': 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx',  // ~ec群 bot url
    'b2b': 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx',  // ~b2b群 bot url
    'ogs': 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx'  // ~ongoing群 bot url
  };
  [
    { data: expedite_ec, type: 'ec' },
    { data: expedite_b2b, type: 'b2b' },
    { data: expedite_ogs, type: 'ogs' }
  ].forEach(item => {
    if (item.data.length == 0) { return } // 如果没有数据则跳过
    // 设置每批消息包含的最大行数
    const MAX_ROWS_PER_MESSAGE = 5;
    const totalBatches = Math.ceil(item.data.length / MAX_ROWS_PER_MESSAGE);
    for (let batchNum = 0; batchNum < totalBatches; batchNum++) {
      const startIdx = batchNum * MAX_ROWS_PER_MESSAGE;
      const endIdx = Math.min((batchNum + 1) * MAX_ROWS_PER_MESSAGE, item.data.length);
      const batchData = item.data.slice(startIdx, endIdx);
      // 构建当前批次的消息
      let word = `### 🤖 加急Bot最新反馈 | [友情跳转](https://docs.google.com/spreadsheets/d/xxx) | (${batchNum + 1}/${totalBatches}) | 表格支持左右滑动\n\n`;
      word += '| Status | Assignee | AccountId/JiraKey | ClientName | Owner | OrgLevel2 | SubmitTime | Reason |\n';
      word += '| :------ | :------ | :------ | :------ | :------ | :------ | :------ | :------ |\n';
      batchData.forEach(r => {
        // 防止reason写的过于啰嗦
        var truncatedReason = r.reason.length > 20 ? r.reason.substring(0, 17) + '...' : r.reason;
        word += `| ${r.case_level} | ${r.case_assignee} | ${r.case_id_given} | ${r.biz_name} | ${r.bd_owner} | ${r.sf_org_l2} | ${r.submit_time} | ${truncatedReason} |\n`;
      })
      // 发送当前批次到企业微信
      var payload = {
        'msgtype': 'markdown_v2',
        'markdown_v2': {
          'content': word
        }
      }
      var options = {
        'method': 'post',
        'contentType': 'application/json',
        'payload': JSON.stringify(payload)
      }
      UrlFetchApp.fetch(bot_url[item.type], options);
      Utilities.sleep(1000);
    }
    // 在企业微信艾特人
    var assignee_list = item.data.map(i => {
      return i.case_assignee
    })
    var member_analysis = get_phone_list(member_list=assignee_list, team_tag=item.type);
    var word2 = `被@到的人请及时处理/帮忙分配case \n \n \n`;
    if (member_analysis.not_found_members.length > 0) {
      word2 += `请team-leader及时将以下邮箱的手机号更新至 https://docs.google.com/spreadsheets/d/xxx/edit?gid=1799752229#gid=1799752229 上的X:Y列,否则加急信息无法精确告知至这些同学 \n <${member_analysis.not_found_members.join('>, <')}> \n \n \n \n`;
    }
    var data2 = {
      'msgtype': 'text',
      'text': {
        'content': word2,
        'mentioned_mobile_list': member_analysis.unique_phone_list
      }
    }
    var options2 = {
      'method': 'post',
      'contentType': 'application/json',
      'payload': JSON.stringify(data2)
    }
    UrlFetchApp.fetch(bot_url[item.type], options2);
    Utilities.sleep(1000);
  })
}


/** 发通知反馈给SEA bd - slack 一条一条 */
function share_data_bd_sea(data) {
  data.forEach(r => {
    var payload_txt = 'From Bot: ' + '\n' + 
      'Hi ' + r.reporter + ', We have received your kyc review speed up application: ' + '\n' + '\n' +
      'Submit Time: ' + r.submit_time + '\n' +
      'Account ID / Jira Key: ' + r.case_id_given + '\n' +
      'Client Name / Jira Summary: ' + r.biz_name + '\n' +
      'Owning Entity: ' + r.owning_entity + '\n' +
      'BD Owner: ' + r.bd_owner + '\n' +
      'Current Status: ' + r.case_level + '\n' +
      'RFI Status: ' + r.rfi_status + '\n' +
      'Reason to speed up: ' + r.reason + '\n' + '\n';
    if (r.scenario == 0) {
      payload_txt += '✅ Already aware, will process as soon as possible.';
    }
    else if (r.scenario == 1) {
      payload_txt += '⚠️ Please double check your input info and re-submit the request after at least 45 min. We have not expedited the case by default.';
    }
    else if (r.scenario == 2) {
      payload_txt += '⚠️ Backend datasource delayed. Waiting for the next round refresh. We would update here in next round.';
    }
    else if (r.scenario == 3) {
      payload_txt += `⚠️ This is the client of ${r.owning_entity}, which would be handled by the local kyc team. You could fill in the <https://docs.google.com/forms/d/e/xxx/viewform|GoogleForm>, and the submission would be automatically sent to channels of local kyc teams`;
    }
    else if (r.scenario == 4) {
      payload_txt += '⚠️ Your submission time is even less than 1 hour from the case generation. Sorry that we have not expedited the case by default.';
    }
    else if (r.scenario == 5) {
      payload_txt += '⚠️ We found the case is not pending KYC Team now. We have not expedited the case by default.';
    }
    var param = {
      method: 'post',
      contentType: 'application/json',
      payload: JSON.stringify({
        'type': 'mrkdwn',
        'text': payload_txt
      })
    }
    UrlFetchApp.fetch('https://hooks.slack.com/services/T0SEVS2SG/xxx', param);  // ~intl bd slack channel
    Utilities.sleep(1000);
  })
}


/** 发通知反馈给SEA kyc - 企业微信 summary */
function share_data_kyc_sea(data) {
  var expedite_sea = data.filter(kc => ['intl', 'uncategorised'].includes(kc.team_tag) && kc.scenario == 0)
    .sort((a, b) => {
      // 再按 case_level 升序排序
      if (a.case_level != b.case_level) {
        return a.case_level.localeCompare(b.case_level)
      }
      // 当 case_level 相同时，按 assignee 升序排序
      return (a.case_assignee || '').localeCompare(b.case_assignee || '')
    })
  if (expedite_sea.length == 0) { return } // 如果没有数据则跳过
  var word = `### 🤖 加急Bot最新反馈 | [友情跳转](https://docs.google.com/spreadsheets/d/xxxx/edit?gid=2065846974#gid=2065846974) | 表格支持左右滑动\n\n`;
  word += '| Status | Assignee | AccountId/JiraKey | ClientName | Owner | OrgLevel2 | SubmitTime | Reason |\n';
  word += '| :------ | :------ | :------ | :------ | :------ | :------ | :------ | :------ |\n';
  expedite_sea.forEach(r => {
    // 防止reason写的过于啰嗦
    var truncatedReason = r.reason.length > 20 ? r.reason.substring(0, 17) + '...' : r.reason;
    word += `| ${r.case_level} | ${r.case_assignee} | ${r.case_id_given} | ${r.biz_name} | ${r.bd_owner} | ${r.sf_org_l2} | ${r.submit_time} | ${truncatedReason} |\n`;
  })
  // 发送到企业微信
  var data = {
    'msgtype': 'markdown_v2',
    'markdown_v2': {
      'content': word
    }
  }
  var options = {
    'method': 'post',
    'contentType': 'application/json',
    'payload': JSON.stringify(data)
  }
  UrlFetchApp.fetch('https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx', options);  // ～intl群 bot url
  // 在企业微信艾特人
  var assignee_list = expedite_sea.map(i => {
    return i.case_assignee
  })
  // 屁事多 还要根据owningentity来艾特不同的人来分配case
  var awx_entity_list = expedite_sea.map(i => {
    return i.owning_entity
  })
  var member_analysis = get_phone_list(member_list=assignee_list, team_tag='intl', intl_entity=[... new Set(awx_entity_list)]);
  var word2 = `被@到的人请及时处理/帮忙分配case \n \n \n`;
  if (member_analysis.not_found_members.length > 0) {
    word2 += `请team-leader及时将以下邮箱的手机号更新至 https://docs.google.com/spreadsheets/d/xxx 上的X:Y列,否则加急信息无法精确告知至这些同学 \n <${member_analysis.not_found_members.join('>, <')}> \n \n \n \n`;
  }
  var data2 = {
    'msgtype': 'text',
    'text': {
      'content': word2,
      'mentioned_mobile_list': member_analysis.unique_phone_list
    }
  }
  var options2 = {
    'method': 'post',
    'contentType': 'application/json',
    'payload': JSON.stringify(data2)
  }
  UrlFetchApp.fetch('https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx', options2);  // ～intl群 bot url
}


/** 先刷新bigquery，再后续。 暂时没权限自主刷新。*/
function expedite_main() {
  // refreshDataAndContinue
  var shc = SpreadsheetApp.getActiveSpreadsheet().getSheetById('1679686918');
  // A3 如果是空的，则根本就没要刷新
  if (!shc.getRange('A3').getDisplayValue()) {
    Logger.log(`没有数据需要刷新`);
    return
  }
  shc.getRange('H2').activate();
  SpreadsheetApp.enableAllDataSourcesExecution();
  try {
    var dst = shc.getCurrentCell().getDataSourceTables()[0];
    dst.forceRefreshData();
    dst.waitForCompletion(200);
    // 刷新成功，执行后续操作
    Logger.log('数据源刷新成功');
    var results = process_data_bd();
    // CN
    if (results[0].length > 0) {
      share_data_bd_cn(data=results[0]);  // 外部通知 - 企业微信
      Logger.log(`已处理 ${results[0].length} 条记录并发送至企业微信`);
      share_data_kyc_cn(data=results[0]); // 内部通知 - 企业微信
      Logger.log(`已处理 ${results[0].length} 条记录并发送至企业微信`);
    }
    // SEA
    if (results[1].length > 0) {
      share_data_bd_sea(data=results[1]); // 外部通知 - slack
      Logger.log(`已处理 ${results[1].length} 条记录并发送至Slack`);
      share_data_kyc_sea(data=results[1]); // 内部通知 - 企业微信
      Logger.log(`已处理 ${results[1].length} 条记录并发送至企业微信`);
    }
  } catch (error) {
    word = `dailyPending-expediteBot-数据源刷新失败: ${error.message}`;
    Logger.log(word);
    var data = {
      'msgtype': 'text',
      'text': {
        'content': word,
        // 'mentioned_mobile_list': ['17317234357']
      }
    }
    var options = {
      'method': 'post',
      'contentType': 'application/json',
      'payload': JSON.stringify(data)
    }
    UrlFetchApp.fetch('https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxxx', options);  // ~yikai selfgroup bot url
  }
}
