from typing import List, Optional, Union

import yaml

import src.jobs.whereami

_COMMENT_START = "-- "


class SqlFile:
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
            contents = line[len(_COMMENT_START) :]  # "-- <yaml>" -> "<yaml>"
            if contents.startswith("<yaml>"):
                continue
            if contents.startswith("</yaml>"):
                break
            yaml_lines.append(contents)
        if len(yaml_lines) > 0:
            to_parse = "\n".join(yaml_lines)
            return yaml.safe_load(to_parse)
        return dict()
