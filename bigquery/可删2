https://cloud.google.com/bigquery/docs/reference/standard-sql/range-functions  

---

`GENERATE_RANGE_ARRAY`  
```bq
GENERATE_RANGE_ARRAY(range_to_split, step_interval, include_last_partial_range)
```
```bq
SELECT GENERATE_RANGE_ARRAY(
  RANGE(DATE '2020-01-01', DATE '2020-01-06'),
  INTERVAL 2 DAY,
  TRUE) AS results;

/*----------------------------+
 | results                    |
 +----------------------------+
 | [                          |
 |  [2020-01-01, 2020-01-03), |
 |  [2020-01-03, 2020-01-05), |
 |  [2020-01-05, 2020-01-06)  |
 | ]                          |
 +----------------------------*/
```
```bq
SELECT GENERATE_RANGE_ARRAY(
  RANGE(DATE '2020-01-01', DATE '2020-01-06'),
  INTERVAL 2 DAY,
  FALSE) AS results;

/*----------------------------+
 | results                    |
 +----------------------------+
 | [                          |
 |  [2020-01-01, 2020-01-03), |
 |  [2020-01-03, 2020-01-05)  |
 | ]                          |
 +----------------------------*/
```

---

`RANGE`  
Produces an error if lower_bound is greater than or equal to upper_bound. To return `NULL` instead, add the `SAFE.` prefix to the function name.  
```bq
SELECT RANGE(TIMESTAMP '2022-10-01 14:53:27 America/Los_Angeles',
             TIMESTAMP '2022-10-01 16:00:00 America/Los_Angeles') AS results;

-- Results depend upon where this query was executed.
/*------------------------------------------------------------------+
 | results                                                          |
 +------------------------------------------------------------------+
 | [2022-10-01 21:53:27.000000 UTC, 2022-10-01 23:00:00.000000 UTC) |
 +------------------------------------------------------------------*/
```
```bq
SELECT RANGE(TIMESTAMP '2022-10-01 14:53:27 America/Los_Angeles',
             TIMESTAMP '2022-10-01 16:00:00 America/Los_Angeles') AS results;

-- Results depend upon where this query was executed.
/*------------------------------------------------------------------+
 | results                                                          |
 +------------------------------------------------------------------+
 | [2022-10-01 21:53:27.000000 UTC, 2022-10-01 23:00:00.000000 UTC) |
 +------------------------------------------------------------------*/
```

---

`RANGE_CONTAINS`  
1. Checks if every value in one range is in another range.
```bq
SELECT RANGE_CONTAINS(
  RANGE<DATE> '[2022-01-01, 2023-01-01)',
  RANGE<DATE> '[2022-04-01, 2022-07-01)') AS results;

/*---------+
 | results |
 +---------+
 | TRUE    |
 +---------*/
```
```bq
SELECT RANGE_CONTAINS(
  RANGE(CURRENT_DATE(), DATE('2030-09-01')),
  RANGE(DATE '2025-06-15', DATE '2026-04-15')
) AS results;

/*---------+
 | results |
 +---------+
 | TRUE    |
 +---------*/
```
  
2.  Checks if a value is in a range.
```bq
SELECT RANGE_CONTAINS(
  RANGE<DATE> '[2022-01-01, 2023-01-01)',
  DATE '2022-04-01') AS results;

/*---------+
 | results |
 +---------+
 | TRUE    |
 +---------*/
```

---

`RANGE_END` `RANGE_START`  
Gets the upper/lower bound of a range.  

---

`RANGE_INTERSECT` Gets a segment of two ranges that intersect.  

--- 

`RANGE_OVERLAPS` Checks if two ranges overlap.  

---

`RANGE_SESSIONIZE` Produces a table of sessionized ranges.  skip

