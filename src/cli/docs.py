"""
Render documentation website.
"""
import importlib
import os
import os.path

from src.jobs import whereami
from typing import Any, List


class JobDoc:
    def __init__(self, name: str, module: Any):
        self._name = name
        self._module = module

    def render(self) -> List[str]:
        return [
            f"# {self._name}",
            "\n\n",
            self._module.__doc__,
        ]


def gather_job_docs() -> List[JobDoc]:
    out = []
    root_path = whereami.repo_path("src", "jobs")  # /home/foo/Projects/mongo-etls/src/jobs
    for ent in os.listdir(root_path):  # `ent`: "materialize_large_cedar" or "whereami.py"
        ent_path = os.path.join(root_path, ent)
        full_mars_path = os.path.join(ent_path, "__mars__.py")
        # Look for src/jobs/* where exists __mars__.py
        if os.path.isdir(ent_path) and os.path.exists(full_mars_path):
            to_import = ".".join(["src", "jobs", ent, "__mars__"])
            imported = importlib.import_module(to_import)
            doc = JobDoc(ent, imported)
            out.append(doc)
    return out


def _main():
    jobs_mars_imports()


if __name__ == "__main__":
    _main()
