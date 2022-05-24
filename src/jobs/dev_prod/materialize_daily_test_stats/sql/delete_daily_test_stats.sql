DELETE FROM "awsdatacatalog"."{{ get_value_from_variable('schema_name') }}"."results__daily_test_stats__intermediate"
WHERE "task_create_iso" = TO_ISO8601(DATE(TIMESTAMP '{{ get_value_from_ctx("start_time") }}') - INTERVAL '1' DAY)
 
