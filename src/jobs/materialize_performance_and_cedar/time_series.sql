-- <yaml>
-- DependsOn: {}
-- </yaml>

SELECT  CAST(ts."_id" AS VARCHAR)    AS "_id",
        ts."measurement"             AS "measurement",
        ts."project"                 AS "project",
        ts."task"                    AS "task",
        ts."test"                    AS "test",
        ts."variant"                 AS "variant",
        ts."data"                    AS "data",
        ts."updatefailures"          AS "updatefailures",
        ts."lastsuccessfulupdate"    AS "lastsuccessfulupdate",
        ts."lastupdateattempt"       AS "lastupdateattempt",
        LOCALTIMESTAMP               AS "_extract_timestamp"
FROM dev_prod_performance_atlas.expanded_metrics.time_series AS ts
