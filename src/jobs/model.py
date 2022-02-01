"""Domain model for objects in this repo."""
import importlib
import os
from typing import List, Optional, Set, Union

import yaml
from mars_util.job_dag import JobDAG
from mars_util.task import PrestoTask, Task
from mars_util.task.destination import PrestoTableDestination

from src.jobs import whereami


class _Repo:
    """The repository of tasks. Lives in src/jobs."""

    def __init__(self, root: Optional[str] = None):
        """:param root: forced job root defaults to $repo/src/jobs. Useful for testing."""
        if root is None:
            root = whereami.repo_path("src", "jobs")
        self.root = root

    def mars_namespaces(self) -> List["_MarsNamespace"]:
        """Namespaces are subdirs of the repo e.g. `dev_prod` or `evergreen`."""
        out = []
        for ent in os.listdir(self.root):
            ent_path = os.path.join(self.root, ent)
            if not os.path.isdir(ent_path):
                continue
            out.append(_MarsNamespace(repo=self, name=ent, dir_path=ent_path))
        return out


class _MarsNamespace:
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


class _PrestoNamespace:
    def __init__(self, name: str):
        self.name = name


class _MarsJob:
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

    def add_task(self, task: Union[None, Task, str], helper: "DagHelper") -> Task:
        task = _MarsJobTask(task=task, mars_job=self, presto_namespace=helper.presto_namespace)
        self.tasks.add(task)
        return task.dag_task()

    def helper_tasks(self) -> List["_MarsJobTask"]:
        prefix = self.mars_namespace.repo.root
        split = ["src", "jobs", *self.dir_path[len(prefix) + 1 :].split("/"), "__mars__"]  # noqa
        module = ".".join(split)
        m = importlib.import_module(module)
        helper: "DagHelper" = m._HELPER  # noqa
        return helper.mars_job.tasks  # noqa


class _MarsJobTask:
    def __init__(
        self,
        mars_job: _MarsJob,
        task: Union[None, Task, str],
        presto_namespace: Optional[str] = None,
    ):
        self._mars_job = mars_job
        self._task = task

        self._presto_table: Optional[_PrestoTable] = None
        self._sql_file: Optional[_SqlFile]
        if isinstance(self._task, str):
            self._presto_table = _PrestoTable(
                name=_sanitize_name(self._task), presto_namespace=presto_namespace
            )
            self._sql_file = _SqlFile(
                os.path.join(self._mars_job.dir_path, "sql_jobs", f"{task}.sql")
            )

            self._task = PrestoTask(
                name=self._task,
                conn_id=_PRESTO_CONN,
                sql_source="config",
                sql=self._sql_file.parsed_contents(),
                destination=PrestoTableDestination(
                    dest_tgt=self._presto_table.dest_tgt,
                    dest_replace=True,
                    dest_format="PARQUET",
                ),
            )

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
    def __init__(self, name: str, presto_namespace: Union[str, _PrestoNamespace]):
        self.name = name
        if isinstance(presto_namespace, str):
            presto_namespace = _PrestoNamespace(name=presto_namespace)
        self.presto_namespace = presto_namespace

    def dest_tgt(self):
        return f"awsdatacatalog.{self.presto_namespace.name}.{self.name}"


_PRESTO_CONN = "920d5dfe-33ba-402a-b3ed-67ba21c25582"


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
        mars_job: Optional[_MarsJob] = None,
        presto_namespace: Optional[str] = None,
    ):
        """:param file_path: the __file__ value from the __mars__ file."""
        self._file_path = os.path.dirname(file_path)
        self.presto_namespace = "dev_prod_live" if not presto_namespace else presto_namespace
        if not mars_job:
            mars_job = _MarsJob.from_file_path(self._file_path)
        self.mars_job = mars_job

    def add_task(self, task: Union[None, Task, str]) -> Task:
        """
        :param task: TODO
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


def _table_ize(mapping: dict):
    longest = max(len(k) for k in mapping.keys())
    for k, v in mapping.items():
        print(f"- {k}: {' '*(longest-len(k))} {v}")


def _main() -> None:
    repo = _Repo()
    for namespace in repo.mars_namespaces():
        print(f"# MARS Namespace: `{namespace.name}`\n")
        for job in namespace.mars_jobs():
            print(f"## MARS Job: `{job.name}`")
            print(f"\nTasks:\n")
            for task in job.helper_tasks():
                print(f"- {task.name}")
            print()
            for task in job.helper_tasks():
                print(f"### Job Task: `{task.name}`")
                metadata = {"MARS Namespace": f"`{namespace.name}`", "MARS Job": f"`{job.name}`"}
                dest = task.presto_destination
                if dest:
                    metadata["Destination Presto Namespace"] = f"`{dest.presto_namespace.name}`"
                    metadata["Destination Table"] = f"`{dest.name}`"
                print()
                _table_ize(metadata)
                print(f"\nSQL:\n\n{_prefix_lines(task.sql,'    ')}\n")


if __name__ == "__main__":
    _main()
