"""
Helpers and wrappers that make usages of mars_util more consistent.
"""
import os.path
from typing import Any, List, Optional, Union

import yaml
from mars_util.job_dag import JobDAG
from mars_util.task import PrestoTask
from mars_util.task.destination import PrestoTableDestination

import src.jobs.whereami

PRESTO_CONN = "920d5dfe-33ba-402a-b3ed-67ba21c25582"


class DagHelper:
    """
    Convenience APIs to create MARS DAG graphs.

    Intended to be invoked via

        _HELPER = DagHelper(__file__)
        ....
        _DAG = _HELPER.extract()

    Pass in the `__file__` value so paths in the helper can be simplified
    to the directory of the __mars__ file itself.
    """

    def __init__(self, file_path: str):
        """:param file_path: path to file where subsequent `read_file`, `add_task`, etc. will look."""
        self._tasks: List[PrestoTask] = []
        self._file_path = os.path.dirname(file_path)

    def read_file(self, *child_path: str) -> "_SqlFile":
        """
        :param child_path:
            Sub-path rooted at dirname of file passed into ctor. E.g. sql_jobs/foo.sql.
            Throws an exception if the indicated file is not found.
        :return: the SqlFile representation.
        """
        path = src.jobs.whereami.repo_path(self._file_path, *child_path)
        return _SqlFile([path])

    def add_task(self, task: Union[PrestoTask, str]) -> PrestoTask:
        """
        Add a new or generated PrestoTask.

        :param task:
            If given a PrestoTask will add to the internal task registry as-is.

            If given a string, will create a conventional Presto task that assumes

            1. The source sql is located at sql_jobs/{task}.sql
            2. The destination is a parquet table in dev_prod_live.
               The destination table's name is 'task' (with - replaced with _)
        :return
            The generated (or passed-in) task. Use this to add dependencies or otherwise
            interact with it using the MARS dag object primitives.
        """
        if not isinstance(task, PrestoTask):
            task = _ConventionalPrestoTask(name=task, helper=self)
        self._tasks.append(task)
        return task

    def extract(self) -> JobDAG:
        """
        :return: The JobDag that includes all tasks created or passed into add_task.
        """
        dag = JobDAG()
        dag.register_tasks(list(set(self._tasks)))
        return dag

    def __str__(self) -> str:
        out = ["DagHelper("]
        for task in self._tasks:
            out.append(str(task))
            out.append(", ")
        out.append(")")
        return "".join(out)


# TODO: this is to work around DP-1894
def _sanitize_name(name: str) -> str:
    return name.replace("-", "_")


class _ConventionalPrestoTask(PrestoTask):
    def __init__(self, name: str, helper: DagHelper, **other_args: Any):
        self._name = name
        self._helper = helper

        dest_name = _sanitize_name(name)
        args = {
            "name": name,
            "conn_id": PRESTO_CONN,
            "sql_source": "config",
            "destination": PrestoTableDestination(
                dest_tgt=f"awsdatacatalog.dev_prod_live.{dest_name}",
                dest_replace=True,
                dest_format="PARQUET",
            ),
        }
        self._sql_file: Optional[_SqlFile] = None
        if "sql" not in other_args:
            self._sql_file = self._helper.read_file("sql_jobs", f"{name}.sql")
            args["sql"] = self._sql_file.parsed_contents()
        else:
            self._sql_file = None
        args.update(other_args)

        super().__init__(**args)
        helper.add_task(self)

    def __str__(self) -> str:
        return f"ConventionalPrestoTask({self._name}, {self._sql_file})"


_COMMENT_START = "-- "


# This started as an external class (used in __mars__.py files) but ended up only
# being needed in here. Perhaps refactor.
class _SqlFile:
    def __init__(self, path: Union[List[str], str]):
        if isinstance(path, str):
            self._contents: Optional[str] = path
            self.path = None
        else:
            self.path = src.jobs.whereami.repo_path(*path)
            self._contents = None

    def location(self) -> str:
        return self.path if self.path else "InlineContents"

    def __str__(self) -> str:
        return f"SQLFile:{self.parsed_contents()}@{self.location()}"

    def contents_lines(self) -> List[str]:
        if self._contents:
            out = self._contents.split("\n")
            return out
        assert self.path is not None
        with open(self.path, "r") as handle:
            return [line.rstrip() for line in handle.readlines()]

    def contents(self) -> str:
        return "\n".join(self.contents_lines())

    def parsed_lines(self) -> List[str]:
        return [line for line in self.contents_lines()]

    def parsed_contents(self) -> str:
        return "\n".join(self.parsed_lines())

    def front_matter(self) -> dict:
        # TODO: the <yaml> thing is a bit hokey and not really supported
        yaml_lines = []
        for line in self.contents_lines():
            line = line.rstrip()
            if not line.startswith(_COMMENT_START):
                break

            # "-- <yaml>" -> "<yaml>":
            contents = line[len(_COMMENT_START) :]  # noqa (pep8-E203 vs black)

            if contents.startswith("<yaml>"):
                continue
            if contents.startswith("</yaml>"):
                break
            yaml_lines.append(contents)
        if len(yaml_lines) > 0:
            to_parse = "\n".join(yaml_lines)
            return yaml.safe_load(to_parse)
        return dict()
