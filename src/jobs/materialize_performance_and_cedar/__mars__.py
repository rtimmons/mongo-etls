"""
By convention we expose the _DAG object in a __mars__.py file.
"""

from mars_util.job_dag import JobDAG
from mars_util.task import PrestoTask
from mars_util.task.destination import PrestoTableDestination

import src.task_helpers as helpers


PRESTO_CONN = "920d5dfe-33ba-402a-b3ed-67ba21c25582"


perf_results = PrestoTask(
    name="perf_results",
    conn_id=PRESTO_CONN,
    sql_source="config",
    sql=helpers.read_file("src", "jobs", "materialize_performance_and_cedar", "perf_results.sql"),
    destination=PrestoTableDestination(
        dest_tgt="awsdatacatalog.dev_prod_live.perf_results",
        dest_replace=True,
        dest_format="table",
    )
)
perf_results_unrolled = PrestoTask(
    name="perf_results_unrolled",
    conn_id=PRESTO_CONN,
    sql_source="config",
    sql=helpers.read_file("src", "jobs", "materialize_performance_and_cedar", "perf_results_unrolled.sql"),
    destination=PrestoTableDestination(
        dest_tgt="awsdatacatalog.dev_prod_live.perf_results_unrolled",
        dest_replace=True,
        dest_format="table",
    )
)
# DependsOn
perf_results_unrolled.set_prev(perf_results)


time_series = PrestoTask(
    name="time_series",
    conn_id=PRESTO_CONN,
    sql_source="config",
    sql=helpers.read_file("src", "jobs", "materialize_performance_and_cedar", "time_series.sql"),
    destination=PrestoTableDestination(
        dest_tgt="awsdatacatalog.dev_prod_live.time_series",
        dest_replace=True,
        dest_format="table",
    )
)
time_series_unrolled = PrestoTask(
    name="time_series_unrolled",
    conn_id=PRESTO_CONN,
    sql_source="config",
    sql=helpers.read_file("src", "jobs", "materialize_performance_and_cedar", "time_series_unrolled.sql"),
    destination=PrestoTableDestination(
        dest_tgt="awsdatacatalog.dev_prod_live.time_series_unrolled",
        dest_replace=True,
        dest_format="table",
    )
)
# DependsOn
time_series_unrolled.set_prev(time_series)

dag = JobDAG()
dag.register_tasks([
    perf_results,
    perf_results_unrolled,
    time_series,
    time_series_unrolled
])
_DAG = dag

