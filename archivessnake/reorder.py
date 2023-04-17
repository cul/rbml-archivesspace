import argparse


from scripts.update_order import OrderUpdater


def main():
    parser = argparse.ArgumentParser(description="Removes subseries-level wayfinders.")
    parser.add_argument("series_id", help="ASpace ID of parent series. E.g., 1234")
    parser.add_argument("mode", help="ArchivesSpace instance: dev, prod, or test.")
    parser.add_argument(
        "stop_id", help="ASpace ID of sibling to stop finding wayfinders. E.g., 4321"
    )
    parser.add_argument("delete_list", help="Output list for wayfinders to delete.")
    parser.add_argument(
        "--output_only",
        default=False,
        action="store_true",
        help="Output to file only; do not delete.",
    )
    args = parser.parse_args()
    order_updater = OrderUpdater(args.series_id, args.mode)
    order_updater.get_wayfinders(args.stop_id, args.delete_list)
    if not args.output_only:
        order_updater.reorder_objects_from_file(args.delete_list)


if __name__ == "__main__":
    main()
