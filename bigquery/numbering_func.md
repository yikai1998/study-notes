https://cloud.google.com/bigquery/docs/reference/standard-sql/numbering_functions  
#### Numbering functions  
Numbering functions are a subset of window functions.  
Numbering functions assign integer values to each row based on their position within the specified window.  

---

`DENSE_RANK`  
```sql
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
  UNION ALL SELECT 'Meghan Lederer', TIMESTAMP '2016-10-18 2:59:01', 'F30-34')
SELECT name,
  finish_time,
  division,
  DENSE_RANK() OVER (PARTITION BY division ORDER BY finish_time ASC) AS finish_rank
FROM finishers;

/*-----------------+------------------------+----------+-------------*
 | name            | finish_time            | division | finish_rank |
 +-----------------+------------------------+----------+-------------+
 | Sophia Liu      | 2016-10-18 09:51:45+00 | F30-34   | 1           |
 | Meghan Lederer  | 2016-10-18 09:59:01+00 | F30-34   | 2           |
 | Nikki Leith     | 2016-10-18 09:59:01+00 | F30-34   | 2           |
 | Jen Edwards     | 2016-10-18 10:06:36+00 | F30-34   | 3           |
 | Lisa Stelzner   | 2016-10-18 09:54:11+00 | F35-39   | 1           |
 | Lauren Matthews | 2016-10-18 10:01:17+00 | F35-39   | 2           |
 | Desiree Berry   | 2016-10-18 10:05:42+00 | F35-39   | 3           |
 | Suzy Slane      | 2016-10-18 10:06:24+00 | F35-39   | 4           |
 *-----------------+------------------------+----------+-------------*/
```

---

`NTILE`  
This function divides the rows into constant_integer_expression buckets based on row ordering and returns the 1-based bucket number that is assigned to each row. The number of rows in the buckets can differ by at most 1. The remainder values (the remainder of number of rows divided by buckets) are distributed one for each bucket, starting with bucket 1.  
NTILE(N) 的分配规则  
- 尽可能让 N 个桶的行数相等。
- 如果不能均分，靠前的桶优先多分 1 行。
```sql
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
  UNION ALL SELECT 'Meghan Lederer', TIMESTAMP '2016-10-18 2:59:01', 'F30-34')
SELECT name,
  finish_time,
  division,
  NTILE(3) OVER (PARTITION BY division ORDER BY finish_time ASC) AS finish_rank
FROM finishers;

/*-----------------+------------------------+----------+-------------*
 | name            | finish_time            | division | finish_rank |
 +-----------------+------------------------+----------+-------------+
 | Sophia Liu      | 2016-10-18 09:51:45+00 | F30-34   | 1           |
 | Meghan Lederer  | 2016-10-18 09:59:01+00 | F30-34   | 1           |
 | Nikki Leith     | 2016-10-18 09:59:01+00 | F30-34   | 2           |
 | Jen Edwards     | 2016-10-18 10:06:36+00 | F30-34   | 3           |
 | Lisa Stelzner   | 2016-10-18 09:54:11+00 | F35-39   | 1           |
 | Lauren Matthews | 2016-10-18 10:01:17+00 | F35-39   | 1           |
 | Desiree Berry   | 2016-10-18 10:05:42+00 | F35-39   | 2           |
 | Suzy Slane      | 2016-10-18 10:06:24+00 | F35-39   | 3           |
 *-----------------+------------------------+----------+-------------*/
```

---

`RANK` 
```sql
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
  UNION ALL SELECT 'Meghan Lederer', TIMESTAMP '2016-10-18 2:59:01', 'F30-34')
SELECT name,
  finish_time,
  division,
  RANK() OVER (PARTITION BY division ORDER BY finish_time ASC) AS finish_rank
FROM finishers;

/*-----------------+------------------------+----------+-------------*
 | name            | finish_time            | division | finish_rank |
 +-----------------+------------------------+----------+-------------+
 | Sophia Liu      | 2016-10-18 09:51:45+00 | F30-34   | 1           |
 | Meghan Lederer  | 2016-10-18 09:59:01+00 | F30-34   | 2           |
 | Nikki Leith     | 2016-10-18 09:59:01+00 | F30-34   | 2           |
 | Jen Edwards     | 2016-10-18 10:06:36+00 | F30-34   | 4           |
 | Lisa Stelzner   | 2016-10-18 09:54:11+00 | F35-39   | 1           |
 | Lauren Matthews | 2016-10-18 10:01:17+00 | F35-39   | 2           |
 | Desiree Berry   | 2016-10-18 10:05:42+00 | F35-39   | 3           |
 | Suzy Slane      | 2016-10-18 10:06:24+00 | F35-39   | 4           |
 *-----------------+------------------------+----------+-------------*/
```

<img width="742" alt="image" src="https://github.com/user-attachments/assets/f74edf5c-fddc-4efd-97e7-30d6b32e2a18" />

---

`ROW_NUMBER`  
```sql
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
  UNION ALL SELECT 'Meghan Lederer', TIMESTAMP '2016-10-18 2:59:01', 'F30-34')
SELECT name,
  finish_time,
  division,
  ROW_NUMBER() OVER (PARTITION BY division ORDER BY finish_time ASC) AS finish_rank
FROM finishers;

/*-----------------+------------------------+----------+-------------+
 | name            | finish_time            | division | finish_rank |
 +-----------------+------------------------+----------+-------------+
 | Sophia Liu      | 2016-10-18 09:51:45+00 | F30-34   | 1           |
 | Meghan Lederer  | 2016-10-18 09:59:01+00 | F30-34   | 2           |
 | Nikki Leith     | 2016-10-18 09:59:01+00 | F30-34   | 3           |
 | Jen Edwards     | 2016-10-18 10:06:36+00 | F30-34   | 4           |
 | Lisa Stelzner   | 2016-10-18 09:54:11+00 | F35-39   | 1           |
 | Lauren Matthews | 2016-10-18 10:01:17+00 | F35-39   | 2           |
 | Desiree Berry   | 2016-10-18 10:05:42+00 | F35-39   | 3           |
 | Suzy Slane      | 2016-10-18 10:06:24+00 | F35-39   | 4           |
 +-----------------+------------------------+----------+-------------*/
```
