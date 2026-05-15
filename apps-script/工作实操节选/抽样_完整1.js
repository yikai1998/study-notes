function sampleCases() {
  // 基本参数
  var dateinfo = new Date();
  dateinfo.setMonth(dateinfo.getMonth() - 1);  // set the month to the previous 
  dateinfo.setDate(1);  // set the date to the first day of the month
  var monthbatch = Utilities.formatDate(dateinfo, 'GMT+8', 'YYYY-MM-dd');
  var accum = 0;
  
  // 获取数据
  const sheet_pool = SpreadsheetApp.getActiveSpreadsheet().getSheetById(1356321158);
  const sheet_ea = SpreadsheetApp.getActiveSpreadsheet().getSheetById(0);
  const sheet_au = SpreadsheetApp.getActiveSpreadsheet().getSheetById(989690082);
  const sheet_eu = SpreadsheetApp.getActiveSpreadsheet().getSheetById(1724512175);
  const sheet_us = SpreadsheetApp.getActiveSpreadsheet().getSheetById(1923723751);
  const data = sheet_pool.getDataRange().getValues();
  const headers = data[0];
  const rows = data.slice(1); // 移除标题行, 正文数据
  
  // 定义常用列索引
  const pos_region = headers.indexOf('region');
  const pos_entity = headers.indexOf('owning_entity');
  const pos_group = headers.indexOf('ref_rule_group');
  
  // 统计数据
  const regionCounts = {};
  const entityCountsByRegion = {};
  const groupCountsByEntity = {};
  
  // 初始分类统计，知晓各个region entity group的数量分布
  rows.forEach((row, index) => {
    const region = row[pos_region];
    const entity = row[pos_entity];
    const group = row[pos_group];
    // 数region
    regionCounts[region] = (regionCounts[region] || 0) + 1;
    // 数entity
    if (!entityCountsByRegion[region]) {
      entityCountsByRegion[region] = {};
    }
    entityCountsByRegion[region][entity] = (entityCountsByRegion[region][entity] || 0) + 1;
    // 数group
    const entityKey = `${region}|${entity}`;
    if (!groupCountsByEntity[entityKey]) {
      groupCountsByEntity[entityKey] = {};
    }
    groupCountsByEntity[entityKey][group] = (groupCountsByEntity[entityKey][group] || 0) + 1;
  });
  
  // 计算分配数量并抽样
  const sampledRows = [];
  const sampledIndices = new Set(); // 用于记录已抽样的行索引, 比{}性能更优 更清晰
  // 第一层 - region
  for (const region in regionCounts) {
    // 根据region的案例数量动态确定抽样数量
    const regionCaseCount = regionCounts[region];
    const regionSampleTarget = determineRegionSampleSize(regionCaseCount);
    Logger.log(`处理region: ${region}, 总数: ${regionCaseCount}, 抽样: ${regionSampleTarget}`);
    // 第二层 - owning entity
    const entitiesInRegion = entityCountsByRegion[region];
    const samplesForRegion = [];
    // 计算每个entity应抽取的样本数
    for (const entity in entitiesInRegion) {
      const entityCount = entitiesInRegion[entity];
      const entityRatio = entityCount / regionCounts[region];
      let entitySamples = Math.round(regionSampleTarget * entityRatio);
      // 确保至少抽取1个样本，如果比例大于0
      if (entityRatio > 0 && entitySamples == 0) {
        entitySamples = 1;
      }
      Logger.log(`Entity: ${entity}, 数量: ${entityCount}, 比例: ${entityRatio}, 分配样本数: ${entitySamples}`);
      // 该entity中的所有group
      const entityKey = `${region}|${entity}`;
      const groupsInEntity = groupCountsByEntity[entityKey] || {};
      const groupSamples = {};
      // let totalGroupSamples = 0;
      // 第三层 - group of rule name
      for (const group in groupsInEntity) {
        const groupCount = groupsInEntity[group];
        const groupRatio = groupCount / entityCount;
        let groupSampleCount = Math.round(entitySamples * groupRatio);
        // 确保至少抽取1个样本，如果比例大于0
        if (groupRatio > 0 && groupSampleCount == 0) {
          groupSampleCount = 1;
        }
        groupSamples[group] = groupSampleCount;
        // totalGroupSamples += groupSampleCount;
        Logger.log(`Group: ${group}, 数量: ${groupCount}, 比例: ${groupRatio}, 分配样本数: ${groupSampleCount}`);
      }
      
      /** 先不考虑
      // 如果group样本数和entity样本数不一致
      if (totalGroupSamples != entitySamples) {
        Logger.log(`需要调整样本数: ${totalGroupSamples} -> ${entitySamples}`);
        // 简单调整策略：从最大的group中增减
        const groupsSorted = Object.keys(groupSamples).sort((a, b) => groupSamples[b] - groupSamples[a]);
        const diff = entitySamples - totalGroupSamples;
        groupSamples[groupsSorted[0]] += diff;
      }
      */
      
      // 从每个group中抽取样本
      for (const group in groupSamples) {
        const sampleCount = groupSamples[group];
        if (sampleCount <= 0) continue;
        // 找出所有符合条件的行
        const candidateRows = rows.map((rowInfo, idxTag) => 
          ({rowInfo: rowInfo, idxTag: idxTag})  // 小括号不能省略，否则会被解析为带有标签(label)的代码块，而不是返回对象，导致语法错误
        ).filter(item => 
          item.rowInfo[pos_region] == region && 
          item.rowInfo[pos_entity] == entity && 
          item.rowInfo[pos_group] == group &&
          !sampledIndices.has(item.idxTag)
        );
        // 随机抽取指定数量的行
        const selected = sampleRandomRows(candidateRows, sampleCount);
        var addrowdatas = [];
        // 添加到结果并记录已抽样的行索引
        selected.forEach(item => {
          samplesForRegion.push(item.rowInfo);
          sampledIndices.add(item.idxTag);
          var accum_code = Utilities.formatString('%4s',String(accum));
          for (var j=1; j<100; j++) {
            accum_code = accum_code.replace(' ','0')
            if (!accum_code.includes(' ')) {
              break;
            }
          }
          var team = item.rowInfo[10];
          var rfitag = (item.rowInfo[11] == 'TRUE' ? 'Y' : 'N');
          var qaid =  'RT' + Utilities.formatDate(dateinfo, 'GMT+8', 'YYMM') + accum_code + rfitag + team;  // QA样本编号 'RT'+年后两位+月两位+四位累增编码+RFI标记+teamtag
          var type = 'Real-Time';
          var caseid = item.rowInfo[0];
          var entity = item.rowInfo[7];
          var l1owner = item.rowInfo[2];
          var l2owner = item.rowInfo[3];
          var l3owner = item.rowInfo[4];
          var rulename = item.rowInfo[5];
          var addrowdata = [monthbatch, qaid, entity, type, caseid, l1owner, l2owner, l3owner, rulename];
          addrowdatas.push(addrowdata);
          accum++;
        });
        Logger.log(`从Group[${group}]抽取了${selected.length}个样本`);
        Logger.log(addrowdatas);
        //判断region 决定去哪张sheet贴
        if(region == 'ANZ') {
          var to_sheet = sheet_au;
        } 
        else if(region == 'EMEA') {
          
          var to_sheet = sheet_eu;
        }
        else if(region == 'HK&SG&MY') {
          
          var to_sheet = sheet_ea;
        }
        else if(region == 'US') {
          
          var to_sheet = sheet_us;
        }
        to_sheet.getRange(getLastRow(to_sheet,'A:A')+1, 1, addrowdatas.length, addrowdatas[0].length).setValues(addrowdatas);
      }
    }
    sampledRows.push(...samplesForRegion);
    Logger.log(`Region[${region}]总共抽取了${samplesForRegion.length}个样本`);
  }
  
  return sampledRows;
}
