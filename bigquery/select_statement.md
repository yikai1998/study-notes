```SELECT DISTINCT``` cannot return columns of the following types: ```STRUCT``` ```ARRAY```

struct() is to make all fields with in the parenthesis into one json

array is to make the whole select result into one row

---
```SELECT AS STRUCT```
This produces a value table with a STRUCT row type, where the STRUCT field names and types match the column names and types produced in the SELECT list.
select as struct is to make all columns behind the select into one json

---
sample <br>
```SELECT AS STRUCT 1 a, 2 b``` <br>
![image](https://github.com/user-attachments/assets/24621af8-ef8d-4b63-ba3b-57179e7949a3)

```SELECT ARRAY(SELECT AS STRUCT 1 a, 2 b) AS a_array``` <br>
![image](https://github.com/user-attachments/assets/4e7a8b31-edee-415d-af43-397730de904d)


![image](https://github.com/user-attachments/assets/794464fc-cc1a-4c0f-8892-ed11e18c7420)

---

```SELECT * REPLACE```  
Note: SELECT * REPLACE doesn't replace columns that don't have names.  
```
WITH orders AS
  (SELECT 5 as order_id,
  "sprocket" as item_name,
  200 as quantity)
SELECT * REPLACE ("widget" AS item_name)
FROM orders;

/*----------+-----------+----------*
 | order_id | item_name | quantity |
 +----------+-----------+----------+
 | 5        | widget    | 200      |
 *----------+-----------+----------*/

WITH orders AS
  (SELECT 5 as order_id,
  "sprocket" as item_name,
  200 as quantity)
SELECT * REPLACE (quantity/2 AS quantity)
FROM orders;

/*----------+-----------+----------*
 | order_id | item_name | quantity |
 +----------+-----------+----------+
 | 5        | sprocket  | 100      |
 *----------+-----------+----------*/
```

---

SELECT AS VALUE 是 BigQuery 在处理“GROUP BY + ARRAY_AGG(... LIMIT 1)”时的一种简化形式，用来直接返回 struct 本身，而不是再包一层字段名。更完整的例子是：
```
CREATE TEMP TABLE basic_per_cle AS (
  SELECT AS VALUE
    ARRAY_AGG(basic ORDER BY basic.account_id LIMIT 1)[OFFSET(0)]
  FROM `...account_basic_info` AS basic
  WHERE basic.account_status = 'ACTIVE'
    AND basic.type = 'BUSINESS'
  GROUP BY basic.client_legal_entity_id
);
```
等价于
```
CREATE TEMP TABLE basic_per_cle AS (
  SELECT
    ARRAY_AGG(basic ORDER BY basic.account_id LIMIT 1)[OFFSET(0)] AS basic_row
  FROM `...account_basic_info` AS basic
  WHERE basic.account_status = 'ACTIVE'
    AND basic.type = 'BUSINESS'
  GROUP BY basic.client_legal_entity_id
);
```
区别是：  
不用给这个 struct 起名 basic_row  
后面直接当成一行来用（SELECT * FROM basic_per_cle 就是所有列）  
所以它适合这种模式：  
  
有一个表 T，里面一堆列  
你想按 key group，每组只保留一行（比如“第一个”或“最新的”）  
保留那一行的所有列  
而不想手动列出所有列名。  
在你这份大 SQL 里，凡是“per CLE 压成一行”的场景，都可以考虑这种写法，它既省代码，又让最终结果天然是“一行一个 CLE”，避免最后不得不用 DISTINCT/STRING_AGG(DISTINCT ...) 去救场。  
