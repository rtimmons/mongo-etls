-- TODO: The buildlogs table is too large to materialize in the 7h time limit imposed by MARS.
--       We need to have an effective base+delta strategy here.

-- <yaml>
-- DependsOn: {}
-- </yaml>
SELECT  CAST(vs."_id" AS VARCHAR)  AS "_id",
        vs."artifact"              AS "artifact",
        vs."completed_at"          AS "completed_at",
        vs."created_at"            AS "created_at",
        vs."info"                  AS "info"
        -- <COMMON_ETL_FIELDS>
        , LOCALTIMESTAMP AS "_extract_timestamp"
        -- </COMMON_ETL_FIELDS>
        , 'EXAMPLE DATA ONLY' AS "crude_commentary"
FROM  "evergreen_cedar_atlas"."cedar"."buildlogs" AS vs
LIMIT 1000

