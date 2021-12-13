-- <yaml>
-- DependsOn:
--   time_series: awsdatacatalog.dev_prod_live.time_series
-- </yaml>

SELECT series."_id"                         AS "series_id",
       series."project"                     AS "project",
       series."task"                        AS "task",
       series."test"                        AS "test",
       series."variant"                     AS "variant",
       series."updatefailures"              AS "updatefailures",
       series."lastsuccessfulupdate"        AS "lastsuccessfulupdate",
       series."_extract_timestamp"          AS "_series_extract_timestamp",
       datapoints."cedar_perf_result_id"    AS "cedar_perf_result_id",
       datapoints."order"                   AS "order",
       datapoints."value"                   AS "value",
       datapoints."version"                 AS "version",
       datapoints."commit"                  AS "commit",
       datapoints."commit_date"             AS "commit_date",
       datapoints."evg_create_date"         AS "evg_create_date",
       LOCALTIMESTAMP                       AS "_extract_timestamp"
FROM   awsdatacatalog.dev_prod_live.time_series    AS series,
       UNNEST(series."data")                       AS datapoints
