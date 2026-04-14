import pandas as pd
import gspread
from tqdm import tqdm
import datetime

# 便于展示df
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 1000)

# pandas cowork with tqdm
tqdm.pandas(desc='extracting basic info from ng')
df_old['LegalEntityId'] = df_old['AccountId'].progress_apply(lambda x: get_LegalEntityId(accountid=x), axis=1)
# 优化 (直接作用于 Series，不需要 axis=1) 如果你是对 AccountId 这一列单独操作，其实不需要写 axis；但如果你是对整个 df 做 apply 且需要用到同一行里的多个字段，就必须写 axis=1。Axis 0 = Index (行)：你可以想象成垂直向下的重力。Axis 1 = Columns (列)：你可以想象成水平向右的推力。
# df_old['LegalEntityId'] = df_old['AccountId'].progress_apply(get_LegalEntityId)

# 从googlesheet上获取信息
sa = gspread.service_account('./xxx.json')
sh1 = sa.open('name of your googlesheet')
sh_workpaper = sh1.worksheet('Workpaper-A')
head_table = pd.DataFrame(sh_ref.get('F2:G'), columns=['OrgL2', 'Head'])  # list of bd head mapping

# 加工处理原数据
df_old = sh_workpaper.get_all_values()
df_old = pd.DataFrame(data=df_old[1:], columns=df_old[0])
NULL_FLAG = '__NULL__'          # 1. 先定好“空值标记”
df = (df
      .drop_duplicates()
      .replace({'': None, np.nan: None})   # 2. 先统一成 None
      .astype(str)
      .where(pd.notnull(df), NULL_FLAG))   # 3. None → 自定义标记 [满足条件就保留原值，不满足就用另一个值替换] This method allows conditional replacement of values. Where the condition evaluates to True, the original values are retained; where it evaluates to False, values are replaced with corresponding entries from other

# 更新数据至googlesheet
sh_to.clear()
sh_to.update([df.columns.values.tolist()] + df.values.tolist())
# gspread 的 update 面对大数据量（比如超过 1 万行）可能会触发 API 配额限制或超时。

# join to get the head info
com_df = pd.merge(com_df, head_table, on='OrgL2', how='left')

# put some function on specific column
new_jira_df['Note'] = new_jira_df['LegalEntityId'].apply(lambda x: '' if len(x) == 36 else ' [InvalidLegalEntityId]')

# 文本转成时间，utc
old_jira_df['RfiTime'] = pd.to_datetime(old_jira_df['RfiTime'], format='%Y-%m-%dT%H:%M:%S.%f%z', utc=True)

# 时间转文本
old_jira_df['RfiTime'] = old_jira_df['RfiTime'].dt.strftime('%Y-%m-%dT%H:%M:%S.%f%z')

# 在已知时间的基础上做时间计算
old_jira_df['DeadLine'] = old_jira_df['RfiTime'].apply(lambda x: x+datetime.timedelta(hours=24*60))

# 获取当前时间，基于既定时间字段的时区
current_time = datetime.datetime.now(old_jira_df['RfiTime'].dt.tz)

# 两个时间计算做差
old_jira_df['PendingHours'] = ((current_time - old_jira_df['RfiTime']).dt.total_seconds()/3600).round(1)

# 聚合1 返回与原表行数一样的结果。在每一行旁边增加一个“组内统计值”。
raw_content['sum_usd_amount_acctId'] = raw_content.groupby('AccountId')['delta amount usd'].transform('sum')

# 聚合2 返回缩减后的结果。真正的归纳总结，生成报表/汇总统计。
adj_content = (adj_content
                   .groupby(['AccountId', 'currency', 'Wallet Action', 'AccountName', 'AccountOwnerEmail', 'Batch'])
                   .agg({'amount': 'sum', 'transaction_id': lambda x: '\n'.join(set(x)), 'Issuing team comment - From Puzzle': lambda x: '\n'.join(set(x))})
                   .reset_index())

# 拼接 新增数据
# 法1 新增数据的标准做法 列顺序不一样：自动对齐  列名不一致（缺失或多余）：取并集
key_mapping = {
    'LegalEntityId': 'legalentityid',
    'AccountId': 'accountid',
    'GlobalAccountId': 'gaid',
    'DataRegion': 'dc',
    'ReasonCode': 'reason',
    'AdditionalComment': 'detail',
}
df_new = df_new.rename(columns=key_mapping) # 改列名
df_new[['operatorname', 'operatormail']] = operator_name, operator_mail # 填常数
df_combine = pd.concat([df_old, df_new], ignore_index=True) # 拼接

# 法2 利用了向量化操作，比循环快几个数量级。当你需要根据某个条件（比如 AccountId）去改特定的列时，这是唯一正确的姿势。
for field, value in fields_to_update.items():
    value = 'NaN' if value is None or (isinstance(value, list) and len(value) == 0) else value
    self.df.loc[self.df.AccountId == accountid, field] = value

# 用@方法来筛选数据 只要过滤条件超过 2 个，或者需要引用外部变量，无脑选
account_ids = ['9557ba1e-1128-40a8-b860-a9bae093eea8', 'ef34c6eb-3f33-4ed1-8a65-1b0b2aefb59f']
df = df.query("account_id.isin(@account_ids) and category in ('Risk concern')")

# Function to flatten list values in DataFrame cells
def flatten_cells(cell):
    if isinstance(cell, list):
        return ', '.join(map(str, cell))  # Convert the list to a comma-separated string
    return cell
final_df = final_df.map(flatten_cells)

# 希望Account Id等动态内容直接显示在validation check进度条（tqdm）的一行描述里，不要每条都print成新行，就像desc='validation check [Account Id xxx]'这种“随进度条实时刷新”
with tqdm(df_work.values.tolist()) as bar:
    for row in bar:
        bar.set_description(f'validation check | Account Id: {row[0]}')  # “刷新和初始化行为”是tqdm进度条第一次输出的正常现象，不是 bug，也不是重复多行。随后进度只在同一行刷新，不会再多新的一行。
        ecOnboard.validation_check(accountid=row[0])
        time.sleep(0.2)
