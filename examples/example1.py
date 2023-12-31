try:
    import sys
    sys.path.insert(0, '../pathlibutil')
finally:
    from pathlibutil import Path


def main():
    """Example 1: Read a file and print its content and some file information to stdout."""

    readme = Path('README.md')

    print(f'File size: {readme.size()} Bytes')
    print(f'File sha1: {readme.hexdigest("sha1")}')

    print('File content'.center(80, '='))

    for line in readme.read_lines(encoding='utf-8'):
        print(line, end='')

    print('EOF'.center(80, '='))


if __name__ == '__main__':
    main()
