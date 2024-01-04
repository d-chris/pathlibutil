try:
    import sys
    sys.path.insert(0, '../pathlibutil')
finally:
    import pathlibutil


def main():
    """Example 5: Register new archive format."""

    import shutil

    class Path(pathlibutil.Path):
        @staticmethod
        def _register_rar_format():
            """ 
                implement new register functions for given suffixes
                as a staticmethod: `_register_<suffixes>_format()`

                eg. achive.foo.bar as `_register_foobar_format()` 
            """
            try:
                from pyunpack import Archive
            except ModuleNotFoundError:
                raise ModuleNotFoundError('pip install pyunpack')
            else:
                shutil.register_archive_format(
                    'rar', Archive, description='rar archive'
                )
                shutil.register_unpack_format(
                    'rar', ['.rar'], Archive
                )

    archive = Path('README.md').make_archive('README.rar')

    backup = archive.move('./backup/')

    print(f'rar archive created: {archive.name} and moved to: {backup.parent}')


if __name__ == '__main__':
    main()
