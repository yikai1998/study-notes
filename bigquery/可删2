https://cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax#unnest_operator  
The ```UNNEST``` operator takes an array and returns a table with one row for each element in the array.  
```
SELECT * FROM UNNEST ([10,20,30]) as numbers WITH OFFSET WHERE numbers IN UNNEST([10, 20]);

/*---------+--------*
 | numbers | offset |
 +---------+--------+
 | 10      | 0      |
 | 20      | 1      |
 *---------+--------*/
```

**Example: Sorting an Array During UNNEST**
```
WITH example_data AS (
  SELECT 1 AS id, [10, 30, 20] AS array_column UNION ALL
  SELECT 2 AS id, [3, 1, 2] AS array_column
)

SELECT
  id, s, sorted_element_with_offset
FROM (
  SELECT
    id,
    ARRAY(SELECT element FROM UNNEST(array_column) AS element ORDER BY element ASC) AS sorted_array
  FROM example_data
),
UNNEST(sorted_array) AS s WITH OFFSET AS sorted_element_with_offset
```

---

```
WITH example_data AS (
  SELECT 
  ARRAY[1, 3, 3, 4, 5] AS int_array,
  ['x', 'x', 'z'] AS str_array 
) 

# cross join effect 
SELECT 
qq, 
qq2 
FROM
example_data,
UNNEST(example_data.int_array) AS qq, 
UNNEST(example_data.str_array) AS qq2 

# cross join effect 
SELECT 
qq, 
qq2 
FROM
example_data 
LEFT JOIN UNNEST(example_data.int_array) AS qq 
LEFT JOIN UNNEST(example_data.str_array) AS qq2 

# one by one target effect 
SELECT 
qq, 
idx, 
qq2, 
idx2, 
FROM 
example_data, 
example_data.int_array AS qq WITH OFFSET AS idx  -- UNNEST(example_data.int_array) AS qq WITH OFFSET AS idx 
LEFT JOIN example_data.str_array AS qq2 WITH OFFSET AS idx2 ON idx2 = idx
```
