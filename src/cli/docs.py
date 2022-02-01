"""
Render documentation website.
"""
import importlib
import os
import os.path

from src.jobs.model import DagHelper
from src.jobs import whereami
from typing import Any, List


class HelperDoc:
    def __init__(self, job_doc: "JobDoc", helper: DagHelper):
        self.helper = helper
        self.job_doc = job_doc

    def render(self) -> List[str]:
        if not self.helper:
            return []
        return ["Helper"]


class JobDoc:
    def __init__(self, name: str, module: Any):
        self._name = name
        self._module = module

    def render(self) -> List[str]:
        helper = HelperDoc(job_doc=self, helper=getattr(self._module, "_HELPER", None))
        out = [
            f"# {self._name}",
            "\n\n",
            self._module.__doc__
        ]
        if helper:
            out.extend(helper.render())
        return out


def gather_job_docs() -> List[JobDoc]:
    out = []
    root_path = whereami.repo_path("src", "jobs")  # /home/foo/Projects/mongo-etls/src/jobs
    for mars_namespace in os.listdir(root_path):
        mars_path = os.path.join(root_path, mars_namespace)
        if not os.path.isdir(mars_path):
            continue
        for ent in os.listdir(mars_path):  # `ent`: "materialize_large_cedar" or "whereami.py"
            ent_path = os.path.join(mars_path, ent)
            full_mars_path = os.path.join(ent_path, "__mars__.py")
            # Look for src/jobs/* where exists __mars__.py
            if os.path.isdir(ent_path) and os.path.exists(full_mars_path):
                to_import = ".".join(["src", "jobs", mars_namespace, ent, "__mars__"])
                imported = importlib.import_module(to_import)
                doc = JobDoc(ent, imported)
                out.append(doc)
    return out


def _main():
    docs = [j.render() for j in gather_job_docs()]
    print(docs)


if __name__ == "__main__":
    _main()
