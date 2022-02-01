-- <yaml>
-- DependsOn:
--   series: awsdatacatalog.dev_prod_live.performance__expanded_metrics__time_series__raw
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
       datapoints."evg_create_date"         AS "evg_create_date"
       -- <COMMON_ETL_FIELDS>
       , LOCALTIMESTAMP AS "_extract_timestamp"
       -- </COMMON_ETL_FIELDS>
FROM   awsdatacatalog.dev_prod_live.performance__expanded_metrics__time_series__raw    AS series,
       UNNEST(series."data")                                                           AS datapoints
