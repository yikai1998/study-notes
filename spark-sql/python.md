# python in notebook

## create temp fields as external sources for query use
```py
%python
raw = """
xxx@xxx.com
xxx@xxx.com
...
"""
ids = [line.strip() for line in raw.strip().splitlines()]
df = spark.createDataFrame([(i, 'temp') for i in ids], "user STRING, tag STRING")

# 直接落到永久表或永久视图
df.write.mode("overwrite").option("mergeSchema", "true").saveAsTable("`data-prod-sg`.yikai_test_dbt.tmp_external_table")
# df.createOrReplaceGlobalTempView("tmp_ids_0902")
```

## extract data from databricks table
### method-1
```py
%python
df = spark.sql("select * from `data-prod-sg`.yikai_test_dbt.result_kycsd893")
df = df.toPandas()
print(df)
```
### method-2
```py
# in cell-1
%sql
create or replace temp view my_temp as
select * from `data-prod-sg`.yikai_test_dbt.result_kycsd893;
```
```py
# in cell-2
%python
df = spark.table('my_temp').toPandas()
print(df)
```

## connect with google sheet
```py
# in cell-1
%pip install gspread google-auth
dbutils.library.restartPython()
```
```py
# in cell-2
import gspread
from google.oauth2.service_account import Credentials

service_account_path = "xxx.json"

scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file(service_account_path, scopes=scopes)
gc = gspread.authorize(creds)
sh = gc.open_by_key('xxx').get_worksheet_by_id(xxx)
print(sh.get_all_records())
```
