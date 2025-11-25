参考链接：https://spark.apache.org/docs/latest/sql-ref-functions-builtin.html  

# 主要是一些基本常见的函数整理  

---
## aggregate related
- array_agg  // Collects and returns a list of non-unique elements.
- listagg
- string_agg
```sql
select 
emo, 
listagg(distinct grade, '*'),
string_agg(distinct grade, '*')
from values ('a', 'happy'), ('b', 'sad'), ('c', 'happy') as tab(grade, emo) 
group by all;
```

--- 

## array related
- array_append(array, element)  // Add the element at the end of the array. Type of element should be similar to type of the elements of the array.
- array_prepend
- array_compact(array)  // Removes null values from the array.
- array_contains(array, value)  // Returns true if the array contains the value.
- array_distinct(array)  // Removes duplicate values from the array.
- array_except(array1, array2)  // Returns an array of the elements in array1 but not in array2, without duplicates.
- array_insert(x, pos, val)  // Places val into index pos of array x. Array indices start at 1. The maximum negative index is -1 for which the function inserts new element after the current last element.
- array_intersect(array1, array2)  // Returns an array of the elements in the intersection of array1 and array2, without duplicates.
- arrays_overlap  // Returns true if a1 contains at least a non-null element present also in a2. If the arrays have no common element and they are both non-empty and either of them contains a null element null is returned, false otherwise.
- array_join(array, delimiter[, nullReplacement])	 // Concatenates the elements of the given array using the delimiter and an optional string to replace nulls. If no value is set for nullReplacement, any null value is filtered.
```sql
SELECT array_join(array('hello', null ,'world'), '!!', '[replace]');
```
- array_min, array_max, array_postion (1-based, 0 if not found)
- array_remove  // Remove all elements that equal to element from array.
- array_repeat  // Returns the array containing element count times.
```sql
SELECT array_repeat('123', 2);
```
- array_union  // Returns an array of the elements in the union of array1 and array2, without duplicates.
- arrays_zip  // Returns a merged array of structs in which the N-th struct contains all N-th values of input arrays.
```sql
SELECT arrays_zip(array(1, 2, 3), array(2, 3, 4));  -- [{1, 2}, {2, 3}, {3, 4}]
SELECT arrays_zip(array(1, 2), array(2, 3), array(3, 4));  -- [{1, 2, 3}, {2, 3, 4}]
```
<img width="650" alt="image" src="https://github.com/user-attachments/assets/1bb4018a-2fe1-4be0-b769-9f4a4478f2d1" />
<img width="852" alt="image" src="https://github.com/user-attachments/assets/e47c7d18-c7b9-4209-a60b-0a780eb22e3e" />

- flatten  // Transforms an array of arrays into a single array.
```sql
SELECT flatten(array(array(1, 2), array(3, 4)));  -- [1, 2, 3, 4]
```
- get(array, index)	 // Returns element of array at given (0-based) index. If the index points outside of the array boundaries, then this function returns NULL.
- sequence(start, stop, step)
- slice(x, start, length)	 // Subsets array x starting from index start (array indices start at 1, or starting from the end if start is negative) with the specified length.
- sort_array(array[, ascendingOrder])	 // Null elements will be placed at the beginning of the returned array in ascending order or at the end of the returned array in descending order.

---

## map related  
- (try_)element_at(array, index)  // Returns element of array at given (1-based) index.
- (try_)element_at(map, key)  // Returns value for given key. The function returns NULL if the key is not contained in the map.
- map(key0, value0, key1, value1, ...)  // Creates a map
- map_concat(map, ...)
- map_contains_key(map, key)
- map_entries(map)	// Returns an unordered array of all entries in the given map.
```sql
“entry”在英语里常作为“入口”用词，但在数据结构或数据库语境下，entry 指的是“一个键值对项”（key-value pair）。
map_entries(map) 就是把“字典”里的每一组（key,value）“拆包”成数组，或者说“变成一张两列的表”。
在SQL（如 Presto、Trino、SparkSQL、ClickHouse 等）里的 map 结构，本质就是一个“键→值”的两列关系，即“key→value”
每个key只能对应一个value
... 你每个map entry依然只有两列（key和value），但value本身可以是Record、对象或结构体，可以有多个字段。
SELECT map_entries(map(1, 'a', 2, 'b'));  -- [{1, a}, {2, b}]
```
- map_from_arrays()
```sql
SELECT map_from_arrays(array(1.0, 3.0), array('2', '4'));
-- {1.0 -> 2, 3.0 -> 4}
```
- map_from_entries
```sql
SELECT map_from_entries(array(struct(1, 'a'), struct(2, 'b')));  -- {1 -> a, 2 -> b}
看到 map: 就是字典{key→value}
看到 entries: 就是一堆(key,value)一组的东西
看到 map_from_entries: 就是把这些组装成字典
看到 map_entries: 就是把字典拆成一堆(key,value)的行
```
- map_keys, map_values  // Returns an unordered array containing the keys/values of the map
- str_to_map(text[, pairDelim[, keyValueDelim]])
```sql
SELECT str_to_map('a:1,b:2,c:3', ',', ':');
```

---

## date timestamp related
```sql
select current_timestamp(), timestamp('2023-01-31T04:07:37.993+00:00') - interval 2 days
// 你如果写的是 '2023-01-31T04:07:37.993+08:00' 那么会自动帮你转成+00的时间 如果你没写或写的直接是+00 那么时间就不会变 仍然是+00
```
- add_months  // 加的是month，可以减
- date_add  // 加的是day，可以减 或者有date_sub
- convert_timezone  // 从一个地区时间转换到另一个地区时间
```sql
SELECT convert_timezone('UTC', 'Asia/Shanghai', timestamp_ntz'2021-12-06 00:00:00');  -- 2021-12-06T08:00:00.000
SELECT convert_timezone('UTC', 'UTC+8', timestamp_ntz'2021-12-06 00:00:00');  -- 2021-12-06T08:00:00.000
SELECT convert_timezone('UTC+8', timestamp_ntz'2021-12-06 00:00:00'); -- 2021-12-06T08:00:00.000 默认第一个param是utc
select convert_timezone('UTC', 'Asia/Shanghai', now())  -- current local time as now() would return current utc response
类似 from_utc_timestamp(timestamp/string, timezone)
```
- current_date()
- current_timestamp()
- date_diff(end, start)
```
select from_utc_timestamp(from_unixtime(1738146297797/1000), 'UTC+8'), to_date(from_unixtime(1738146297797/1000)), current_timestamp(), date_diff(MONTH, timestamp(from_unixtime(1738146297797/1000)), current_timestamp())
```
- date_format  // 把timestamp转换成string
```sql
SELECT date_format('2016-04-08', 'y');  -- 2016
SELECT date_format(current_date(), 'yyyy-MM-dd');  -- 2025-05-20
SELECT date_format(now(), 'yyyy-MM-dd HH:mm:ss');  -- 2025-05-20 02:58:14
```
- date_from_unix_date  // Create date from the number of days since 1970-01-01.
```
date_from_unix_date(x) 里的参数 x 必须是从 1970-01-01 开始的“天数”（整数天），而不是你常见的秒或毫秒级Unix时间戳。
1738146297797 是一个毫秒级时间戳（通常是13位数，远大于一天数int能存的范围），会溢出。
如果是毫秒级时间戳，先除以1000得到秒
如果是秒级时间戳 from_unixtime(CAST(kc.created_at AS BIGINT))
date_from_unix_date 的参数范围超了int最大，强制类型转的时候报溢出错。
select from_unixtime(1738146297797/1000)  -- 2025-01-29 10:24:57
```
- date_part(field, source)  // Extracts a part of the date/timestamp or interval source.
```sql
select date_part('year', now());  -- 2025
select date_part('month', now()); -- 5
select date_part('day', now()); -- 20
select date_part('week', now());  -- 21
select date_part('doy', timestamp('2025-02-10'));  -- 41 (days of the year) [没有所谓的dom，这种效果你直接看day就行了]
select date_part('dow', timestamp('2025-05-25'));  -- 1 (day of the week, 1 is Sunday, 2 is Monday)
select date_part('days', interval 5 days 3 hours 7 minutes 30 seconds 1 milliseconds 1 microseconds);  -- 5
select date_part('minutes', interval 5 days 3 hours 7 minutes 30 seconds 1 milliseconds 1 microseconds);  -- 7
```
- date_trunc(fmt, ts)  // Returns timestamp that is truncated to the unit specified by the format model
```sql
select date_trunc('MONTH', now());  -- 2025-05-01T00:00:00.000+00:00
DAY MONTH QUARTER WEEK YEAR MINUTE SECOND ...
```
- make_date()
```sql
select make_date(2025, 11, 8)  -- 2025-11-08
```
- last_day(date)  // 返回当月的最后一天
```sql
SELECT last_day('2009-01-12');  -- 2009-01-31
```
- window(time_column, window_duration[, slide_duration[, start_time]])  // 如果你没做实时流式大数据，没做事件流分析/传感器/行为数据监控，确实日常做业务SQL很难用到
```sql
SELECT
  window(event_time, '5 minutes') as win,
  sum(amount)
FROM events
GROUP BY window(event_time, '5 minutes')
# 如果你要每5分钟统计一次总金额，window会自动帮你把这些 row 按照 12:00-12:05, 12:05-12:10, 12:10-12:15... 分组。
```
- unix_date  // Returns the number of days since 1970-01-01.
- unix_millis
- unix_micros
- from_unixtime
```sql
SELECT from_unixtime(0);  -- 1970-01-01 00:00:00
select from_unixtime(1752529852653/1000, 'yyyy-MM-dd')  -- 2025-07-14
SELECT unix_date(DATE("1970-01-02"));  -- 1
---

## json related  
- from_json(jsonStr, schema[, options])	 // `SELECT from_json('{"a":1, "b":0.8}', 'a INT, b DOUBLE')['a'];`
- get_json_object(json_txt, path)	 // Extracts a json object from `path`.
```sql
-- $ 就是整个 JSON 的根，$. 表示“从顶层往下”，用于写JSON路径
SELECT get_json_object('{"a":"b"}', '$.a');  -- b
SELECT get_json_object('{"user":{"name":"张三", "age":18}, "status":"ok"}', '$.user.name');  -- 张三
SELECT get_json_object('{"tags":["a","b","c"], "count": 3}', '$.tags[1]');  -- b
```
```sql
-- 特殊 如果key是带引号的话
SELECT
  get_json_object(extra_info::string,
    "$.oktaUser['urn:ietf:params:scim:schemas:extension:enterprise:2.0:User']") AS enterprise_raw,
  get_json_object(extra_info::string,
    '$.oktaUser.schemas[1]') AS idname,
    extra_info,
    *
FROM `tp-prod-sg`.silver.airboardngauth__account
where id = '330'
```
- json_array_length(jsonArray) 
- json_object_keys(json_object)
- json_tuple  // 能一次性从 JSON 字符串里“批量取出多个字段”，每个字段单独成一列。它只支持扁平、不嵌套的key
```sql
SELECT json_tuple('{"order_id": 1234, "item": {"name": "Beer", "price": 10}, "customer": "张三"}', 'order_id', 'item')
-- json_tuple：只能用字段名，不加$，不允许路径，只会找最外面的key
-- get_json_object / json_extract：必须以$开头，完整写路径
```
- schema_of_json
- to_json()  // Returns a JSON string with a given struct value
```sql
SELECT to_json(array(named_struct('a', 1, 'b', 2)));  -- [{"a":1,"b":2}]
SELECT to_json(map('a', named_struct('b', 1)));  -- {"a":{"b":1}}
SELECT to_json(array(map('a', 1)));  -- [{"a":1}]
```

---

## string related  
- trim ltrim rtrim
- len length char_length character_length
- concat_ws  // concatenation of the strings separated by `sep`, skipping null values
```sql
SELECT concat_ws('/', 'foo', null, 'bar');  -- foo/bar
```
- contains(left, right)  // Returns a boolean. The value is True if right is found inside left.
- instr locate position  // Returns the (1-based) index of the first occurrence of `substr` in `str`.
- find_in_set(str, str_array)  // Returns the index (1-based) of the given string (`str`) in the comma-delimited list (`str_array`). Returns 0, if the string was not found or if the given string (`str`) contains a comma.
- endwith startwith
- initcap  // 空格隔开的每个单词的首字母大写
- lower lcase upper ucase
- format_string printf  // `SELECT printf("Hello World %d %s", 100, "days");  -- Hello World 100 days`
- regexp_count regexp_extract regexp_extract_all regexp_instr regexp_replace
- repeat  // 重复string
- replace  // 区分大小写的
- split split_part(不接受[...])
```sql
SELECT split('oneAtwoBthreeCfourDfive', '[ABCd]');  -- ["one","two","three","fourDfive"]
SELECT split('oneAtwoBthreeCfourDfive', '[ABCd]', 3);  -- ["one","two","threeCfourDfive"]
SELECT split('oneAtwoBthreeCfourDfive', '[ABCd]', -1);  -- ["one","two","three","fourDfive"]
SELECT split_part('oneAtwoBthreeCfourDfive', 'o', -1); -- urDfive
SELECT split_part('oneAtwoBthreeCfourDfive', 'o', 2); -- neAtw
```

---

## conditional related
- coalesce

---

## conversion related
- cast(expr AS type)

---

## predicate related
- !expression  // logical not
- expr1 <=> expr2  // 就是想让“两个都是NULL”也算“相等”，规避掉NULL导致的“比对失效”
<img width="857" alt="image" src="https://github.com/user-attachments/assets/3a77fd3d-1f78-490d-898a-bcbc47b5e113" />
- = ==
- regexp regexp_like rlike  // Returns true if `str` matches `regexp`, or false otherwise.
```sql
-- Python： r'abc\n' => "abc\n"（四个字符）
-- Spark SQL (escapedStringLiterals=false)： 'abc\n' => "abc\n"（四个字符）
-- Spark SQL (escapedStringLiterals=true)： 'abc\n' => "abc" + 换行
SELECT regexp('%SystemDrive%\\Users\\John', '%SystemDrive%\\\\Users.*');  -- true
SELECT regexp('%SystemDrive%\\Users\\John', r'%SystemDrive%\\\\Users.*');  -- false
select 'hello\\n\nworld';  -- hello\n换行world
```
- like
```sql
like 'a%_b%'  -- a后跟着至少一任意字符，然后b及后续内容
like '%#_%' escape '#'  -- "#_"会匹配真实的下划线
```

---

## window related
- lead 后一行
- lag 前一行
- dense_rank  -- 1,1,2,...
- rank  -- 1,1,3,...
- nth_value  `nth_value(wlb.list_element:createdBy::string, 1, true) over (partition by ... order by wlb.list_element:createTime::bigint desc) as creator` `nth_value(case when startswith(op.operation_type, 'KYC_S_OPS') then op.operator_email end, 1, true) over (partition by ikl.kyc_case_id order by op.operation_time desc rows between unbounded preceding and unbounded following) as last_operator_level_two`
- row_number

---

## others
- current_user, user
- typeof
- explode
BigQuery/标准SQL: UNNEST 一般写在 FROM 或 JOIN 后面，相当于"炸"列变多行；  
Spark SQL: 直接 explode 写 SELECT 里，或写成 LATERAL VIEW explode(arr) AS num。
gsheet里的explode，尤其是param，```SELECT explode(split(@btwo, ',')) AS temp_field```
```sql
SELECT e.col1, e.col2
FROM (SELECT explode(array(struct(10, 20), struct(null, 55))) AS e)
```
```sql
with temp as (
  -- 构造数据
SELECT 101 AS user_id, array(
    named_struct('reviewDate', '2024-01-01', 'reviewResult', 'PASS', 'reviewType', 'KYC'),
    named_struct('reviewDate', '2024-01-05', 'reviewResult', 'FAIL', 'reviewType', 'AML')
) AS reviews
UNION ALL
SELECT 102, array(
    named_struct('reviewDate', '2024-02-01', 'reviewResult', 'PASS', 'reviewType', 'KYC')
)
UNION ALL
SELECT 103, array()  -- 空数组
)

SELECT
  user_id,
  r.reviewDate,
  r.reviewResult,
  r.reviewType
FROM (
  temp
) t
LATERAL VIEW OUTER explode(reviews) AS r
-- 用LATERAL VIEW OUTER 或 explode_outer()可以实现类似LEFT JOIN的效果，即保留主表原有行，即便数组为空。
-- LATERAL VIEW explode（不带OUTER）行为类似inner join，有空数组就会把那行“炸没”。
```
```
...
lateral view outer posexplode(cast (kc.data:decisions as array<struct<comment:string, final:boolean, maker:string, result:string, reasons:array<string>, time:timestamp, source:string, additionalInfo:struct<actions:array<string>, assignTo:string, assignToLevel:string, referForAction:string>>>)) as `index`, decision_log
...
qualify row_number() over (partition by kc.id order by `index` desc) = 1
```
```sql
-- variant 好比“超大百宝箱”，到底能不能explode要先搞清楚它是不是“装了数组”！能的话先转array，不能就不能直接爆
-- 结构体数组要“点名道姓”写struct才能转
-- 面对很大的variant，不是必须所有字段都写struct; `CAST(arr_column AS ARRAY<STRUCT<字段1:STRING, 字段9:INT>>)`

select 
a.id::string as account_id,
-- cast(a.data:kycRecord:kycReviewedRecords as ARRAY<STRUCT<reviewDate:TIMESTAMP, reviewResult:STRING, reviewType:STRING>>)
r.reviewDate

from `tp-prod-sg`.`silver`.`authorisation__account` as a
lateral view explode(cast(a.data:kycRecord:kycReviewedRecords as ARRAY<STRUCT<reviewDate:STRING, reviewResult:STRING, reviewType:STRING>>)) as r
where a.id = '8f7ac892-b2aa-4f0c-afea-8ed67784e550'
```
```sql
-- 解析和展开
SELECT 
  id, 
  item 
FROM `fp-prod-sg`.silver.midas__midas_product
LATERAL VIEW explode(from_json(price_matching_strategy?::string, 'ARRAY<STRING>')) e AS item
WHERE id = 'PAYMENT_METHOD_FEE'

select distinct
cle.id as legal_entity_id,
bpr,
roles
from `tp-prod-sg`.silver.authorisation__client_legal_entity as cle
left join `tp-prod-sg`.silver.authorisation__business_profile as bp on bp.id = cle.data:profileId::string
lateral view outer explode(cast(bp.data:businessPeople as array<struct<roles: array<string>, personId: string>>)) as bpr
lateral view outer explode(bpr.roles) as roles
where cle.id = '24a68250-3b1a-49b1-8302-b67d5d8a0290'

-- 如果您只想获取整个数组而不展开
SELECT 
  id, 
  from_json(price_matching_strategy?::string, 'ARRAY<STRING>') AS strategy_array
FROM `fp-prod-sg`.silver.midas__midas_product
WHERE id = 'PAYMENT_METHOD_FEE'


["item1", "item2", "item3"]
✅ 正确用法: 'ARRAY<STRING>'

{"key1": "value1", "key2": "value2"}
✅ 正确用法: 'MAP<STRING, STRING>'

[
  {"reviewDate": "2023-01-01", "reviewResult": "pass", "reviewType": "annual"},
  {"reviewDate": "2023-06-01", "reviewResult": "fail", "reviewType": "interim"}
]
✅ 正确用法: 'ARRAY<STRUCT<reviewDate:STRING, reviewResult:STRING, reviewType:STRING>>'

{"reviewDate": "2023-01-01", "reviewResult": "pass", "reviewType": "annual"}
✅ 正确用法: 'STRUCT<reviewDate:STRING, reviewResult:STRING, reviewType:STRING>'
```

