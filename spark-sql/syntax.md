```
UDF
如果仅用 SQL 语法注册，那 UDF 逻辑只能在 Java/Scala 里实现（打成 jar 包，注册到 Spark SQL）
不能用 SQL 写函数体，也不能用 SQL 动态写 Python 函数体
如果你用 Python 写 UDF，只能在 PySpark（Python 程序/Notebook）环境下通过 API 注册，然后在本 session 的 SQL 里用，不能在 SQL Warehouse/SQL 编辑器直接注册，更不能"persist"成全局永久函数。
Databricks、Spark 官方都不支持通过 SQL 写 "Python/Scala/Java" 逻辑函数体；SQL UDF 只能用简单 SQL 语句做些组合。
```


```
建临时视图、写 select 语句，这些 standard SQL 都能用

建持久表（CREATE TABLE）——支持，并写到 catalog/warehouse 里。
建临时视图（CREATE TEMP VIEW）——完全支持，强烈推荐。
CREATE TEMP TABLE —— 语法不推荐／少数 Spark 版本才勉强兼容；优先用 VIEW 替代。
```

```
CREATE OR REPLACE TEMP VIEW t1 AS
SELECT explode(array(struct(10, 20), struct(null, 55))) AS col;

as后的query，不用加分号，也不要最外层括号
CREATE VIEW/CREATE TABLE/CREATE TEMP VIEW 只做定义，没展示结果。
只有 SELECT（或 SHOW TABLES）等查询动作，才会返回内容！


create view 和 create table虽然看起来都能生成表，但是有区别：
表（table）是真实持久存储数据的“实体”，数据物理存在，只有你drop table才消失，其他对象（如视图或其它sql）通常依赖它都不会失效（除非你真把表删了）。
视图（view）是虚拟的“查询结果”，本身不真正存数据，而是保存了一段SQL逻辑。

如果你有一串链式的view，比如：
%sql
CREATE VIEW v1 AS SELECT ... FROM t_base;
CREATE VIEW v2 AS SELECT ... FROM v1;
CREATE VIEW v3 AS SELECT ... FROM v2;
这时如果删除了v1（执行DROP VIEW v1），
v2、v3都会立刻失效/报错（因为v2定义里用到了v1，v3里用到了v2）。
只要中间的基础view被删，依赖它的view全部不能用了。

实际效果是：
你再查 SELECT * FROM v2 或 v3，都会报“找不到依赖对象v1/v2”等类似错误。
这种依赖链在所有主流数据库/引擎/大数据平台中都是如此的！
```



```py
# 查看表结构
spark.sql("DESCRIBE TABLE my_table").show()
```

```py
把「直接粘来的 id 列表」先变成一个 Python 列表，再用 Notebook 的 参数注入 或 临时视图 两种方式，让后面的 SQL cell 直接当列来用
# 把列表变成 DataFrame
raw = """
id1
id2
id3
id4
"""
ids = [line.strip() for line in raw.strip().splitlines()]
df = spark.createDataFrame([(i, 'hello') for i in ids], "id STRING, temp_str STRING")

# 直接落到永久表或永久视图
df.write.mode("overwrite").option("mergeSchema", "true").saveAsTable("`data-prod-sg`.yikai_test_dbt.tmp_ids")
# 想彻底重建表结构（字段完全保持与 DataFrame 一致）：先Drop，再SaveAsTable 【`spark.sql("DROP TABLE IF EXISTS `data-prod-sg`.yikai_test_dbt.tmp_ids")`】，或用overwriteSchema（若支持）
# 或者：df.createOrReplaceGlobalTempView("tmp_ids") 也可以，但不如落到表简单[serverless 环境下不能用 createOrReplaceGlobalTempView，只能用本地 temp view 或持久表。]
```

```
DECLARE VARIABLE row_limit = 10;
```
