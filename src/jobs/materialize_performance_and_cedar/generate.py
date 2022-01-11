import yaml
import src.jobs.whereami as whereami


def get_struct() -> dict:
    struct_path = whereami.repo_path("src", "jobs", "materialize_performance_and_cedar", "structure.yml")
    with open(struct_path, "r") as handle:
        return yaml.safe_load(handle)


def columnize(kvs: dict,
              padding: int = 2,
              leader: str = "SELECT",
              last_line: str = "-- <COMMON_ETL_FIELDS>") -> str:
    max_len = 0
    for k, v in kvs.items():
        max_len = max(max_len, len(k))

    leader_len = len(leader)

    out = []
    count = -1
    max_count = len(kvs.keys()) - 1
    for k, v in kvs.items():
        count += 1
        if count == 0:
            line = f"{leader}{' '*padding}"
        else:
            line = f"{' '*(leader_len+padding)}"
        remain = max_len - len(k) + padding
        line = f"{line}{k}{' '*remain}AS {v}"
        if count < max_count:
            line = f"{line},"
        out.append(line)
    if last_line:
        out.append(f"{' '*(padding+leader_len)}{last_line}")
    return "\n".join(out)

# def sql_for_table(table) -> str:
#     out = ["SELECT"]


def main():
    struct = get_struct()
    for source_name, source in struct["Sources"].items():
        for db_name, db in source.items():
            for table_name, table in db.items():
                col_dict = dict()
                col_dict['CAST(vs."_id" AS VARCHAR)'] = '"_id"'
                for column in table:
                    col_dict[f'vs."{column}"'] = f'"{column}"'
                select_statement = columnize(col_dict)
                from_statement = f"FROM  {source_name}.{db_name}.{table_name} AS vs"
                print(f"{select_statement}\n{from_statement}\n\n")



if __name__ == "__main__":
    main()
