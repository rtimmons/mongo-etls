import json
from typing import Tuple, Optional
import csv

with open("/Users/rtimmons/Desktop/fields.csv") as handle:
    reader = csv.DictReader(handle)
    prefix = "fields__"
    _KNOWN_FIELDS = set([row["Column"][len(prefix):] for row in reader])

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


class Field:
    def __init__(self, data: dict):
        self.data = data

    @property
    def ignore(self) -> bool:
        is_custom = self.data["custom"]
        known_field =  self.data["id"] in _KNOWN_FIELDS
        if not known_field:
            print(f"{self.data['id']} not in known fields")
        return not is_custom or not known_field

    @property
    def id(self) -> str:
        return f"fields__{self.data['id']}"

    @property
    def id_num(self) -> str:
        prefix = len("customfield_")
        return self.data["id"][prefix:]

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


if __name__ == "__main__":
    with open("/Users/rtimmons/Desktop/jira_fields_prod.json") as handle:
        fields = [Field(it) for it in json.load(handle)]

    not_ignored = [field for field in fields if not field.ignore]
    types = set("-".join(list(field.schema_type)) for field in not_ignored)
    # print(",\n".join([field.schema_type for field in fields if not field.ignore]))
    # print("\n".join(types))

    print("\n".join([field.select for field in not_ignored]))
