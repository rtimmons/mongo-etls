import json
from typing import Tuple, Optional


_MISSING_FIELDS = set(st[8:] for st in [   # lol this is a mess
        f"fields__customfield_{it}" for it in [
            "14750", "14751", "16152", "16563", "17456", "17457", "18151", "18255", "18554", "19352",
            "19476", "19958", "20057", "20181", "20191", "20259", "20361", "20396", "20477", "20757",
            "13354", "16151", "20258", "10030", "10041", "11050", "11653", "11850", "11851", "11852",
            "11855", "11860", "12752", "14351", "16254", "16556", "16559", "16561", "16564", "17550",
            "17552", "17764", "18062", "18550", "18551", "18552", "18553", "18850", "18851", "18857",
            "18956", "19255", "19460", "19461", "19477", "19752", "20050", "20051", "20052", "20053",
            "20060", "20061", "20062", "20179", "20180", "20182", "20183", "20184", "20185", "20186",
            "20187", "20188", "20189", "20190", "20251", "20252", "20253", "20254", "20256", "20257",
            "20261", "20262", "20360", "20362", "20363", "20364", "20365", "20366", "20367", "20368",
            "20369", "20370", "20478", "20479", "20480", "20758", "20759", "20760", "20761", "20762",
            "10165", "17482", "17483", "18450", "19957",
    ]
])


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
        force_ignored = self.data["id"] in _MISSING_FIELDS
        return not is_custom or force_ignored

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
        return f"{replaced}_cf"

    @property
    def select(self) -> str:
        return f"{self.id} as {self.column_name}_{self.id_num}_orig, "\
               f"{self.castable} as {self.column_name}, "\
               f"-- {self.data['name']}"


if __name__ == "__main__":
    with open("/Users/rtimmons/Desktop/jira_fields.json") as handle:
        fields = [Field(it) for it in json.load(handle)]

    not_ignored = [field for field in fields if not field.ignore]
    types = set("-".join(list(field.schema_type)) for field in not_ignored)
    # print(",\n".join([field.schema_type for field in fields if not field.ignore]))
    # print("\n".join(types))

    print("\n".join([field.select for field in not_ignored]))
