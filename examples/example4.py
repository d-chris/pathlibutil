try:
    import sys
    sys.path.insert(0, '../pathlibutil')
finally:
    from pathlibutil import Path


def main():
    """Example 4: Search all pycache directories and free the memory."""

    mem = 0
    i = 0

    for i, cache in enumerate(Path('.').rglob('*/__pycache__/'), start=1):
        cache_size = cache.size()
        try:
            cache.delete(recursive=True)
        except OSError:
            print(f'Failed to delete {cache}')
        else:
            mem += cache_size

    print(f'{i} cache directories deleted, {mem / 2**20:.2f} MB freed.')


if __name__ == '__main__':
    main()
