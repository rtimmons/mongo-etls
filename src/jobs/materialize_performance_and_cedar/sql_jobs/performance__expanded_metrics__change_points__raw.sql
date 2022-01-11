-- This file generated by generate.py.

-- <yaml>
-- DependsOn: {}
-- </yaml>
SELECT  CAST(vs."_id" AS VARCHAR)  AS "_id",
        vs."algorithm"             AS "algorithm",
        vs."calculated_on"         AS "calculated_on",
        vs."cedar_perf_result_id"  AS "cedar_perf_result_id",
        vs."order"                 AS "order",
        vs."percent_change"        AS "percent_change",
        vs."time_series_info"      AS "time_series_info",
        vs."triage"                AS "triage",
        vs."version"               AS "version"
        -- <COMMON_ETL_FIELDS>
        , LOCALTIMESTAMP AS "_extract_timestamp"
        -- </COMMON_ETL_FIELDS>
FROM  dev_prod_performance_atlas.expanded_metrics.change_points AS vs

