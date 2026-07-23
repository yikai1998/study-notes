MySQL 不是 BigQuery 那种原生 ARRAY/STRUCT 思维
要用其他方式替代UNNEST场景

JSON_EXTRACT函数用于提取JSON类型数据中指定json_path的数据
JSON_UNQUOTE函数用于去掉JSON数据中的引号
```sql
SELECT JSON_EXTRACT('{"user": {"name": "Jane", "age": 25}}', '$.user.age');
SELECT JSON_UNQUOTE(JSON_EXTRACT('{"name": "John", "age": 25, "city": "New York"}','$.city'));  -- 返回New York


-- JSON_EXTRACT 的简写
SELECT data->'$.city' FROM users;

-- JSON_UNQUOTE(JSON_EXTRACT(...)) 的简写
SELECT data->>'$.city' FROM users;
-- 返回的是不带引号的字符串 ← 更常用
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

```sql
SELECT
  a.*,
  jt.sku,
  jt.qty,
  jt.price
FROM (
  SELECT
    1 AS order_id,
    101 AS customer_id,
    JSON_ARRAY(
      JSON_OBJECT('sku', 'A001', 'qty', 2, 'price', 10.50),
      JSON_OBJECT('sku', 'B002', 'qty', 1, 'price', 20.00)
    ) AS items_json

  UNION ALL

  SELECT
    2 AS order_id,
    102 AS customer_id,
    JSON_ARRAY(
      JSON_OBJECT('sku', 'C003', 'qty', 3, 'price', 5.25)
    ) AS items_json

  UNION ALL

  SELECT
    3 AS order_id,
    103 AS customer_id,
    JSON_ARRAY() AS items_json

  UNION ALL

  SELECT
    4 AS order_id,
    104 AS customer_id,
    NULL AS items_json
) AS a
LEFT JOIN JSON_TABLE(
  a.items_json,
  '$[*]' COLUMNS (
    sku VARCHAR(50) PATH '$.sku',
    qty INT PATH '$.qty',
    price DECIMAL(10,2) PATH '$.price'
  )
) AS jt
ON TRUE
ORDER BY
  a.order_id,
  jt.sku;

+----------+-------------+----------------------------------------------------------------------------------------+------+------+-------+
| order_id | customer_id | items_json                                                                             | sku  | qty  | price |
+----------+-------------+----------------------------------------------------------------------------------------+------+------+-------+
|        1 |         101 | [{"qty": 2, "sku": "A001", "price": 10.50}, {"qty": 1, "sku": "B002", "price": 20.00}] | A001 |    2 | 10.50 |
|        1 |         101 | [{"qty": 2, "sku": "A001", "price": 10.50}, {"qty": 1, "sku": "B002", "price": 20.00}] | B002 |    1 | 20.00 |
|        2 |         102 | [{"qty": 3, "sku": "C003", "price": 5.25}]                                             | C003 |    3 |  5.25 |
|        3 |         103 | []                                                                                     | NULL | NULL |  NULL |
|        4 |         104 | NULL                                                                                   | NULL | NULL |  NULL |
+----------+-------------+----------------------------------------------------------------------------------------+------+------+-------+
```

性能注意事项
```txt
-- JSON_TABLE 在大表上很慢！
-- 因为 MySQL 没办法对 JSON 内部字段建索引

-- 如果频繁查询，考虑：
-- ① 生成列 + 索引
ALTER TABLE orders
  ADD COLUMN first_sku VARCHAR(50)
  GENERATED ALWAYS AS (JSON_UNQUOTE(items_json->>'$[0].sku')) STORED,
  ADD INDEX idx_first_sku (first_sku);

-- ② 或者直接把 JSON 拆成正规化的表
```
