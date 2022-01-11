from typing import Union, List
import yaml

import src.jobs.whereami

_COMMENT_START = "-- "

_REPLACEMENTS = {
    "-- <COMMON_ETL_FIELDS>": ", LOCALTIMESTAMP AS \"_extract_timestamp\""
}


def _replace(line: str) -> str:
    for needle, replacement in _REPLACEMENTS.items():
        line = line.replace(needle, replacement)
    return line


class SqlFile:
    def __init__(self, path: Union[List[str], str]):
        if isinstance(path, str):
            self.contents = path
            self.path = None
        else:
            self.path = src.jobs.whereami.repo_path(*path)
            self.contents = None

    def location(self) -> str:
        return self.path if self.path else "InlineContents"

    def __str__(self):
        return f"SQLFile:{self.parsed_contents()}@{self.location()}"

    def contents_lines(self) -> List[str]:
        if self.contents:
            out = self.contents.split("\n")
            return out
        with open(self.path, "r") as handle:
            return [line.rstrip() for line in handle.readlines()]

    def contents(self) -> str:
        return "\n".join(self.contents_lines())

    def parsed_lines(self) -> List[str]:
        return [_replace(line) for line in self.contents_lines()]

    def parsed_contents(self) -> str:
        return "\n".join(self.parsed_lines())

    def front_matter(self) -> dict:
        yaml_lines = []
        for line in self.contents_lines():
            line = line.rstrip()
            if not line.startswith(_COMMENT_START):
                break
            contents = line[len(_COMMENT_START):]  # "-- <yaml>" -> "<yaml>"
            if contents.startswith("<yaml>"):
                continue
            if contents.startswith("</yaml>"):
                break
            yaml_lines.append(contents)
        if len(yaml_lines) > 0:
            to_parse = "\n".join(yaml_lines)
            return yaml.safe_load(to_parse)
        return dict()

# if __name__ == "__main__":
#     f = SqlFile("""-- <yaml>
# -- DependsOn: {}
# -- </yaml>
# SELECT *
# -- <COMMON_ETL_FIELDS>
# FROM x
# """)
#     print(f.front_matter())
#     print(f.parsed_lines())
#     print(f.parsed_contents())
