def main():
    """
    Write a file with md5 checksums of all python files in the pathlibutil-directory.
    > `Path.hexdigest()`
    """

    from pathlibutil import Path

    file = Path("pathlibutil.md5")

    with file.open("w") as f:
        f.write(
            "# MD5 checksums generated with pathlibutil "
            "(https://pypi.org/project/pathlibutil/)\n\n"
        )

        i = 0
        for i, filename in enumerate(Path("./pathlibutil").glob("*.py"), start=1):
            f.write(f"{filename.hexdigest()} *{filename}\n")

    print(f"\nwritten: {i:>5} {file.default_hash}-hashes to: {file}")


if __name__ == "__main__":
    main()
