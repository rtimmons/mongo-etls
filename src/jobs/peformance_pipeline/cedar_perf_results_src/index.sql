--
-- Target:
-- awsdatacatalog.dev_prod_live.cedar_perf_results_src
--

SELECT  ps."_id"            AS "_id",
        ps."info"           AS "info",
        ps."created_at"     AS "created_at",
        ps."completed_at"   AS "completed_at",
        ps."rollups"        AS "rollups",
        ps."analysis"       AS "analysis",
        LOCALTIMESTAMP      AS "_extract_timestamp"
FROM    evergreen_cedar_atlas.cedar.perf_results as ps
