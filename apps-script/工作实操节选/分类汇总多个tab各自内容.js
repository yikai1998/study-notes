const wb = SpreadsheetApp.openById('xxx--xx');

const ss1 = wb.getSheetById(1083627185);  // #1 - CLE in non-responsive WL 
const ss2 = wb.getSheetById(1029548490);  // #2 - 115 in review cases
const ss3 = wb.getSheetById(268802701);   // #3 - Dormancy in review cases

let ssc1 = ss1.getRange('A3:Z').getDisplayValues();
let ssc2 = ss2.getRange('A3:Z').getDisplayValues();
let ssc3 = ss3.getRange('A3:Z').getDisplayValues();

const ss1_headers = ssc1[0];
const ss2_headers = ssc2[0];
const ss3_headers = ssc3[0];

ssc1 = ssc1.slice(1);
ssc2 = ssc2.slice(1);
ssc3 = ssc3.slice(1);

var ssc1_class = {ANZ: [], EMEA: [], NA: [], GC: [], 'HK&SEA': []};
var ssc2_class = {ANZ: [], EMEA: [], NA: [], GC: [], 'HK&SEA': []};
var ssc3_class = {ANZ: [], EMEA: [], NA: [], GC: [], 'HK&SEA': []};

const combo = [
  {cls: ssc1_class, data: ssc1, headers: ss1_headers},
  {cls: ssc2_class, data: ssc2, headers: ss2_headers},
  {cls: ssc3_class, data: ssc3, headers: ss3_headers}
];

for (let {cls, data, headers} of combo) {
  const entity_idx = headers.indexOf('owningEntity');

  for (let i = 0; i < data.length; i++) {
    const entity = data[i][entity_idx];

    if (['AIRWALLEX_AU', 'AIRWALLEX_NZ'].includes(entity)) {
      cls.ANZ.push(data[i]);
    } else if (['AIRWALLEX_UK', 'AIRWALLEX_NL', 'AIRWALLEX_LT'].includes(entity)) {
      cls.EMEA.push(data[i]);
    } else if (['AIRWALLEX_US', 'AIRWALLEX_CA'].includes(entity)) {
      cls.NA.push(data[i]);
    } else if (['AIRWALLEX_HK', 'AIRWALLEX_SG', 'AIRWALLEX_MY'].includes(entity)) {
      cls.GC.push(data[i]);
      // 如果你想归到 HK&SEA，就改成：
      // cls['HK&SEA'].push(data[i]);
    }
  }
}

let ogs_backlog_summary = {
  SCENARIO_ONE: ssc1_class,
  SCENARIO_TWO: ssc2_class,
  SCENARIO_THREE: ssc3_class
};
