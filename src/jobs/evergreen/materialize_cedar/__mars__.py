"""
By convention we expose the _DAG object in a __mars__.py file.
"""

from src.jobs.model import DagHelper

_HELPER = DagHelper(__file__, presto_namespace="evergreen_base")


cedar__cedar__perf_results__raw = _HELPER.add_task("cedar__cedar__perf_results__raw")
cedar__cedar__perf_results__unrolled_intermediate = _HELPER.add_task(
    "cedar__cedar__perf_results__unrolled_intermediate"
)
cedar__cedar__perf_results__unrolled_intermediate.set_prev(cedar__cedar__perf_results__raw)

cedar__cedar__test_results__raw = _HELPER.add_task("cedar__cedar__test_results__raw")


_DAG = _HELPER.extract()
