import argparse

from scripts.file_level_restrictions import FileLevelRestrictions


def main():
    parser = argparse.ArgumentParser(
        description="Adds access restriction to archival objects without conditions governing access notes and with at least one instance."
    )
    parser.add_argument("mode", help="ArchivesSpace instance: dev, prod, or test.")
    parser.add_argument(
        "-r",
        "--resources",
        nargs="+",
        help="List of resources (integers). E.g.: -r 123 654",
        type=int,
        required=True,
    )
    args = parser.parse_args()
    for resource in args.resources:
        FileLevelRestrictions(args.mode).run(resource)


if __name__ == "__main__":
    main()
