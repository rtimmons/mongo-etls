"""Parser for MARS job configurations"""

import json
from typing import Dict, List

import mars_util.task as task
import mars_util.task.destination as dest
from jinja2 import Template
from mars_util.job_dag import JobDAG
from mars_util.task.task import Condition

_tasks = {
    task.AlertTask.TASK_TYPE: task.AlertTask,
    task.BigQueryTask.TASK_TYPE: task.BigQueryTask,
    task.GlueTask.TASK_TYPE: task.GlueTask,
    task.KubernetesTask.TASK_TYPE: task.KubernetesTask,
    task.MongoDBTask.TASK_TYPE: task.MongoDBTask,
    task.NightwatchTask.TASK_TYPE: task.NightwatchTask,
    task.PrestoTask.TASK_TYPE: task.PrestoTask,
    task.PythonTask.TASK_TYPE: task.PythonTask,
    task.TableauTask.TASK_TYPE: task.TableauTask,
}

_destinations = {
    "bigquery_table": dest.BigQueryTableDestination,
    "bigquery_view": dest.BigQueryViewDestination,
    "email": dest.EmailDestination,
    "gsheet": dest.GSheetDestination,
    "mongodb": dest.MongoDBDestination,
    "presto_bigquery": dest.PrestoToBigQueryDestination,
    "presto_ext_table": dest.PrestoExtTableDestination,
    "presto_insert": dest.PrestoInsertDestination,
    "presto_s3": dest.PrestoS3Destination,
    "presto_table": dest.PrestoTableDestination,
    "presto_view": dest.PrestoViewDestination,
    "s3_export": dest.S3ExportDestination,
}

_conditions = {
    "on_completion": Condition.ON_COMPLETION,
    "on_failure": Condition.ON_FAILURE,
    "on_success": Condition.ON_SUCCESS,
}

_TASK_NAME_KEY = "name"
_TASK_TYPE_KEY = "type"
_TASK_DESTINATION_KEY = "destination"
_TASK_CHILDREN_KEY = "children"
_DESTINATION_TYPE_KEY = "type"


def parse_job_config(file_path: str, variables: Dict[str, str] = None) -> JobDAG:
    """
    Parse the given MARS job configuration and create the corresponding JobDAG
    object.
    :param file_path:
        The file path containing the JSON formatted job configuration.
    :param variables:
        A set of variables for jinja template rendering of the configuration.
        If none passed in, template rendering will not take place.
    :return:
        The JobDAG object with the generated Task objects from the job
        configuration.
    """
    with open(file_path, "r") as f:
        job_config_str = f.read()
        if variables is not None:
            job_config_str = Template(
                job_config_str, variable_start_string="[@dag-eval", variable_end_string="@]"
            ).render(variables)
    job_config = json.loads(job_config_str)

    task_map = {
        task_config[_TASK_NAME_KEY]: _parse_task_config(task_config) for task_config in job_config
    }
    _add_children(task_map, job_config)

    dag = JobDAG()
    dag.register_tasks(task_map.values())
    valid, err_msg = dag.is_valid()
    if not valid:
        raise ValueError(f"invalid JobDAG: {err_msg}")

    return dag


def _parse_task_config(task_config: dict) -> task.Task:
    if _TASK_DESTINATION_KEY in task_config:
        dest_config = task_config[_TASK_DESTINATION_KEY]
        task_config[_TASK_DESTINATION_KEY] = _destinations[dest_config[_DESTINATION_TYPE_KEY]](
            **dest_config
        )

    return _tasks[task_config[_TASK_TYPE_KEY]](**task_config)


def _add_children(task_map: Dict[str, task.Task], job_config: List[dict]) -> None:
    for task_config in job_config:
        if _TASK_CHILDREN_KEY not in task_config:
            continue

        for child_name, condition in task_config[_TASK_CHILDREN_KEY].items():
            parent = task_map[task_config[_TASK_NAME_KEY]]
            child = task_map[child_name]
            parent.set_next(child, _conditions[condition])
