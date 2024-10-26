#! .venv\Scripts\python.exe

"""
Console application to convert UNC paths to intranet URLs.

By default, it checks if the filename and URL are available and copies the
normalized URL to the clipboard.

> `pathlibutil.urlpath.url_from()`
"""

import argparse
import sys

try:
    import pyperclip

    import pathlibutil.urlpath as up
except ModuleNotFoundError as e:
    raise ModuleNotFoundError(f"pip install {e.name.split('.')[0]}") from e


def intranet_from(uncpath: str, check: bool = True) -> str:
    """
    Return the intranet URL for the given UNC path.
    """

    url = up.url_from(
        uncpath,
        hostname="http://intranet.example.de",
        strict=check,
    )

    return url.normalize()


def cli():

    parser = argparse.ArgumentParser(
        description=intranet_from.__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "filename",
        nargs="*",
        help="The UNC path to the file.",
    )
    parser.add_argument(
        "-c",
        "--no-check",
        action="store_false",
        dest="check",
        help="Don't check if filename and url is available.",
    )
    parser.add_argument(
        "-s",
        "--silent",
        action="store_true",
        help="Do not print the url to stdout.",
    )
    parser.add_argument(
        "-n",
        "--no-clip",
        action="store_false",
        dest="clip",
        help="Don't copy the url to the clipboard.",
    )

    args = parser.parse_args()
    filename = " ".join(args.filename)

    url = intranet_from(filename, check=args.check)

    if not args.silent:
        print(url)

    if args.clip:
        pyperclip.copy(url)


if __name__ == "__main__":
    try:
        cli()
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)
