def main():
    """
    Read a file with md5 checksums and verify them.
    > `Path.verify()`, `Path.default_hash` and `contextmanager`
    """

    from pathlibutil import Path

    file = Path("pathlibutil.md5")

    def no_comment(line: str) -> bool:
        return not line.startswith("#")

    with file.parent as cwd:
        miss = 0
        ok = 0
        fail = 0

        for line in filter(no_comment, file.read_lines()):
            try:
                digest, filename = line.strip().split(" *")
                verification = Path(filename).verify(digest, "md5")
            except ValueError as split_failed:
                continue
            except FileNotFoundError as verify_failed:
                tag = "missing"
                miss += 1
            else:
                if verification:
                    tag = "ok"
                    ok += 1
                else:
                    tag = "fail"
                    fail += 1

            print(f'{tag.ljust(len(digest), ".")} *{filename}')

        print(f"\nok: {ok:<5} fail: {fail:<5} missing: {miss}")


if __name__ == "__main__":
    main()
