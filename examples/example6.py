"""
>>> poetry run examples/example6.py -b
Building frozen: K:/pathlibutil/examples/example6.exe
Build succeeded: 0

>>> poetry run examples/example6.py
we are                          not frozen

bundle dir is                   K:/pathlibutil/examples
sys.argv[0] is                  K:/pathlibutil/examples/example6.py
sys.executable is               K:/pathlibutil/.venv/Scripts/python.exe
os.getcwd is                    K:/pathlibutil

Path.cwd(frozen=True) is        K:/pathlibutil
Path.cwd(frozen=False) is       K:/pathlibutil
Path.cwd(frozen=_MEIPASS) is    K:/pathlibutil

>>> examples/example6.exe
we are                          ever so frozen

bundle dir is                   C:/Users/CHRIST~1.DOE/AppData/Local/Temp/_MEI106042
sys.argv[0] is                  examples/example6.exe
sys.executable is               K:/pathlibutil/examples/example6.exe
os.getcwd is                    K:/pathlibutil

Path.cwd(frozen=True) is        K:/pathlibutil/examples
Path.cwd(frozen=False) is       K:/pathlibutil
Path.cwd(frozen=_MEIPASS) is    C:/Users/CHRIST~1.DOE/AppData/Local/Temp/_MEI106042
"""

import os
import sys

import click

from pathlibutil import Path


def run_build():
    import subprocess

    try:
        subprocess.run(
            ["pyinstaller", "--version"], capture_output=True
        ).check_returncode()
    except (subprocess.CalledProcessError, FileNotFoundError):
        raise ModuleNotFoundError("pip install pyinstaller")

    file = Path(__file__)

    return subprocess.run(
        [
            "pyinstaller",
            "--onefile",
            "--noconfirm",
            "--name",
            file.stem,
            "--distpath",
            file.parent.as_posix(),
            "--log-level",
            "ERROR",
            file.as_posix(),
        ]
    ).returncode


def main(build: bool):
    """
    Access the current working directory with optional parameter `frozen` to determine
    different directories when script is bundled to an executable,
    e.g. with `pyinstaller`.
    > `Path.cwd()`
    """

    if getattr(sys, "frozen", False):
        frozen = "ever so"
        bundle_dir = sys._MEIPASS

        if build is True:
            raise click.BadOptionUsage(
                "--build", "Run from a normal Python environment"
            )

    else:
        frozen = "not"
        bundle_dir = Path(__file__).parent

        if build is True:
            print(f"Building frozen: {Path(__file__).with_suffix('.exe')}")
            try:
                result = run_build()
            except Exception as e:
                result = 1
                print(f"Build failed: {e}")
            else:
                print(f"Build succeeded: {result}")
            finally:
                sys.exit(result)

    print(f'{"we are":<32}{frozen} frozen\n')
    print(f'{"bundle dir is":<32}{bundle_dir}')
    print(f'{"sys.argv[0] is":<32}{sys.argv[0]}')
    print(f'{"sys.executable is":<32}{sys.executable}')
    print(f'{"os.getcwd is":<32}{os.getcwd()}\n')

    for param in (True, False, "_MEIPASS"):
        print(f'{f"Path.cwd(frozen={param}) is":<32}{Path.cwd(frozen=param)}')


@click.command()
@click.option("-b", "--build", is_flag=True, help="Build the frozen executable")
def cli(build: bool = False):
    main(build)


if __name__ == "__main__":
    cli()
