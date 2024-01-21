def main():
    """
    Read a file and print its content and some file information to stdout.
    > `Path.read_lines()`
    """
    from pathlibutil import Path

    readme = Path("README.md")

    print(f"File size: {readme.size()} Bytes")
    print(f'File sha1: {readme.hexdigest("sha1")}')

    print("File content".center(80, "="))

    for line in readme.read_lines(encoding="utf-8"):
        print(line, end="")

    print("EOF".center(80, "="))


if __name__ == "__main__":
    main()
