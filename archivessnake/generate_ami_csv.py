import argparse

from scripts.ami_csv import AMISpreadsheet


def main():
    parser = argparse.ArgumentParser(
        description="Adds access restriction to archival objects without conditions governing access notes and with at least one instance."
    )
    parser.add_argument("mode", help="ArchivesSpace instance: dev, prod, or test.")
    parser.add_argument(
        "series_id", help="ArchivesSpace ID for AV series. Example: 1234",
    )
    args = parser.parse_args()
    AMISpreadsheet(args.mode).create(args.series_id)


if __name__ == "__main__":
    main()
