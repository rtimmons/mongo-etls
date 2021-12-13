from typing import Union, Tuple
import os.path

from mars_util.job_dag import JobDAG
from mars_util.task import PrestoTask
from mars_util.task.destination import PrestoTableDestination

import jobs.whereami

PRESTO_CONN = "920d5dfe-33ba-402a-b3ed-67ba21c25582"


class DagHelper:
    def __init__(self, file_path: str):
        self._tasks = []
        self._file_path = os.path.dirname(file_path)

    def read_file(self, *child_path) -> Tuple[str, str]:
        to_read = jobs.whereami.repo_path(self._file_path, *child_path)
        with open(to_read) as handle:
            return handle.read(), to_read

    def add_task(self, task: Union[PrestoTask, str]) -> PrestoTask:
        if not isinstance(task, PrestoTask):
            task = ConventionalPrestoTask(name=task, helper=self)
        self._tasks.append(task)
        return task

    def extract(self):
        dag = JobDAG()
        dag.register_tasks(list(set(self._tasks)))
        return dag

    def __str__(self):
        out = ["DagHelper("]
        for task in self._tasks:
            out.append(str(task))
            out.append(", ")
        out.append(")")
        return "".join(out)


class ConventionalPrestoTask(PrestoTask):
    def __init__(self, name: str, helper: DagHelper, **other_args):
        self._name = name
        self._helper = helper

        args = {
            "name": name,
            "conn_id": PRESTO_CONN,
            "sql_source": "config",
            "destination": PrestoTableDestination(
                dest_tgt=f"awsdatacatalog.dev_prod_live.{name}",
                dest_replace=True,
                dest_format="PARQUET",
            ),
        }
        if "sql" not in other_args:
            args["sql"], self._sql_path = self._helper.read_file(f"{name}.sql")
        else:
            self._sql_path = "UNKNOWN"
        args.update(other_args)

        super().__init__(**args)
        helper.add_task(self)

    def __str__(self):
        return f"ConventionalPrestoTask({self._name}, sql@{self._sql_path})"