"""Domain model for objects in this repo."""
import importlib
import os
from typing import Any, List, Optional, Set, Union

import yaml
from mars_util.job_dag import JobDAG
from mars_util.task import PrestoTask, Task
from mars_util.task.destination import PrestoTableDestination

from src.jobs import whereami

# The implementation here is a bit shaky. The primary purpose
# is twofold:
#
# 1. Provide the `DagHelper` class used by __mars__ modules.
#    This lets you easily construct MARS DAGs using simple
#    conventions.
# 2. Provide documentation. Starting from a `_Repo` object,
#    you can traverse around the object graph for various
#    MARS and Presto things. Right now this is used to
#    produce a single super verbose markdown document, but
#    future enhancements could make the structure more
#    navigable.
#
# If the below structure doesn't work out long-term that's fine.
#
# There is minimal testing of this code. Mostly only around DagHelper.
# See the test_mars_entry_points.py test. This does only minimal
# traversal of the object graph.


class _Repo:
    """The repository of tasks. Lives in src/jobs."""

    def __init__(self, root: Optional[str] = None):
        """:param root: forced job root defaults to $repo/src/jobs. Useful for testing."""
        if root is None:
            root = whereami.repo_path("src", "jobs")
        self.root = root

    def mars_namespaces(self) -> List["_MarsNamespace"]:
        out = []
        for ent in os.listdir(self.root):
            ent_path = os.path.join(self.root, ent)
            if not os.path.isdir(ent_path):
                continue
            out.append(_MarsNamespace(repo=self, name=ent, dir_path=ent_path))
        return out


class _MarsNamespace:
    """Namespaces are subdirs of the repo e.g. `dev_prod` or `evergreen`."""

    @staticmethod
    def from_file_path(dir_path: str) -> "_MarsNamespace":
        name = os.path.basename(dir_path)
        repo_path = os.path.dirname(dir_path)
        repo = _Repo(repo_path)
        return _MarsNamespace(repo=repo, name=name, dir_path=dir_path)

    def __init__(self, repo: _Repo, name: str, dir_path: str):
        self.repo = repo
        self.name = name
        self.dir_path = dir_path

    def mars_jobs(self) -> List["_MarsJob"]:
        out = []
        for ent in os.listdir(self.dir_path):
            ent_path = os.path.join(self.dir_path, ent)
            if not os.path.isdir(ent_path):
                continue
            out.append(_MarsJob(mars_namespace=self, name=ent, dir_path=ent_path))
        return out


_NAMESPACES = dict()


class _PrestoNamespace:
    """dev_prod_live or evergreen_base. No good way to specify these for now."""

    @staticmethod
    def from_name(name: str) -> "_PrestoNamespace":
        if name not in _NAMESPACES:
            _NAMESPACES[name] = _PrestoNamespace(name=name)
        return _NAMESPACES[name]

    def __init__(self, name: str):
        self.name = name
        self.tables: Set[_PrestoTable] = set()

    def add_table(self, table: "_PrestoTable") -> None:
        self.tables.add(table)


class _MarsJob:
    """A job has many tasks."""

    @staticmethod
    def from_file_path(file_path: str) -> "_MarsJob":
        namespace_dir = os.path.dirname(file_path)
        name = os.path.basename(file_path)
        mars_namespace = _MarsNamespace.from_file_path(namespace_dir)
        return _MarsJob(mars_namespace=mars_namespace, name=name, dir_path=file_path)

    def __init__(self, mars_namespace: _MarsNamespace, name: str, dir_path: str):
        self.mars_namespace = mars_namespace
        self.name = name
        self.dir_path = dir_path
        self.tasks: Set[_MarsJobTask] = set()
        self._helper: Optional[DagHelper] = None

    def add_task(self, task: Union[Task, str], helper: "DagHelper") -> Task:
        task = _MarsJobTask(task=task, mars_job=self, presto_namespace=helper.presto_namespace)
        self.tasks.add(task)
        return task.dag_task()

    def helper(self) -> Any:
        if self._helper is None:
            prefix = self.mars_namespace.repo.root
            split = [
                "src",
                "jobs",
                *self.dir_path[len(prefix) + 1 :].split("/"),  # noqa
                "__mars__",
            ]  # noqa
            module = ".".join(split)
            m = importlib.import_module(module)
            helper: "DagHelper" = m._HELPER  # noqa
            helper.is_from_module(m)
            self._helper = helper
        return self._helper

    def helper_tasks(self) -> List["_MarsJobTask"]:
        return self.helper().mars_job.tasks  # noqa


class _MarsJobTask:
    """
    Do a unit of work e.g. run a SELECT and insert to Presto.

    As we support other task types, we may want to refactor the
    documentation-generation pieces out into independent
    wrappers or helpers.
    """

    def __init__(
        self,
        mars_job: _MarsJob,
        task: Union[Task, str],
        presto_namespace: str,
    ):
        self._mars_job = mars_job

        self._presto_table: Optional[_PrestoTable] = None
        self._sql_file: Optional[_SqlFile]
        if isinstance(task, str):
            self._presto_table = _PrestoTable(
                name=_sanitize_name(task), presto_namespace=presto_namespace, task=self
            )
            self._sql_file = _SqlFile(
                os.path.join(self._mars_job.dir_path, "sql_jobs", f"{task}.sql")
            )

            self._task = PrestoTask(
                name=task,
                conn_id=_PRESTO_CONN,
                sql_source="config",
                sql=self._sql_file.parsed_contents(),
                destination=PrestoTableDestination(
                    dest_tgt=self._presto_table.dest_tgt(),
                    dest_replace=True,
                    dest_format="PARQUET",
                ),
            )
        else:
            self._task = task

    def dag_task(self) -> Task:
        return self._task

    @property
    def name(self) -> str:
        return self._task.name

    @property
    def sql(self) -> Optional[str]:
        if self._sql_file:
            return self._sql_file.parsed_contents()
        else:
            return f"Unknown SQL: {self._task.TASK_TYPE}"

    @property
    def presto_destination(self) -> Optional["_PrestoTable"]:
        return self._presto_table


class _PrestoTable:
    """
    Presto (destination) tables belong to _PrestoNamespaces and
    are populated by means of a _MarsJobTask.
    """

    def __init__(
        self, name: str, presto_namespace: Union[str, _PrestoNamespace], task: _MarsJobTask
    ):
        self.name = name
        if isinstance(presto_namespace, str):
            self.presto_namespace = _PrestoNamespace.from_name(name=presto_namespace)
        else:
            self.presto_namespace = presto_namespace
        self.task = task
        self.presto_namespace.add_table(self)

    def dest_tgt(self) -> str:
        return f"awsdatacatalog.{self.presto_namespace.name}.{self.name}"


_PRESTO_CONN = "920d5dfe-33ba-402a-b3ed-67ba21c25582"
# ↑ Would be nice to doc this.


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

    def __init__(
        self,
        file_path: str,
        presto_namespace: Optional[str] = None,
        mars_job: Optional[_MarsJob] = None,
    ):
        """
        :param file_path:
            The `__file__` value from the `__mars__.py` file creating this object.
        :param presto_namespace:
            In which presto namespace should the results of queries be to. Default
            is "dev_prod_live" where most raw and view data live.
        :param mars_job:
            The MARS job name that owns this helper. This is used primarily in other
            discovery mechanisms where we want to e.g. find the job that begot a table,
            and this parameter is passed in when doing these kinds of "reverse lookups".
            If not specified, the file path and directory structure will be used to figure
            this out. If the `__mars__.py` file is in folder X, we will
            assume the mars_job is X.
        """
        self._file_path = os.path.dirname(file_path)
        self.presto_namespace = "dev_prod_live" if not presto_namespace else presto_namespace
        if not mars_job:
            mars_job = _MarsJob.from_file_path(self._file_path)
        self.mars_job = mars_job
        self.doc: str = ""

    def add_task(self, task: Union[Task, str]) -> Task:
        """
        :param task:
            Either a pre-formed MARS Task or a string representing
            a file in sql_jobs that will be used to populate the Presto
            table with the same name.
        :return
            The generated task. Use this to add dependencies or otherwise
            interact with it using the MARS dag object primitives.
        """
        return self.mars_job.add_task(task=task, helper=self)

    def extract(self) -> JobDAG:
        """
        :return: The JobDag that includes all tasks created or passed into add_task.
        """
        dag = JobDAG()
        for task in self.mars_job.tasks:
            dag.register_tasks([task.dag_task()])
        return dag

    def is_from_module(self, mod: Any) -> None:
        """Indicate the containing __mars__ module."""
        self.doc = getattr(mod, "__doc__", "")


# TODO: this is to work around DP-1894
def _sanitize_name(name: str) -> str:
    return name.replace("-", "_")


_COMMENT_START = "-- "


class _SqlFile:
    def __init__(self, path: str):
        self.path = path

    def contents_lines(self) -> List[str]:
        with open(self.path, "r") as handle:
            return [line.rstrip() for line in handle.readlines()]

    def contents(self) -> str:
        return "\n".join(self.contents_lines())

    def parsed_lines(self) -> List[str]:
        return [line for line in self.contents_lines()]

    def parsed_contents(self) -> str:
        return "\n".join(self.parsed_lines())

    def front_matter(self) -> dict:
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


def _prefix_lines(paragraph: str, prefix: str) -> str:
    return "\n".join(f"{prefix}{line}" for line in paragraph.split("\n"))


def _table_ize(mapping: dict) -> None:
    longest = max(len(k) for k in mapping.keys())
    for k, v in mapping.items():
        print(f"- {k}: {' '*(longest-len(k))} {v}")


def print_docs_markdown() -> None:
    """Print documentation for all tasks."""
    repo = _Repo()
    for namespace in repo.mars_namespaces():
        print(f"# MARS Namespace: `{namespace.name}`\n")

        jobs = namespace.mars_jobs()
        if jobs:
            print("Jobs:\n")
            for job in jobs:
                print(f"- `{job.name}`")
            print()

        for job in jobs:
            print(f"## MARS Job: `{namespace.name}`.`{job.name}`")

            if job.helper().doc:
                print(job.helper().doc)

            print("\nTasks:\n")
            for task in job.helper_tasks():
                print(f"- `{task.name}`")
            print()

            for task in job.helper_tasks():
                print(f"### Job Task: `{namespace.name}`.`{job.name}`.`{task.name}`")
                metadata = {"MARS Namespace": f"`{namespace.name}`", "MARS Job": f"`{job.name}`"}
                dest = task.presto_destination
                if dest:
                    if dest.presto_namespace:
                        metadata["Destination Target"] = f"`{dest.dest_tgt()}`"
                        metadata["Destination Presto Namespace"] = f"`{dest.presto_namespace.name}`"
                    metadata["Destination Table"] = f"`{dest.name}`"
                print()
                _table_ize(metadata)
                if task.sql:
                    print(f"\nSQL:\n\n{_prefix_lines(task.sql,'    ')}\n")
