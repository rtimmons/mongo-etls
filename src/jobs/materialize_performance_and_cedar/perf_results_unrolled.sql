-- <yaml>
-- DependsOn:
--   perf_results: awsdatacatalog.dev_prod_live.cedar_perf_results_src
-- </yaml>

SELECT  ps."_id"                    AS "perf_result_id",
        ps."info"                   AS "perf_result_info",
        ps."created_at"             AS "perf_result_created_at",
        ps."completed_at"           AS "perf_result_completed_at",
        ps."_extract_timestamp"     AS "_perf_result_extract_timestamp",
        ps.rollups."processed_at"   AS "rollup_processed_at",
        ps.rollups."count"          AS "rollups_count",
        ps.rollups."valid"          AS "rollups_valid",
        ps."analysis"               AS "rollups_analysis",
        stats."name"                AS "stat_name",
        stats."val"                 AS "stat_value"
        -- <COMMON_ETL_FIELDS>
FROM    awsdatacatalog.dev_prod_live.cedar_perf_results_src AS ps,
        UNNEST(ps.rollups."stats")                          AS stats
