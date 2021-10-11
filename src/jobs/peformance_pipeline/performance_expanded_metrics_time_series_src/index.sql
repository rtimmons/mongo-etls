--
-- Target:
-- awsdatacatalog.dev_prod_live.performance_expanded_metrics_time_series_src
--

SELECT  "_id"                     AS "_id",
        "measurement"             AS "measurement",
        "project"                 AS "project",
        "task"                    AS "task",
        "test"                    AS "test",
        "variant"                 AS "variant",
        "data"                    AS "data",
        "updatefailures"          AS "updatefailures",
        "lastsuccessfulupdate"    AS "lastsuccessfulupdate",
        "lastupdateattempt"       AS "lastupdateattempt",
        LOCALTIMESTAMP            AS "_extract_timestamp"
FROM dev_prod_performance_atlas.expanded_metrics.time_series
