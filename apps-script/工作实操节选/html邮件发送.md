`<? ... ?>` 执行 JS，不输出内容  
`<?= ... ?>` 输出内容到 HTML


## mail_content_t3060.html
```html
<!DOCTYPE html>
<html>
  <head>
    <style>
        .spaced {
            margin-bottom: 60px; /* Adjust as needed for spacing */
        }
    </style>
  </head>
  <body>
    <p>Hi Commercial Team</p>
    <p>Kindly find the weekly tracking report of the KYC periodical review (PR) long-pending client list as below, and the REQUIRED ACTION is also highlighted for your attention and follow-up.</p>
    <p><b>Here is the full list for your reference: </b><a href = 'https://lookerstudio.google.com/u/0/reporting/f41789bb-a2af-4897-aa15-7982d33437e5/page/i376D'>KYC Periodical Review (PR) & Material Trigger (MT) Long Pending Client List</a></p>

    <!-- Part of T60 clients -->
    <p class='spaced'></p>
    <p style='color:red;'><b>Part 1: Below newly identified client's KYC PR is overdue more than 60 days without a response, all future transactions from the client will be blocked until PR is completed.</b></p>
    <? if (t60_len == 0) { ?> 
      <p><b>No customer should be newly added into watchlist.</b></p>
    <? } else { ?>
      <p><b>REQUIRED ACTION: </b></p>
      <p><b>1) Please help to contact the respective client ASAP and complete the PR review, or</b></p>
      <p><b>2) Inform the KYC team to offboard the client if no future relationship is required</b></p>
      <table border='1' cellspacing='0'>
        <thead>
          <tr bgcolor='lightblue'>
          <? for (var i = 0; i < head_t60.length; i++) { ?>
              <th style='white-space:nowrap'><?= head_t60[i] ?></th>
          <? } ?>
          </tr>
        </thead>
        <tbody>
          <? for (var i = 0; i < data_t60.length; i++) { ?>
            <tr>
              <td><?= data_t60[i].summary ?></td>
              <td><?= data_t60[i].legalEntityId ?></td>
              <td><?= data_t60[i].customerSegment ?></td>
              <td><?= data_t60[i].accountOwner ?></td>
              <td><?= data_t60[i].head ?></td>
              <td><?= data_t60[i].lastRfiTime ?></td>
            </tr>
          <? } ?>
        </tbody>
      </table>
      <p>KYC will add into watchlist accordingly.</p>
      <p>Hi 
        <? for (var i = 0; i < cn_head_t60.length; i++) { ?>
          <a href="mailto:<?= cn_head_t60[i] ?>"><?= cn_head_t60[i] ?></a>, 
        <? } ?>
        KYC will place the control on customers until the review is completed, and the KYC review RFI has been sent; Please help to inform the right teammate if the owner changes.
      </p>
      <p>Hi 
        <? for (var i = 0; i < intl_head_t60.length; i++) { ?>
          <a href="mailto:<?= intl_head_t60[i] ?>"><?= intl_head_t60[i] ?></a>, 
        <? } ?>
        KYC will place the control on customers until the review is completed, you should have been cc-ed in these KYC review RFI emails, and if need further assistance please approach to <a href = 'mailto: someone@airwallex.com'>Joann Qiu</a>
      </p>
    <? } ?>

    <!-- Part of T30 clients -->
    <p class='spaced'></p>
    <p style='color:red;'><b>Part 2: Below client's KYC PR is overdue for more than 30 days without a response, if no response before the Due date (T+60), the client's future transactions will be blocked.</b></p>
    <? if (t30_len == 0) { ?> 
      <p><b>No customer in T+30.</b></p>
    <? } else { ?>
      <p><b>REQUIRED ACTION: </b></p>
      <p><b>1) Please help to contact the respective client ASAP and complete the PR review, or</b></p>
      <p><b>2) Inform the KYC team to offboard the client if no future relationship is required</b></p>
      <table border='1' cellspacing='0'>
        <thead>
          <tr bgcolor='lightblue'>
          <? for (var i = 0; i < head_t30.length; i++) { ?>
              <th style='white-space:nowrap'><?= head_t30[i] ?></th>
          <? } ?>
          </tr>
        </thead>
        <tbody>
          <? for (var i = 0; i < data_t30.length; i++) { ?>
            <tr>
              <td><?= data_t30[i].summary ?></td>
              <td><?= data_t30[i].legalEntityId ?></td>
              <td><?= data_t30[i].customerSegment ?></td>
              <td><?= data_t30[i].accountOwner ?></td>
              <td><?= data_t30[i].head ?></td>
              <td><?= data_t30[i].lastRfiTime ?></td>
              <td><?= data_t30[i].dueDate ?></td>
            </tr>
          <? } ?>
        </tbody>
      </table>
      <p>Hi 
        <? for (var i = 0; i < cn_head_t30.length; i++) { ?>
          <a href="mailto:<?= cn_head_t30[i] ?>"><?= cn_head_t30[i] ?></a>, 
        <? } ?>
        KYC review RFI has been sent; Please help to inform the right teammate if the owner changes.
      </p>
      <p>Hi 
        <? for (var i = 0; i < intl_head_t30.length; i++) { ?>
          <a href="mailto:<?= intl_head_t30[i] ?>"><?= intl_head_t30[i] ?></a>, 
        <? } ?>
        you should have been cc-ed in these KYC review RFI emails, and if need further assistance please approach to <a href = 'mailto: someone@airwallex.com'>Joann Qiu</a>
      </p>
    <? } ?>
    <p>Best regards,<br>KYC Operation Team</p>
  </body>
</html>
```


```js
function dataGroupPR() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('Workpaper-A');
  const lastRow = getLastRow(sheet, 'A:A');
  const rows = sheet.getRange(`A2:Q${lastRow}`).getDisplayValues();

  const groups = {
    t60: [],
    t30: []
  };

  rows.forEach(row => {
    const tag = row[9];

    const item = {
      summary: row[2],
      legalEntityId: row[1],
      customerSegment: row[11],
      orgL2: row[12],
      accountOwner: row[13],
      head: row[16],
      lastRfiTime: row[4].substring(0, 19),
      dueDate: row[7].substring(0, 10)
    };

    if (tag === ' [T+60]') {
      groups.t60.push(item);
    }

    if ([' [T+30]', ' [T+45]'].includes(tag)) {
      groups.t30.push(item);
    }
  });

  return groups;
}
```

-- 专门拿 CN / Intl heads
```js
function splitHeadsByRegion(data) {
  const cn = [];
  const intl = [];

  data.forEach(r => {
    r.orgL2.substring(0, 2) === 'CN'
      ? cn.push(r.head)
      : intl.push(r.head);
  });

  return {
    cn: [...new Set(cn)],
    intl: [...new Set(intl)]
  };
}
```


```js
function send_3060() {
  const datagroup = dataGroupPR();
  const htmlTemplate = HtmlService.createTemplateFromFile('mail_content_t3060.html');

  // part of T60
  const head_t60 = ['Client Name', 'Legal Entity Id', 'Customer Segment', 'Account Owner', 'Commercial Head', 'Last RFI Time'];
  const data_t60 = datagroup.t60;
  const heads_t60 = splitHeadsByRegion(data_t60);

  htmlTemplate.data_t60 = data_t60;
  htmlTemplate.head_t60 = head_t60;
  htmlTemplate.t60_len = data_t60.length;
  htmlTemplate.cn_head_t60 = heads_t60.cn;
  htmlTemplate.intl_head_t60 = heads_t60.intl;

  // part of T30
  const head_t30 = ['Client Name', 'Legal Entity Id', 'Customer Segment', 'Account Owner', 'Commercial Head', 'Last RFI Time', 'Due Date'];
  const data_t30 = datagroup.t30;
  const heads_t30 = splitHeadsByRegion(data_t30);

  htmlTemplate.data_t30 = data_t30;
  htmlTemplate.head_t30 = head_t30;
  htmlTemplate.t30_len = data_t30.length;
  htmlTemplate.cn_head_t30 = heads_t30.cn;
  htmlTemplate.intl_head_t30 = heads_t30.intl;

  const htmlBody = htmlTemplate.evaluate().getContent();
  const mailsetting = getMailSet();
  const mail_subject = 'Weekly Report - KYC Periodical Review (PR) Long Pending Client List' + mailsetting[0];
  const mail_to = mailsetting[1];
  const mail_cc = mailsetting[2];

  if (mail_to.length + mail_cc.length > 100) {
    GmailApp.sendEmail(
      'kyc.ops@airwallex.com',
      'Error Response - ' + mail_subject,
      '收件人超过上限；调整一下，先单独发给自己的邮箱，再手动复制黏贴群发。'
    );
    return;
  }

  GmailApp.sendEmail(
    mail_to.join(','),
    mail_subject,
    'Please view this email in HTML format.',
    {
      htmlBody: htmlBody,
      cc: mail_cc.join(','),
      replyTo: 'someone@airwallex.com'
    }
  );

  Browser.msgBox('🍻Mail is delivered successfully!');
}
```
