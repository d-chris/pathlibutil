def main():
    """
    Return a `Path` object with mapped paths if they exists.
    > `Path.local()`, `Path.with_anchor()`
    """
    import pathlibutil

    class Path:
        def __new__(cls, *args) -> pathlibutil.Path:
            return pathlibutil.Path.local(
                *args,
                map={
                    r"\\server\static": r"C:\Shares\static",
                    r"\\server\temp": r"C:\Shares\temp",
                },
            )

    org = Path(r"C:\Shares\temp\path\to\file.txt")
    unc = org.with_anchor(r"\\server\temp")

    print(f"{org=} {unc=}")

    dir = Path(r"C:\Shares\temp")
    dir.mkdir(parents=True)

    file = Path(r"\\server\temp\path\to\file.txt")
    assert file.as_posix() == "C:/Shares/temp/path/to/file.txt"
    print(f"{file=} anchor can be mapped when it path exists.")

    dir.parent.delete(recursive=True)

    file = Path(r"\\server\temp\path\to\file.txt")
    assert file.as_posix() == "//server/temp/path/to/file.txt"
    print(f"{file=} can't be resolved when mapped path does not exists.")


if __name__ == "__main__":
    main()
