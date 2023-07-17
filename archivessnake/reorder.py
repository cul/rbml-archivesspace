import argparse

from scripts.update_order import OrderUpdater


def main():
    parser = argparse.ArgumentParser(description="Removes subseries-level wayfinders.")
    parser.add_argument(
        "series_uri",
        help="ASpace ID of parent series. E.g., /repositories/2/archival_objects1234",
    )
    parser.add_argument("mode", help="ArchivesSpace instance: dev, prod, or test.")
    parser.add_argument(
        "stop_uri",
        help="ASpace ID of sibling to stop finding wayfinders. E.g., /repositories/2/archival_objects/4321",
    )
    parser.add_argument("delete_list", help="Output list for wayfinders to delete.")
    parser.add_argument(
        "--output_only",
        default=False,
        action="store_true",
        help="Output to file only; do not delete.",
    )
    parser.add_argument(
        "--file_exists", default=False, action="store_true", help="Use existing list.",
    )
    parser.add_argument(
        "--delete_wayfinders",
        default=False,
        action="store_true",
        help="Delete wayfinders.",
    )
    args = parser.parse_args()
    order_updater = OrderUpdater(args.mode)
    if not args.file_exists:
        order_updater.get_wayfinders(args.series_uri, args.stop_uri, args.delete_list)
    if not args.output_only:
        order_updater.reorder_objects_from_file(
            args.series_uri, args.delete_list, args.delete_wayfinders
        )


if __name__ == "__main__":
    main()
