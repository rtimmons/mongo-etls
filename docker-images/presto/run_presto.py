"""Run a presto query."""
import abc
import os
from typing import Generator

import click
import presto

DESTINATIONS: list[str] = ["stdout"]


def create_reporter(destination: str) -> "Reporter":
    """Create query results reporter"""
    if destination == "stdout":
        return StdoutReporter()

    raise ValueError(f"Invalid destination specified - {destination} not in {DESTINATIONS}")


class Executor:
    """Presto query executor"""

    def __init__(self, conn: presto.dbapi.Connection, sql: str, batchsize: int = 50) -> None:
        self.conn = conn
        self.sql = sql
        self.batchsize = batchsize

    def execute_query(self) -> Generator[list[list], None, None]:
        """Execute query and yield batched results"""
        cur = self.conn.cursor()
        cur.execute(self.sql)
        while True:
            batch = cur.fetchmany(self.batchsize)
            if not batch:
                break
            yield batch


class Reporter(abc.ABC):
    """Base class for Reporter"""

    @abc.abstractmethod
    def report(self, executor: Executor) -> None:
        raise NotImplementedError()


class StdoutReporter(Reporter):
    """Report to stdout"""

    def report(self, executor: Executor) -> None:
        for idx, res in enumerate(executor.execute_query()):
            print(f"Batch {idx}", res)


@click.group(name="presto-argo")
@click.pass_context
def cli(ctx: click.Context) -> None:
    pass


@cli.command("presto-task", help="Run presto task")
@click.option("--host", default=None, required=True, help="Name of the coordinator")
@click.option(
    "--port", default=None, required=True, help="TCP port to connect to the coordinator", type=int
)
@click.option("--catalog", default=None, required=True, help="Catalog to query")
@click.option("--sql", default=None, required=True, help="Sql query to execute")
@click.option(
    "--destination",
    required=True,
    help="Destination to report output",
    type=click.Choice(DESTINATIONS),
)
def presto_task(host: str, port: int, catalog: str, sql: str, destination: str) -> None:
    """Run a presto task."""
    presto_id = os.environ["PRESTO_ID"]
    presto_secret = os.environ["PRESTO_SECRET"]
    conn = presto.dbapi.connect(
        host=host,
        port=port,
        user=presto_id,
        catalog=catalog,
        http_scheme="https",
        auth=presto.auth.BasicAuthentication(presto_id, presto_secret),
    )

    executor = Executor(conn, sql)
    reporter = create_reporter(destination=destination)
    reporter.report(executor)


if __name__ == "__main__":
    cli()
