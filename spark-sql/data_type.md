参考链接：https://docs.databricks.com/aws/en/sql/language-manual/data-types  

```txt
: 用来“取json路径字段”，:: 是“强制转类型”，?:: 是“安全转类型”（失败就null）
原生/support-variant/raw 字段访问用 冒号
struct/schema/cast出来的 字段访问用 点

结构化数据（struct/array/map）：用 .field 或 ['field']（对 struct 也常可用）
JSON 字符串/variant：用 JSON 函数/JSON path（比如 get_json_object、: 等）
```
```
get_json_object(to_json(sf.data), '$.accountManager')
你的字段 data 是 struct 类型（或 map），直接用 :字段名 取子字段最自然。
get_json_object 实际要操作 string 类型。如果参数不是字符串（而是struct），就会报错。
第一个sf.data:accountManager是Spark为struct/map字段提供的语法糖，推荐优先用
```
```
: 链式适合“在 VARIANT/JSON 里走路径”，返回还是 VARIANT，所以能一直写下去
当列已经是 Spark 的强类型（struct/array/map）时，用 .
element_at(from_json(get_json_object(to_json(kc.data), '$.decisions'), 'array<boolean>'), -1).final
```


- ARRAY
  ```sql
  SELECT A.Vaaa[1] FROM VALUES
  (ARRAY(3, 4)),
  (ARRAY(13, 14)),
  (ARRAY(23, 24)) AS A(Vaaa);

  -- 4, 14, 24, each array get the [1]
  ```

- DATE
  ```sql
  select date('2024-12-02 15:00') as create_date;
  ```
  
- DECIMAL
- DOUBLE
- FLOAT
- INT
- INTERVAL
- BIGINT
- BINARY
- BOOLEAN
- VOID
- OBJECT
- SMALLINT
- STRING
- STRUCT
- TIMESTAMP_NTZ
- TINYINT
  
- MAP
  ```sql
  SELECT map('red', 1, 'green', 2);
  
  SELECT m['say'] FROM VALUES(map('say', 'Hello', 'reply', 'World')) AS T(m);
  ```

- TIMESTAMP  
  Timestamps with local timezone are internally normalized and persisted in UTC. Whenever the value or a portion of it is extracted the local session timezone is applied.
  ```sql
  select timestamp('2021-7-1T8:43:28UTC+3')
  -- 2021-07-01T05:43:28.000+00:00
  ```


- VARIANT  
  Represents semi-structured data.
  

```txt
1. array
就是“数组”，像 [1,2,3]，也可以是 ["a", "b", "c"]
每项类型一般相同
SQL类型: ARRAY<STRING>, ARRAY<INT>, ARRAY<STRUCT<...>>...
2. struct
就是“结构体/对象/一行数据”，像{"a":1,"b":"x"} 或 Python 里的 dict 或“数据库表里的单行”
包含一组有名字的字段
SQL类型: STRUCT<a INT, b STRING>
3. map
就是“字典”，一堆key-value键值对，比如{"a":10, "b":20}
和struct区别：map的key一般可以是任意值（字符串、数字，不需要提前写死），struct的key字段是表结构里提前定义好的
SQL类型: MAP<STRING, INT>
4. variant（或有的库叫“any”/“json”）
最包容的类型，啥都能装进来！
你往里面塞个[1,2]变成array，塞个{a:1}变成struct/map，塞个"abc"是字符串，甚至可以嵌套。
真实含义就是“我不知道到底是啥，但保证能装下json任何结构的数据类型”。
```
