def main():
    """
    Search all pycache directories and free the memory and display the number of
    deleted directories and the amount of memory freed in MB.
    > `Path.delete()`, `Path.size()` and `ByteInt`
    """

    from pathlibutil import ByteInt, Path

    mem = ByteInt(0)
    i = 0

    for i, cache in enumerate(Path(".").rglob("*/__pycache__/"), start=1):
        cache_size = cache.size()
        try:
            cache.delete(recursive=True)
        except OSError:
            print(f"Failed to delete {cache}")
        else:
            mem += cache_size

    print(f"{i} cache directories deleted, {mem:.1mb} MB freed.")


if __name__ == "__main__":
    main()
