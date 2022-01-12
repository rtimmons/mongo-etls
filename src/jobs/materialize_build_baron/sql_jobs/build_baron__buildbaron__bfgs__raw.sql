-- This file generated by generate.py.

-- <yaml>
-- DependsOn: {}
-- </yaml>
SELECT  CAST(vs."_id" AS VARCHAR)  AS "_id",
        vs."attributes"            AS "attributes",
        vs."clone_id"              AS "clone_id",
        vs."completion_time"       AS "completion_time",
        vs."events"                AS "events",
        vs."execution"             AS "execution",
        vs."failing_tests"         AS "failing_tests",
        vs."faults"                AS "faults",
        vs."logs"                  AS "logs",
        vs."suggestions"           AS "suggestions",
        vs."task_id"               AS "task_id"
        -- <COMMON_ETL_FIELDS>
        , LOCALTIMESTAMP AS "_extract_timestamp"
        -- </COMMON_ETL_FIELDS>
FROM  "dev_prod_build_baron_atlas"."buildbaron"."bfgs" AS vs

