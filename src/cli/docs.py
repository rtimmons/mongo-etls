"""
Traverses the repo and prints documentation for jobs/tasks/* that are found.
"""
from jobs.model import print_docs_markdown


def _main() -> None:
    print_docs_markdown()


if __name__ == "__main__":
    _main()
