import csv


def write_data_to_csv(sheet_data, filepath):
    """Write data to a CSV file.

    Args:
        sheet_data (list): list of lists (rows)
        filepath (Path obj or str): Path object or string of CSV filepath
    """
    with open(filepath, "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(sheet_data)
