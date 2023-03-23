import argparse

from scripts.update_tree import TreeUpdater


def main():
    parser = argparse.ArgumentParser(
        description="Adds access restriction to archival objects without conditions governing access notes and with at least one instance."
    )
    parser.add_argument("mode", help="ArchivesSpace instance: dev, prod, or test.")
    parser.add_argument(
        "resource",
        help="URI for resource to update. E.g., /repositories/2/resources/123",
    )
    parser.add_argument('--log_only', default=False, action='store_true', help="Run in log-only mode.")
    args = parser.parse_args()
    TreeUpdater(args.mode).run(args.resource, args.log_only)


if __name__ == "__main__":
    main()