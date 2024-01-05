try:
    import sys
    sys.path.insert(0, '../pathlibutil')
finally:
    import pathlibutil


def main():
    """Example 5: Register new archive format."""

    import shutil

    class RegisterRarFormat(pathlibutil.Path, name='rar'):
        @classmethod
        def _register_archive_format(cls):
            """ 
                implement new register functions for given `name`
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

    file = pathlibutil.Path('README.md')

    print(f"available archive formats: {file.archive_formats}")

    archive = file.make_archive('README.rar')

    backup = archive.move('./backup/')

    print(f'rar archive created: {archive.name} and moved to: {backup.parent}')


if __name__ == '__main__':
    main()
