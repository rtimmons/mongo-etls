"""
By convention we expose the _DAG object in a __mars__.py file.
"""

from mars_util.job_dag import JobDAG

from jobs.helpers import ConventionalPrestoTask

perf_results = ConventionalPrestoTask(
    name="perf_results",
    file_path=__file__,
)
perf_results_unrolled = ConventionalPrestoTask(
    name="perf_results_unrolled",
    file_path=__file__,
)
# DependsOn
perf_results_unrolled.set_prev(perf_results)


time_series = ConventionalPrestoTask(
    name="time_series",
    file_path=__file__,
)
time_series_unrolled = ConventionalPrestoTask(
    name="time_series_unrolled",
    file_path=__file__,
)
# DependsOn
time_series_unrolled.set_prev(time_series)

dag = JobDAG()
dag.register_tasks(
    [perf_results, perf_results_unrolled, time_series, time_series_unrolled]
)
_DAG = dag
