-- <yaml>
-- DependsOn: {}
-- </yaml>

SELECT  CAST(ps."_id" AS VARCHAR)   AS "_id",
        ps."info"                   AS "info",
        ps."created_at"             AS "created_at",
        ps."completed_at"           AS "completed_at",
        ps."rollups"                AS "rollups",
        ps."analysis"               AS "analysis"
        -- <COMMON_ETL_FIELDS>
FROM    evergreen_cedar_atlas.cedar.perf_results AS ps
