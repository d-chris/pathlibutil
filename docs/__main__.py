import sys

import click

from pathlibutil import Path


@click.group()
def cli():
    pass


@cli.command()
@click.argument("root", type=click.Path(file_okay=False))
def erase(root: str) -> None:
    """remove a directry tree"""

    self = Path(sys.argv[0]).parent
    root = Path(root).resolve()

    if self == root:
        raise click.UsageError("Invalid value for ROOT: cannot delete itself")

    try:
        root.delete(recursive=True, missing_ok=True)
    except Exception:
        sys.exit(1)


@cli.command()
@click.argument("src", type=click.Path(exists=True, file_okay=False))
@click.argument("dst", type=click.Path(file_okay=False))
@click.option(
    "-u", "--unignore", is_flag=True, help="remove gitignore files in destination"
)
def copy(src: str, dst: str, unignore=True) -> None:
    """copy directory from src to dst and remove any gitignore files"""

    try:
        dest = Path(src).copy(dst)
    except Exception:
        sys.exit(1)

    if unignore:
        for file in dest.rglob(".gitignore"):
            file.unlink()


if __name__ == "__main__":
    cli()
