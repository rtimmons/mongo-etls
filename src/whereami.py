"""
Knows about how to locate files jobs needs to do their work.
Always use whereami instead of hard-coding knowledge about this repo's layout.
I.e., use this file instead of __file__ or relative paths based on cwd in code or tests.
"""
import os


def _findup(fpath: str, cwd: str) -> str:
    """
    Look "up" the directory tree for fpath starting at cwd. Raises if not found.
    :param fpath:
    :param cwd:
    :return:
    """
    curr = cwd
    while os.path.exists(curr):
        if os.path.exists(os.path.join(curr, fpath)):
            return os.path.normpath(curr)
        curr = os.path.join(curr, "..")
    raise Exception(f"Cannot find {fpath} in {cwd} or any parent dirs.")


def repo_path(*args: str) -> str:
    """
    :param args: string path elements for a file in the dsi repo
                 e.g. ("src", "whereami.py") for this file
    :return: the full path to the file or IOError if it doesn't exist.
    """
    root = _findup(".repo-root", os.path.dirname(__file__))
    result = os.path.join(root, *args)
    if not os.path.exists(result):
        raise IOError(f"Repo file {args} doesn't exist")
    return result
