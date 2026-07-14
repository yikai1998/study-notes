MySQL 不是 BigQuery 那种原生 ARRAY/STRUCT 思维
要用其他方式替代UNNEST场景

JSON_EXTRACT函数用于提取JSON类型数据中指定json_path的数据
JSON_UNQUOTE函数用于去掉JSON数据中的引号
```sql
SELECT JSON_EXTRACT('{"user": {"name": "Jane", "age": 25}}', '$.user.age');
SELECT JSON_UNQUOTE(JSON_EXTRACT(json '{"name": "John", "age": 25, "city": "New York"}','$.city'));  -- 返回New York
```

JSON_TABLE 展开数组
```sql
mysql> SELECT *
    -> FROM
    ->   JSON_TABLE(
    ->     '[ {"a": 1, "b": [11,111]}, {"a": 2, "b": [22,222]}, {"a":3}]',
    ->     '$[*]' COLUMNS(
    ->             a INT PATH '$.a',
    ->             NESTED PATH '$.b[*]' COLUMNS (b INT PATH '$')
    ->            )
    ->    ) AS jt
    -> WHERE b IS NOT NULL;

+------+------+
| a    | b    |
+------+------+
|    1 |   11 |
|    1 |  111 |
|    2 |   22 |
|    2 |  222 |
+------+------+
```

从分析思维上，JSON_TABLE确实有点像 BigQuery 的 UNNEST() / Spark 的 explode()。MySQL 官方文档说明 JSON_TABLE() 可以把 JSON document 里的数据提取出来，并以关系表形式返回。
```sql
SELECT
  o.order_id,
  jt.sku
FROM orders o
LEFT JOIN JSON_TABLE(
  o.items_json,
  '$[*]' COLUMNS (
    sku VARCHAR(50) PATH '$.sku'
  )
) AS jt
ON TRUE;
```
