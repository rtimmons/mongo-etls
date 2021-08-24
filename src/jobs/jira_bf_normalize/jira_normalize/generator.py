import os
import json
from typing import Tuple, Optional, List
import csv
import re


def _array_to_row(fd_types: dict) -> str:
    fds = [f"\"{k}\" {v}" for k, v in fd_types.items()]
    return f"array(row({', '.join(fds)}))"


_MULTISELECT_TYPES = {
    "self": "varchar",
    "disabled": "boolean",
    "id": "varchar",
    "value": "varchar",
}

# [{"archived": false, "releaseDate": "2016-06-07", "name": "3.2.7", "description": "Stable",
# "self": "https://jira-staging.corp.mongodb.com/rest/api/2/version/16890", "id": "16890", "released": true}]
_MULTIVERSION_TYPES = {
    "archived": "boolean",
    "releaseDate": "varchar",  # TODO: this should use iso parsing somehow
    "name": "varchar",
    "description": "varchar",
    "self": "varchar",
    "id": "varchar",  # TODO: number
    "released": "boolean",
}

# [{"emailAddress": "abc@mongodb.com", "avatarUrls": {"48x48":
# "https://jira-staging.corp.mongodb.com/secure/useravatar?avatarId=10122", "24x24":
# "https://jira-staging.corp.mongodb.com/secure/useravatar?size=small&avatarId=10122", "16x16":
# "https://jira-staging.corp.mongodb.com/secure/useravatar?size=xsmall&avatarId=10122", "32x32":
# "https://jira-staging.corp.mongodb.com/secure/useravatar?size=medium&avatarId=10122"}, "displayName": "ab
# c", "name": "abc", "timeZone": "UTC", "self":
# "https://jira-staging.corp.mongodb.com/rest/api/2/user?username=abc.abc", "active": true,
# "key": "abc.abc"}]
_REQUEST_PARTICIPANT_TYPES = {
    "emailAddress": "varchar",
    "avatarUrls": "map(varchar, varchar)",
    "displayName": "varchar",
    "name": "varchar",
    "timeZone": "varchar",
    "self": "varchar",
    "active": "boolean",
    "key": "varchar",
}


class JiraCustomField:
    def __init__(self, data: dict):
        self.data = data

    @staticmethod
    def read_from_file(file_path: str) -> List["JiraCustomField"]:
        with open(file_path) as handle:
            return [JiraCustomField(it) for it in json.load(handle)]

    @property
    def ignore(self) -> bool:
        is_custom = self.data["custom"]
        return not is_custom

    @property
    def id(self) -> str:
        return f"fields__{self.data['id']}"

    @property
    def id_num(self) -> str:
        k_prefix = len("customfield_")
        return self.data["id"][k_prefix:]

    @property
    def schema_type(self) -> Tuple[str, Optional[str]]:
        assert not self.ignore
        return self.data["schema"]["type"], self.data["schema"]["custom"]

    @property
    def null_safe(self) -> str:
        return f"nullif(nullif({self.id}, 'nan'), 'None')"

    @property
    def castable(self) -> str:
        typ, subtyp = self.schema_type
        if typ in {"string", "any", "user", "sd-servicelevelagreement", "option", "sd-customerrequesttype"}:
            return self.null_safe
        if typ == "option-with-child" and subtyp.endswith("cascadingselect"):
            return self.null_safe
        if typ == "sd-approvals":
            # TODO: fields__customfield_14450
            return self.null_safe
        if typ == "array":
            # TODO: fields__customfield_18255 is multigrouppicker but missing
            if subtyp.endswith("multiselect") or subtyp.endswith("multiuserpicker") or subtyp.endswith("multicheckboxes") or subtyp.endswith("multigrouppicker"):
                return f"cast({self.json_parsed} as {_array_to_row(_MULTISELECT_TYPES)})"
            if subtyp.endswith("labels") or subtyp.endswith("sd-customer-organizations"):
                return f"cast({self.json_parsed} as array(varchar))"
            if subtyp.endswith("multiversion"):
                return f"cast({self.json_parsed} as {_array_to_row(_MULTIVERSION_TYPES)})"
            if subtyp.endswith("sd-request-participants"):
                return f"cast({self.json_parsed} as {_array_to_row(_REQUEST_PARTICIPANT_TYPES)})"
            if subtyp.endswith("scripted-field"):
                return f"try(cast({self.null_safe} as double))"
            if subtyp.endswith("greenhopper.jira:gh-sprint"):
                return f"cast({self.json_parsed} as array(varchar))"
        if typ == "number":
            if subtyp.endswith("float") or subtyp.endswith("scripted-field") or subtyp.endswith("jpo-custom-field-original-story-points"):
                return f"try(cast({self.null_safe} as double))"
        if typ == "date":
            if subtyp.endswith("datepicker") or subtyp.endswith("jpo-custom-field-baseline-start") or subtyp.endswith("jpo-custom-field-baseline-end"):
                return f"from_iso8601_date({self.null_safe})"
        if typ == "datetime":
            # TODO: fields__customfield_14452 is sd-request-feedback-date but missing
            if subtyp.endswith("firstresponsedate") or subtyp.endswith("customfieldtypes:datetime") or subtyp.endswith("groovyrunner:scripted-field") or subtyp.endswith("sd-request-feedback-date"):
                return f"from_iso8601_timestamp({self.null_safe})"
        if typ == "group":
            return self.null_safe  # TODO: not right, only fields__customfield_10030 uses this I think ?
        if typ == "version":
            if subtyp.endswith("customfieldtypes:version"):  # TODO: fields__customfield_11653
                return self.null_safe
            if subtyp.endswith("greenhopper-releasedmultiversionhistory"):  # TODO: fields__customfield_10559
                return self.null_safe
        print(f"Unknown type ({typ}, {subtyp}) on {self.id}")
        return "??"

    @property
    def json_parsed(self):
        return f"json_parse({self.null_safe})"

    @property
    def column_name(self) -> str:
        out = self.data["name"]
        # lol let's pretend regexes don't exist for now
        replaced = out.lower()\
            .replace(" ", "_")\
            .replace("'", "_")\
            .replace("?", "_")\
            .replace("!", "_")\
            .replace("#", "_")\
            .replace("/", "_")\
            .replace("’", "_")\
            .replace("-", "_")\
            .replace("(", "_")\
            .replace(")", "_")\
            .replace("__", "_")\
            .replace("__", "_")
        return f"\"{replaced}_cf\""

    @property
    def select(self) -> str:
        return (
            # f"{self.id} as {self.column_name}_{self.id_num}_orig, "
            f"{self.castable} as {self.column_name}, "
            f"-- {self.data['name']}"
        )


_CUSTOM_FIELD_REX = re.compile(r"^fields__customfield_(\d+)(?:__(.*?))?(?:__(.*))?$")


class PrestoField:
    # "Column", "Type", "Extra", "Comment"
    def __init__(self, row: dict, custom_fields: List[JiraCustomField]):
        self.column_name = row["Column"]
        self.type = row["Type"]
        self.extra = row["Extra"]
        self.comment = row["Comment"]
        match = _CUSTOM_FIELD_REX.match(self.column_name)
        self.is_custom_field = True if match else False
        if match:
            self.id_num = match.group(1)
            self.subfield_1 = None if not match.group(2) else match.group(2)
            self.subfield_2 = None if not match.group(3) else match.group(3)
        else:
            self.id_num = None
            self.subfield_1 = None
            self.subfield_2 = None

    @staticmethod
    def read_from_file(file_path: str, custom_fields: List[JiraCustomField]) -> List["PrestoField"]:
        with open(file_path) as handle:
            reader = csv.DictReader(handle)
            fields = [PrestoField(row, custom_fields) for row in reader]
        return fields


##
# -- example of casting to row
#
# with x (variant, tasks) as (
#   values
#     ('variant1', array['task-1a', 'task-1b']),
#     ('variant2', array['task-2a', 'task-2b'])
# )
# select
#     cast ((variant, tasks) as row(variant varchar, tasks array(varchar))) as variant_tasks
# from x;
#
# -- so use this style for custom fields:
#
# select
#     cast(
#         (
#             fields__customfield_16450,
#             fields__customfield_16450__disabled,
#             fields__customfield_16450__id,
#             fields__customfield_16450__self,
#             fields__customfield_16450__value
#         ) as row (
#             "full_value" varchar,
#             "disabled" varchar,
#             "id" varchar,
#             "self" varchar,
#             "value" varchar
#         )) as "topology"
# from
#     awsdatacatalog.raw_jira.dw__jira__issues issues;
##


def main():
    my_dir = os.path.dirname(__file__)
    custom_fields = JiraCustomField.read_from_file(os.path.join(my_dir, "jira_custom_fields_prod.json"))
    presto_fields = PrestoField.read_from_file(os.path.join(my_dir, "presto_fields_prod.csv"),
                                               custom_fields)
    # TODO: group presto_fields by id; find way to group multiple fields as a row item


if __name__ == "__main__":
    main()
