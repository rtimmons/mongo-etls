import jobs.whereami


def read_file(*repo_rooted_path):
    to_read = jobs.whereami.repo_path(*repo_rooted_path)
    with open(to_read) as handle:
        return handle.read()
