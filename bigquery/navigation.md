```FIRST_VALUE```  
```LAST_VALUE```  
Gets a value for the first/last row in the current window frame.  
https://cloud.google.com/bigquery/docs/reference/standard-sql/navigation_functions#first_value  
```
WITH finishers AS
 (SELECT 'Sophia Liu' as name,
  TIMESTAMP '2016-10-18 2:51:45' as finish_time,
  'F30-34' as division
  UNION ALL SELECT 'Lisa Stelzner', TIMESTAMP '2016-10-18 2:54:11', 'F35-39'
  UNION ALL SELECT 'Nikki Leith', TIMESTAMP '2016-10-18 2:59:01', 'F30-34'
  UNION ALL SELECT 'Lauren Matthews', TIMESTAMP '2016-10-18 3:01:17', 'F35-39'
  UNION ALL SELECT 'Desiree Berry', TIMESTAMP '2016-10-18 3:05:42', 'F35-39'
  UNION ALL SELECT 'Suzy Slane', TIMESTAMP '2016-10-18 3:06:24', 'F35-39'
  UNION ALL SELECT 'Jen Edwards', TIMESTAMP '2016-10-18 3:06:36', 'F30-34'
  UNION ALL SELECT 'Meghan Lederer', TIMESTAMP '2016-10-18 3:07:41', 'F30-34'
  UNION ALL SELECT 'Carly Forte', TIMESTAMP '2016-10-18 3:08:58', 'F25-29'
  UNION ALL SELECT 'Lauren Reasoner', TIMESTAMP '2016-10-18 3:10:14', 'F30-34')
SELECT name,
  FORMAT_TIMESTAMP('%X', finish_time) AS finish_time,
  division,
  FORMAT_TIMESTAMP('%X', fastest_time) AS fastest_time,
  TIMESTAMP_DIFF(finish_time, fastest_time, SECOND) AS delta_in_seconds
FROM (
  SELECT name,
  finish_time,
  division,
  FIRST_VALUE(finish_time)
    OVER (PARTITION BY division ORDER BY finish_time ASC
    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS fastest_time
  FROM finishers);

/*-----------------+-------------+----------+--------------+------------------*
 | name            | finish_time | division | fastest_time | delta_in_seconds |
 +-----------------+-------------+----------+--------------+------------------+
 | Carly Forte     | 03:08:58    | F25-29   | 03:08:58     | 0                |
 | Sophia Liu      | 02:51:45    | F30-34   | 02:51:45     | 0                |
 | Nikki Leith     | 02:59:01    | F30-34   | 02:51:45     | 436              |
 | Jen Edwards     | 03:06:36    | F30-34   | 02:51:45     | 891              |
 | Meghan Lederer  | 03:07:41    | F30-34   | 02:51:45     | 956              |
 | Lauren Reasoner | 03:10:14    | F30-34   | 02:51:45     | 1109             |
 | Lisa Stelzner   | 02:54:11    | F35-39   | 02:54:11     | 0                |
 | Lauren Matthews | 03:01:17    | F35-39   | 02:54:11     | 426              |
 | Desiree Berry   | 03:05:42    | F35-39   | 02:54:11     | 691              |
 | Suzy Slane      | 03:06:24    | F35-39   | 02:54:11     | 733              |
 *-----------------+-------------+----------+--------------+------------------*/
```

```NTH_VALUE```  
Returns the value of value_expression at the Nth row of the current window frame, where Nth is defined by constant_integer_expression. Returns NULL if there is no such row.  
https://cloud.google.com/bigquery/docs/reference/standard-sql/navigation_functions#nth_value  
```
WITH finishers AS
 (SELECT 'Sophia Liu' as name,
  TIMESTAMP '2016-10-18 2:51:45' as finish_time,
  'F30-34' as division
  UNION ALL SELECT 'Lisa Stelzner', TIMESTAMP '2016-10-18 2:54:11', 'F35-39'
  UNION ALL SELECT 'Nikki Leith', TIMESTAMP '2016-10-18 2:59:01', 'F30-34'
  UNION ALL SELECT 'Lauren Matthews', TIMESTAMP '2016-10-18 3:01:17', 'F35-39'
  UNION ALL SELECT 'Desiree Berry', TIMESTAMP '2016-10-18 3:05:42', 'F35-39'
  UNION ALL SELECT 'Suzy Slane', TIMESTAMP '2016-10-18 3:06:24', 'F35-39'
  UNION ALL SELECT 'Jen Edwards', TIMESTAMP '2016-10-18 3:06:36', 'F30-34'
  UNION ALL SELECT 'Meghan Lederer', TIMESTAMP '2016-10-18 3:07:41', 'F30-34'
  UNION ALL SELECT 'Carly Forte', TIMESTAMP '2016-10-18 3:08:58', 'F25-29'
  UNION ALL SELECT 'Lauren Reasoner', TIMESTAMP '2016-10-18 3:10:14', 'F30-34')
SELECT name,
  FORMAT_TIMESTAMP('%X', finish_time) AS finish_time,
  division,
  FORMAT_TIMESTAMP('%X', fastest_time) AS fastest_time,
  FORMAT_TIMESTAMP('%X', second_fastest) AS second_fastest
FROM (
  SELECT name,
  finish_time,
  division,finishers,
  FIRST_VALUE(finish_time)
    OVER w1 AS fastest_time,
  NTH_VALUE(finish_time, 2)
    OVER w1 as second_fastest
  FROM finishers
  WINDOW w1 AS (
    PARTITION BY division ORDER BY finish_time ASC
    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING));

/*-----------------+-------------+----------+--------------+----------------*
 | name            | finish_time | division | fastest_time | second_fastest |
 +-----------------+-------------+----------+--------------+----------------+
 | Carly Forte     | 03:08:58    | F25-29   | 03:08:58     | NULL           |
 | Sophia Liu      | 02:51:45    | F30-34   | 02:51:45     | 02:59:01       |
 | Nikki Leith     | 02:59:01    | F30-34   | 02:51:45     | 02:59:01       |
 | Jen Edwards     | 03:06:36    | F30-34   | 02:51:45     | 02:59:01       |
 | Meghan Lederer  | 03:07:41    | F30-34   | 02:51:45     | 02:59:01       |
 | Lauren Reasoner | 03:10:14    | F30-34   | 02:51:45     | 02:59:01       |
 | Lisa Stelzner   | 02:54:11    | F35-39   | 02:54:11     | 03:01:17       |
 | Lauren Matthews | 03:01:17    | F35-39   | 02:54:11     | 03:01:17       |
 | Desiree Berry   | 03:05:42    | F35-39   | 02:54:11     | 03:01:17       |
 | Suzy Slane      | 03:06:24    | F35-39   | 02:54:11     | 03:01:17       |
 *-----------------+-------------+----------+--------------+----------------*/
```

```LAG```  
Returns the value of the value_expression on a **preceding** row. 看上面  
Changing the offset value changes which preceding row is returned; the default value is 1, indicating the previous row in the window frame.  
https://cloud.google.com/bigquery/docs/reference/standard-sql/navigation_functions#lag  
```
WITH finishers AS
 (SELECT 'Sophia Liu' as name,
  TIMESTAMP '2016-10-18 2:51:45' as finish_time,
  'F30-34' as division
  UNION ALL SELECT 'Lisa Stelzner', TIMESTAMP '2016-10-18 2:54:11', 'F35-39'
  UNION ALL SELECT 'Nikki Leith', TIMESTAMP '2016-10-18 2:59:01', 'F30-34'
  UNION ALL SELECT 'Lauren Matthews', TIMESTAMP '2016-10-18 3:01:17', 'F35-39'
  UNION ALL SELECT 'Desiree Berry', TIMESTAMP '2016-10-18 3:05:42', 'F35-39'
  UNION ALL SELECT 'Suzy Slane', TIMESTAMP '2016-10-18 3:06:24', 'F35-39'
  UNION ALL SELECT 'Jen Edwards', TIMESTAMP '2016-10-18 3:06:36', 'F30-34'
  UNION ALL SELECT 'Meghan Lederer', TIMESTAMP '2016-10-18 3:07:41', 'F30-34'
  UNION ALL SELECT 'Carly Forte', TIMESTAMP '2016-10-18 3:08:58', 'F25-29'
  UNION ALL SELECT 'Lauren Reasoner', TIMESTAMP '2016-10-18 3:10:14', 'F30-34')
SELECT name,
  finish_time,
  division,
  LAG(name, 2)
    OVER (PARTITION BY division ORDER BY finish_time ASC) AS two_runners_ahead
FROM finishers;

/*-----------------+-------------+----------+-------------------*
 | name            | finish_time | division | two_runners_ahead |
 +-----------------+-------------+----------+-------------------+
 | Carly Forte     | 03:08:58    | F25-29   | NULL              |
 | Sophia Liu      | 02:51:45    | F30-34   | NULL              |
 | Nikki Leith     | 02:59:01    | F30-34   | NULL              |
 | Jen Edwards     | 03:06:36    | F30-34   | Sophia Liu        |
 | Meghan Lederer  | 03:07:41    | F30-34   | Nikki Leith       |
 | Lauren Reasoner | 03:10:14    | F30-34   | Jen Edwards       |
 | Lisa Stelzner   | 02:54:11    | F35-39   | NULL              |
 | Lauren Matthews | 03:01:17    | F35-39   | NULL              |
 | Desiree Berry   | 03:05:42    | F35-39   | Lisa Stelzner     |
 | Suzy Slane      | 03:06:24    | F35-39   | Lauren Matthews   |
 *-----------------+-------------+----------+-------------------*/
```

```LEAD```  
Returns the value of the value_expression on a subsequent row. 看下面  
Changing the offset value changes which subsequent row is returned; the default value is 1, indicating the next row in the window frame.  
https://cloud.google.com/bigquery/docs/reference/standard-sql/navigation_functions#lead  
```
WITH finishers AS
 (SELECT 'Sophia Liu' as name,
  TIMESTAMP '2016-10-18 2:51:45' as finish_time,
  'F30-34' as division
  UNION ALL SELECT 'Lisa Stelzner', TIMESTAMP '2016-10-18 2:54:11', 'F35-39'
  UNION ALL SELECT 'Nikki Leith', TIMESTAMP '2016-10-18 2:59:01', 'F30-34'
  UNION ALL SELECT 'Lauren Matthews', TIMESTAMP '2016-10-18 3:01:17', 'F35-39'
  UNION ALL SELECT 'Desiree Berry', TIMESTAMP '2016-10-18 3:05:42', 'F35-39'
  UNION ALL SELECT 'Suzy Slane', TIMESTAMP '2016-10-18 3:06:24', 'F35-39'
  UNION ALL SELECT 'Jen Edwards', TIMESTAMP '2016-10-18 3:06:36', 'F30-34'
  UNION ALL SELECT 'Meghan Lederer', TIMESTAMP '2016-10-18 3:07:41', 'F30-34'
  UNION ALL SELECT 'Carly Forte', TIMESTAMP '2016-10-18 3:08:58', 'F25-29'
  UNION ALL SELECT 'Lauren Reasoner', TIMESTAMP '2016-10-18 3:10:14', 'F30-34')
SELECT name,
  finish_time,
  division,
  LEAD(name)
    OVER (PARTITION BY division ORDER BY finish_time ASC) AS followed_by
FROM finishers;

/*-----------------+-------------+----------+-----------------*
 | name            | finish_time | division | followed_by     |
 +-----------------+-------------+----------+-----------------+
 | Carly Forte     | 03:08:58    | F25-29   | NULL            |
 | Sophia Liu      | 02:51:45    | F30-34   | Nikki Leith     |
 | Nikki Leith     | 02:59:01    | F30-34   | Jen Edwards     |
 | Jen Edwards     | 03:06:36    | F30-34   | Meghan Lederer  |
 | Meghan Lederer  | 03:07:41    | F30-34   | Lauren Reasoner |
 | Lauren Reasoner | 03:10:14    | F30-34   | NULL            |
 | Lisa Stelzner   | 02:54:11    | F35-39   | Lauren Matthews |
 | Lauren Matthews | 03:01:17    | F35-39   | Desiree Berry   |
 | Desiree Berry   | 03:05:42    | F35-39   | Suzy Slane      |
 | Suzy Slane      | 03:06:24    | F35-39   | NULL            |
 *-----------------+-------------+----------+-----------------*/
```

```PERCENTILE_CONT``` Computes the specified percentile value for the value_expression, with linear interpolation.  
```PERCENTILE_DISC``` Computes the specified percentile value for a discrete value_expression. The returned value is the first sorted value of value_expression with cumulative distribution greater than or equal to the given percentile value.  
```
SELECT
  PERCENTILE_CONT(x, 0 RESPECT NULLS) OVER() AS min,
  PERCENTILE_CONT(x, 0.01 RESPECT NULLS) OVER() AS percentile1,
  PERCENTILE_CONT(x, 0.5 RESPECT NULLS) OVER() AS median,
  PERCENTILE_CONT(x, 0.9 RESPECT NULLS) OVER() AS percentile90,
  PERCENTILE_CONT(x, 1 RESPECT NULLS) OVER() AS max
FROM UNNEST([0, 3, NULL, 1, 2]) AS x LIMIT 1;

/*------+-------------+--------+--------------+-----*
 | min  | percentile1 | median | percentile90 | max |
 +------+-------------+--------+--------------+-----+
 | NULL | 0           | 1      | 2.6          | 3   |
 *------+-------------+--------+--------------+-----*/
```
```
SELECT
  x,
  PERCENTILE_DISC(x, 0 RESPECT NULLS) OVER() AS min,
  PERCENTILE_DISC(x, 0.5 RESPECT NULLS) OVER() AS median,
  PERCENTILE_DISC(x, 1 RESPECT NULLS) OVER() AS max
FROM UNNEST(['c', NULL, 'b', 'a']) AS x;

/*------+------+--------+-----*
 | x    | min  | median | max |
 +------+------+--------+-----+
 | c    | NULL | a      | c   |
 | NULL | NULL | a      | c   |
 | b    | NULL | a      | c   |
 | a    | NULL | a      | c   |
 *------+------+--------+-----*/
```

