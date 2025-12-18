[work with arrays](https://cloud.google.com/bigquery/docs/arrays)  
[array functions](https://cloud.google.com/bigquery/docs/reference/standard-sql/array_functions)

When you use SQL to create arrays, such as with ```ARRAY()``` or ```[]```, you should only include elements of the same data type within the array. This is because SQL arrays are strongly typed, meaning that all elements within an array must conform to the same data type.  
```
SELECT ARRAY[1, 2, 3, 4, 5] AS int_array
```

If you need a collection of mixed-type data, consider structuring your data differently, such as using an array of STRUCTs where each STRUCT can encapsulate multiple fields of different types.  
```
select
  array[
    struct(1 as idx, "alice" as name, true as active),
    struct(2 as idx, "bob" as name, false as active)
  ] as employee
```

---

The ```ARRAY()``` constructor is an explicit method to create an array. It is used to specify array elements within an **SQL query**.  
The ```[]``` syntax is often used to provide **array literals directly** in SQL queries. It is shorthand for defining arrays directly. Same as ``ARRAY[]```
Regardless of whether you use ARRAY or [], the array elements must be of the same data type within the array.  

```ARRAY()```
The ARRAY function returns an ARRAY with one element for each row in a subquery.  
If subquery produces a SQL table, the table must have exactly one column. Each element in the output ARRAY is the value of the single column of a row in the table.  
```
SELECT ARRAY
  (SELECT 1 UNION ALL
   SELECT 2 UNION ALL
   SELECT 3) AS new_array;

/*-----------*
 | new_array |
 +-----------+
 | [1, 2, 3] |
 *-----------*/
```
To construct an ARRAY from a subquery that contains multiple columns, change the subquery to use ```SELECT AS STRUCT```. Now the ARRAY function will return an ARRAY of STRUCTs. The ARRAY will contain one STRUCT for each row in the subquery, and each of these STRUCTs will contain a field for each column in that row.  
```
SELECT
  ARRAY
    (SELECT AS STRUCT 1, 2, 3
     UNION ALL SELECT AS STRUCT 4, 5, 6) AS new_array;

/*------------------------*
 | new_array              |
 +------------------------+
 | [{1, 2, 3}, {4, 5, 6}] |
 *------------------------*/
```

```
WITH sales AS (
  SELECT '2024-01-01' AS sale_date, 'Product A' AS product_name, 10 AS quantity_sold UNION ALL
  SELECT '2024-01-01', 'Product B', 15 UNION ALL
  SELECT '2024-01-02', 'Product A', 12 UNION ALL
  SELECT '2024-01-02', 'Product B', 18
)
SELECT
  sale_date,
  ARRAY_AGG(STRUCT(product_name, quantity_sold)) AS sales_array
FROM sales
GROUP BY sale_date;
```
![image](https://github.com/user-attachments/assets/dde871f9-559c-4b72-950d-6ed08d19cc25)

ARRAY_AGG is typically used with GROUP BY: Because it aggregates row data over groups, collecting all applicable entries into arrays.  
ARRAY_AGG() 的参数可以是任何表达式，包括：  
标量（STRING、INT64 等）  
STRUCT(...) e.g. ```ARRAY_AGG(STRUCT(account_id, businessdetails_businessname_local)) AS accounts```  
甚至是“整行记录”（也就是 table 的 row，本身就是一个隐式 struct）  
这里参数是 STRUCT(...)，结果 accounts 是 ARRAY<STRUCT<account_id STRING, businessdetails_businessname_local STRING>>  

---

```
ARRAY_CONCAT()
SELECT ARRAY_CONCAT([1, 2], [3, 4], [5, 6]) as count_to_six;
```

```
ARRAY_LENGTH()
SELECT
  ARRAY_LENGTH(["coffee", NULL, "milk" ]) AS size_a,
  ARRAY_LENGTH(["cake", "pie"]) AS size_b,
  ARRAY_LENGTH(NULL) AS size_c;
```

```
ARRAY_REVERSE()
SELECT ARRAY_REVERSE([1, 2, 3]) AS reverse_arr
```

```
ARRAY_TO_STRING()
SELECT ARRAY_TO_STRING(['coffee', 'tea', 'milk', NULL], ' || ', 'MISSING') AS text
```

```
GENERATE_ARRAY()
Returns an array of values. The start_expression and end_expression parameters determine the inclusive start and end of the array, with a default step of 1

SELECT GENERATE_ARRAY(10, 0, -3) AS example_array;
/*---------------*
 | example_array |
 +---------------+
 | [10, 7, 4, 1] |
 *---------------*/
SELECT GENERATE_ARRAY(start, 5) AS example_array FROM UNNEST([3, 4, 5]) AS start;
/*---------------*
 | example_array |
 +---------------+
 | [3, 4, 5]     |
 | [4, 5]        |
 | [5]           |
 +---------------*/
```

```
GENERATE_DATE_ARRAY()
Returns an array of dates. The start_date and end_date parameters determine the inclusive start and end of the array.
The default value for this parameter is 1 day.
date_part must be either DAY, WEEK, MONTH, QUARTER, or YEAR.

SELECT GENERATE_DATE_ARRAY('2016-01-01', 2016-12-31', INTERVAL 2 MONTH) AS example;
/*--------------------------------------------------------------------------*
 | example                                                                  |
 +--------------------------------------------------------------------------+
 | [2016-01-01, 2016-03-01, 2016-05-01, 2016-07-01, 2016-09-01, 2016-11-01] |
 *--------------------------------------------------------------------------*/
-----------------------------------------------------------------------------
SELECT GENERATE_DATE_ARRAY(date_start, date_end, INTERVAL 1 WEEK) AS date_range
FROM (
  SELECT DATE '2016-01-01' AS date_start, DATE '2016-01-31' AS date_end
  UNION ALL SELECT DATE "2016-04-01", DATE "2016-04-30"
  UNION ALL SELECT DATE "2016-07-01", DATE "2016-07-31"
  UNION ALL SELECT DATE "2016-10-01", DATE "2016-10-31"
) AS items;
/*--------------------------------------------------------------*
 | date_range                                                   |
 +--------------------------------------------------------------+
 | [2016-01-01, 2016-01-08, 2016-01-15, 2016-01-22, 2016-01-29] |
 | [2016-04-01, 2016-04-08, 2016-04-15, 2016-04-22, 2016-04-29] |
 | [2016-07-01, 2016-07-08, 2016-07-15, 2016-07-22, 2016-07-29] |
 | [2016-10-01, 2016-10-08, 2016-10-15, 2016-10-22, 2016-10-29] |
 *--------------------------------------------------------------*/

同理 GENERATE_TIMESTAMP_ARRAY()
https://cloud.google.com/bigquery/docs/reference/standard-sql/array_functions#generate_timestamp_array
```

