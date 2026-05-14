## 动态mention
```js
// mock user mapping based on owning-entity and txn-type
var userMapping = {
  'AU': {
    'FEE': ["U059ZSxxx"],
    'ADJUSTMENT': ["U059ZSxxxx", "UA43xxx", "UC0xxx3"],
    ...,
    'PAYOUT': ["UxxxDMEK", "UCxxx23"]
  },
  ...,
};

function slackapp_template_10k(account_id, legal_entity_id, client_name, owning_entity, org_l2, account_owner, last_nb_date, net_account_balance_usd, txn_mapping_id, nb_txn_type, nb_txn_sub_typ, nb_txn_domain, nb_txn_reason, url) {
  var country_code = String(org_l2).substring(0, 2)
  var knownRegions = ['AU', 'CN', 'HK', 'SG', 'UK', 'US']
  var region = knownRegions.includes(country_code) ? country_code : 'Others'
  var userIds = ["UC0xxx823", "UR0SxxxE9F"]  // defaults to xxx if no mapping is found
  
  if (userMapping[region] && userMapping[region][nb_txn_type]) {
    userIds = userMapping[region][nb_txn_type];  // fetch user ids
  }

  // construct dynamic user mention elements, with delimiters
  var userMentionElements = [];
  userIds.forEach((userId, index) => {
    userMentionElements.push({
      "type": "user",
      "user_id": userId
    });
    // add a space after every user mention, except the last one
    if (index < userIds.length - 1) {
      userMentionElements.push({
        "type": "text",
        "text": " "
      });
    }
  });

  // block kit
  var param = {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify({
      'text': 'This is the fallback text for clients that do not support blocks',
      'blocks': [
			  ...
              {
                "type": "link",
                "url": "https://lookerstudio.google.com/u/0/reporting/xxx",
                "text": "Go to dashboard"
              },
              {
                "type": "text",
                "text": "\n\nHi "
              },
              ...userMentionElements,  // spread the user mentions into the elements array
              {
                "type": "text",
                "text": ", the Net Account Balance of this client has fallen below $-10K, please take the necessary follow-up actions. "
              },
              ...
            ]
				  }
        ]
        }
      ]
    })
  }

  UrlFetchApp.fetch(url, param)
  Utilities.sleep(1000)
}
```


## 动态生成重复格式
```js
var rfiListElements = [];
if (s4[region]) {
s4[region].forEach(r => {
    rfiListElements.push(
      {"type": "text", "text": r[1], "style": {"code": true}},
      {"type": "text", "text": " received "},
      {"type": "text", "text": r[3], "style": {"code": true}},
      {"type": "text", "text": " time(s) of RFI \n"}
    )
  });
}
```


## 项目符号列表，且保证空格对齐
```js
var element_list = [];

content.forEach(row => {
  var hours = String(row[16]);
  var spaces = ' '.repeat(Math.max(8 - hours.length, 2));

  element_list.push({
    type: 'rich_text_section',
    elements: [
      {
        type: 'text',
        text: `${hours} hrs`,
        style: {
          code: true
        }
      },
      {
        type: 'text',
        text: spaces
      },
      {
        type: 'text',
        text: ` CLE Id: ${row[1]} `
      }
    ]
  });
});
...
{
  type: 'rich_text_list',
  style: 'bullet',
  indent: 0,
  border: 0,
  elements: element_list
}
```


## 删掉特定block
```js
let arr = block.blocks[0].elements;
var property_name = `${region}_DAILY_QUOTA`;
if (PropertiesService.getUserProperties().getProperty(property_name) == 1) {
  [8, 7, 6, 5].forEach(idx => arr.splice(idx, 1));  // 删 part4 和 part3 (倒序删 是对的。因为如果从小到大删，数组 index 会移动，容易删错。)
}
```


## 自动修正多个 ordered list 的编号连续性
```js
let offsetCount = 0;

for (let e of block.blocks[0].elements) {
  if (e.type == "rich_text_list" && e.style == "ordered") {
    e.offset = offsetCount;
    offsetCount += e.elements.length;
  }
}
```


## 生成table
```js
function array_to_table(columns, data) {
  // Convert headers + 2D row array into Slack block-kit rich_text table
  var rows = [];
  var header_row = [];

  for (let col of columns) {
    header_row.push({
      'type': 'rich_text',
      'elements': [{
        'type': 'rich_text_section',
        'elements': [{
          'type': 'text',
          'text': String(col),
          'style': {'bold': true}
        }]
      }]
    })
  }
  rows.push(header_row);

  for (let row of data) {
    var data_row = []

    for (let cell of row) {
      data_row.push({
        'type': 'rich_text',
        'elements': [{
          'type': 'rich_text_section',
          'elements': [{
            'type': 'text',
            'text': value !== '' && value != null ? String(value) : 'null'
          }]
        }]
      })
    }

    rows.push(data_row);
  }

  var block = {
    'type': 'table',
    'rows': rows
  }

  return block;
}
... 特别注意 此处的text里的内容不能为空，否则一定会报错
const payload = {
  'blocks': [
    intro_block, {'type': 'divider'}, table_block
  ]
}
```
