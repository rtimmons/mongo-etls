--
-- Target:
-- awsdatacatalog.dev_prod_live.performance_expanded_metrics_time_series_src
--

SELECT  ts."_id"        AS "_id",
        *,
        LOCALTIMESTAMP  AS "_extract_timestamp"
FROM    dev_prod_performance_atlas.expanded_metrics.time_series AS ts
