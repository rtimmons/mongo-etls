CALL system.sync_partition_metadata(
  schema_name=>'{{ get_value_from_variable("schema_name") }}',
  table_name=>'cedar_test_results_landing',
  mode=>'ADD'
)
