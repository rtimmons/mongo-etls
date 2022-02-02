-- This file generated by generate.py.

-- <yaml>
-- DependsOn: {}
-- </yaml>
SELECT  CAST(vs."_id" AS VARCHAR)  AS "_id",
        vs."data"                  AS "data",
        vs."lastsuccessfulupdate"  AS "lastsuccessfulupdate",
        vs."lastupdateattempt"     AS "lastupdateattempt",
        vs."measurement"           AS "measurement",
        vs."project"               AS "project",
        vs."task"                  AS "task",
        vs."test"                  AS "test",
        vs."updatefailures"        AS "updatefailures",
        vs."variant"               AS "variant"
        -- <COMMON_ETL_FIELDS>
        , LOCALTIMESTAMP AS "_extract_timestamp"
        -- </COMMON_ETL_FIELDS>
FROM  "dev_prod_performance_atlas"."expanded_metrics"."time_series" AS vs

