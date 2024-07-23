def main():
    """
    Inherit from `pathlibutil.Path` to register new a archive format. Specify a
    `archive` as keyword argument in the new subclass, which has to be the suffix
    without `.` of the archives. Implement a classmethod `_register_archive_format()`
    to register new archive formats.

    > Path.make_archive(), Path.archive_formats and Path.move()
    """
    import shutil

    import pathlibutil

    class RegisterFooBarFormat(pathlibutil.Path, archive="foobar"):
        @classmethod
        def _register_archive_format(cls):
            """
            implement new register functions for given `archive`
            """
            try:
                import required_package_name
            except ModuleNotFoundError:
                raise ModuleNotFoundError("pip install <required_package_name>")

            def pack_foobar(
                base_name, base_dir, owner=None, group=None, dry_run=None, logger=None
            ) -> str:
                """callable that will be used to unpack archives.

                Args:
                    base_name (`str`): name of the file to create
                    base_dir (`str`): directory to start archiving from, defaults to `os.curdir`
                    owner (`Any`, optional): as passed in `make_archive(*args, owner=None, **kwargs)`. Defaults to None.
                    group (`Any`, optional): as passed in `make_archive(*args, group=None, **kwargs)`. Defaults to None.
                    dry_run (`Any`, optional): as passed in `make_archive(*args, dry_run=None, **kwargs)`. Defaults to None.
                    logger (`logging.Logger`, optional): as passed in `make_archive(*args, logger=None, **kwargs)`. Defaults to None.

                Returns:
                    str: path of the new created archive
                """
                raise NotImplementedError("implement your own pack function")

            def unpack_foobar(archive, path, filter=None, extra_args=None) -> None:
                """callable that will be used to unpack archives.

                Args:
                    archive (`str`): path of the archive
                    path (`str`): directory the archive must be extracted to
                    filter (`Any`, optional): as passed in `unpack_archive(*args, filter=None, **kwargs)`. Defaults to None.
                    extra_args (`Sequence[Tuple[name, value]]`, optional): additional keyword arguments, specified by `register_unpack_format(*args, extra_args=None, **kwargs)`. Defaults to None.
                """
                raise NotImplementedError("implement your own unpack function")

            shutil.register_archive_format(
                "foobar", pack_foobar, description="foobar archives"
            )
            shutil.register_unpack_format("foobar", [".foo.bar"], unpack_foobar)

    file = pathlibutil.Path("README.md")

    print(f"available archive formats: {file.archive_formats}")

    archive = file.make_archive("README.foo.bar")

    backup = archive.move("./backup/")

    print(f"archive created: {archive.name} and moved to: {backup.parent}")


if __name__ == "__main__":
    main()
