import json
import warnings


class WarningMessageEncoder(json.JSONEncoder):
    def default(self, obj):

        if isinstance(obj, warnings.WarningMessage):
            return {
                k: v
                for k, v in obj.__dict__.items()
                if v is not None and not k.startswith("_")
            }

        if isinstance(obj, type):
            return obj.__name__

        if isinstance(obj, Exception):
            return str(obj).strip().split("\n")

        return super().default(obj)


def main() -> int:
    """
    Create a static html documentation for the project in the 'public' directory.

    Requires follwing PyPi packages:
    - 'pdoc'
    - 'pathlibutil'

    Returns non-zero on failure.
    """

    try:
        from jinja2_pdoc import jinja2pdoc
        from pdoc import pdoc, render

        from pathlibutil import Path

        jinja2pdoc("docs/README.md.jinja2", silent=False, frontmatter=False)

        with Path(__file__).parent as cwd:
            print(f"\nrunning docs in {cwd=}...")

            documentation = cwd / "public"

            try:
                print(f"cleaning output directory {documentation.size()}.")
                documentation.delete(recursive=True, missing_ok=True)
            except FileNotFoundError:
                pass

            documentation.mkdir(parents=True)

            config = {
                "template_directory": cwd / "dark-mode",
                "show_source": False,
                "search": False,
                "docformat": "google",
            }

            modules = [
                "pathlibutil",
                "pathlibutil.json",
                "pathlibutil.urlpath",
                "pathlib",
                "urllib.parse",
                "urllib.request",
                "shutil",
                "hashlib",
                "builtins",
                "datetime",
                "os",
                "json",
            ]

            with warnings.catch_warnings(record=True) as messages:
                print(f"rendering {modules=}.")

                render.configure(**config)
                pdoc(*modules, output_directory=documentation)

                log = documentation / "warnings.json"

                with log.open("w", encoding="utf-8") as f:
                    json.dump(
                        messages,
                        f,
                        cls=WarningMessageEncoder,
                    )

                if messages:
                    print(f"{log=} generated with {len(messages)} warnings.")
    except ModuleNotFoundError as e:
        print(f"Creation failed, due missing dependency!\n\tpip install {e.name}")
        return 2
    except Exception as e:
        print(f"{documentation=} creation failed!\n\t{e}")
        return 1

    print(f"{documentation=} generated successfully.\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
