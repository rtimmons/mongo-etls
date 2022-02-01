import importlib
import os
from typing import Optional, List, Union, Any

import yaml
from mars_util.job_dag import JobDAG
from mars_util.task import PrestoTask
from mars_util.task.destination import PrestoTableDestination

from src.jobs import whereami


class Repo:
    def __init__(self, root: Optional[str] =None):
        if root is None:
            root = whereami.repo_path("src", "jobs")
        self.root = root

    def mars_namespaces(self) -> List["MarsNamespace"]:
        out = []
        for ent in os.listdir(self.root):
            ent_path = os.path.join(self.root, ent)
            if not os.path.isdir(ent_path):
                continue
            out.append(MarsNamespace(repo=self, name=ent, dir_path=ent_path))
        return out


class MarsNamespace:
    def __init__(self, repo: Repo, name: str, dir_path: str):
        self.repo = repo
        self.name = name
        self.dir_path = dir_path

    def mars_jobs(self) -> List["MarsJob"]:
        out = []
        for ent in os.listdir(self.dir_path):
            ent_path = os.path.join(self.dir_path, ent)
            if not os.path.isdir(ent_path):
                continue
            out.append(MarsJob(mars_namespace=self,
                               name=ent, dir_path=ent_path))
        return out


class PrestoNamespace:
    pass


class MarsJob:
    def __init__(self, mars_namespace: MarsNamespace, name: str,
                 dir_path: str):
        self.mars_namespace = mars_namespace
        self.name = name
        self.dir_path = dir_path

    def tasks(self) -> List["MarsJobTask"]:
        prefix = self.mars_namespace.repo.root
        split = ["src", "jobs", *self.dir_path[len(prefix)+1:].split("/"), "__mars__"]
        module = ".".join(split)
        m = importlib.import_module(module)
        helper: "DagHelper" = m._HELPER
        return helper._tasks


class MarsJobTask:
    def __init__(self, mars_job: MarsJob, helper: "DagHelper"):
        self.helper = helper


class PrestoTable:
    pass


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

    def __init__(self, file_path: str, namespace: Optional[str] = None):
        """
        :param file_path:
            path to file where subsequent `read_file`, `add_task`, etc. will look.
        :param namespace:
            To which Presto namespace should destination tables belong.
            Default is "dev_prod_live".
        """
        self._tasks: List[PrestoTask] = []
        self._file_path = os.path.dirname(file_path)

        if namespace is None:
            namespace = "dev_prod_live"
        self._namespace = namespace

    @property
    def namespace(self) -> str:
        """:return To which Presto namespace should destination tables belong."""
        return self._namespace

    def read_file(self, *child_path: str) -> "_SqlFile":
        """
        :param child_path:
            Sub-path rooted at dirname of file passed into ctor. E.g. sql_jobs/foo.sql.
            Throws an exception if the indicated file is not found.
        :return: the SqlFile representation.
        """
        path = whereami.repo_path(self._file_path, *child_path)
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
                dest_tgt=f"awsdatacatalog.{helper.namespace}.{dest_name}",
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


class _SqlFile:
    def __init__(self, path: Union[List[str], str]):
        if isinstance(path, str):
            self._contents: Optional[str] = path
            self.path = None
        else:
            self.path = whereami.repo_path(*path)
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


def _main():
    repo = Repo()
    for namespace in repo.mars_namespaces():
        print(f"# {namespace.name}")
        for job in namespace.mars_jobs():
            print(f"## {job.name}")
            for task in job.tasks():
                print(f"- {task}")


if __name__ == "__main__":
    _main()
