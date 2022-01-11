"""
By convention we expose the _DAG object in a __mars__.py file.
"""

from src.jobs.helpers import DagHelper

helper = DagHelper(__file__)

cedar__cedar__buildlogs__raw = helper.add_task("cedar__cedar__buildlogs__raw")
cedar__cedar__historical_test_data__raw = helper.add_task("cedar__cedar__historical_test_data__raw")
cedar__cedar__system_metrics__raw = helper.add_task("cedar__cedar__system_metrics__raw")


_DAG = helper.extract()
