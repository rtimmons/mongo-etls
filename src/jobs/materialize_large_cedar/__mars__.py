"""
By convention we expose the _DAG object in a __mars__.py file.
"""

from src.jobs.helpers import DagHelper

_HELPER = DagHelper(__file__)

cedar__cedar__buildlogs__raw = _HELPER.add_task("cedar__cedar__buildlogs__raw")
cedar__cedar__historical_test_data__raw = _HELPER.add_task("cedar__cedar__historical_test_data__raw")
cedar__cedar__system_metrics__raw = _HELPER.add_task("cedar__cedar__system_metrics__raw")
cedar__cedar__test_results__raw = _HELPER.add_task("cedar__cedar__test_results__raw")


_DAG = _HELPER.extract()
