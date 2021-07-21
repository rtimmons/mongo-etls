

Presto task type destinations:

* view -- creates a view, views are logical table and doesn't actually create physical data underneath
* table -- creates a table using default schema-level storage configuration. So if you create a table in your team's schema, data is automatically managed by presto in your team's bucket. This is the recommended option if you want to create tables
* external_table -- creates a table with explicit storage location, so you can point to anywhere on the S3 storage structure for presto to base its table off of. When you drop an external table, data is not deleted, so this option requires more manual management. Not so recommended.
* Insert -- Inserts your query result to the table. Presto handles insertion of records in this case. The table needs to exist already and shall have compatible schema as your query result.

Notes:

* queries (sql files) cannot end with semicolons
* if you set dest as a table it creates with a syntax like `CREATE TABLE awsdatacatalog.dev_prod_metrics_v1.performance_change_points_raw WITH (format = 'PARQUET') AS <the sql>`
