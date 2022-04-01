WITH "sans_average" AS (
    SELECT  ls."project"                                            AS "project",
            ls."variant"                                            AS "variant",
            ls."task_name"                                          AS "task_name",
            COALESCE(rs."display_test_name", rs."test_name")        AS "test_name",
            ls."request_type"                                       AS "request_type",
            ls."task_create_iso"                                    AS "task_create_iso",
            SUM(IF(rs."status" IN ('pass'              ), 1, 0))    AS "num_pass",
            SUM(IF(rs."status" IN ('fail', 'silentfail'), 1, 0))    AS "num_fail",
            SUM(IF(rs."status" IN ('pass'),
                   TO_MILLISECONDS(rs."test_end_time" - rs."test_start_time")*1e6,
                   0))                                              AS "total_pass_duration_ns"
    FROM    "awsdatacatalog"."{{ get_value_from_variable('schema_name') }}"."cedar_test_results_landing"  AS "ls",
            UNNEST("results")                                                                             AS "rs"
    WHERE   1=1
    AND     "task_create_iso" = TO_ISO8601(DATE(TIMESTAMP '{{ get_value_from_ctx("start_time") }}') - INTERVAL '1' DAY)
    GROUP BY 1, 2, 3, 4, 5, 6
)
SELECT  "project"                                                      AS "project",
        "variant"                                                      AS "variant",
        "task_name"                                                    AS "task_name",
        "test_name"                                                    AS "test_name",
        "request_type"                                                 AS "request_type",
        date("task_create_iso")                                        AS "date",
        "num_pass"                                                     AS "num_pass",
        "num_fail"                                                     AS "num_fail",
        IF("num_pass" <> 0, "total_pass_duration_ns"/"num_pass", 0)    AS "average_duration"
        -- <COMMON_ETL_FIELDS>
        , LOCALTIMESTAMP AS "_extract_timestamp"
        -- </COMMON_ETL_FIELDS>
FROM "sans_average"
