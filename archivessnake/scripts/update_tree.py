import logging
from configparser import ConfigParser
from datetime import datetime
from re import fullmatch

from .aspace_client import ArchivesSpaceClient


class DateException(Exception):
    pass


def date_is_iso(date_string):
    """Determine whether a date string conforms to ISO-8601.

    Args:
        date_string (str): date string (e.g., 1950-05-01)

    Returns:
        bool: return True if ISO date
    """
    if fullmatch(r"\d\d\d\d", date_string):
        return True
    elif fullmatch(r"\d\d\d\d-\d\d", date_string):
        return True
    else:
        try:
            datetime.fromisoformat(date_string)
            return True
        except ValueError:
            raise DateException(
                "One or more normalized dates do not conform to ISO-8601"
            )


def leading_trailing(aspace_json):
    """Gets keys whose values contain leading or trailing whitespace.

    Args:
        aspace_json (dict): json representation of an ASpace object

    Returns:
        list: keys whose values contain leading or trailing whitespace
    """
    leading_trailing = []
    for k, v in aspace_json.items():
        if type(v) is str:
            if v.strip() != v:
                if k not in ["display_string"]:
                    leading_trailing.append(k)
    return leading_trailing


def check_date(date):
    """Determines whether ArchivesSpace begin and end dates are ISO-8601.

    Modifies begin/end date if it contains leading or trailing whitespace.

    Args:
        date (dict): ArchivesSpace date

    Returns:
        dict: ArchivesSpace date, modified if necessary
    """
    try:
        expression = date.get("expression")
        if expression:
            if expression.strip() != expression:
                date["expression"] = expression.strip()
        begin = date.get("begin")
        if begin:
            if begin.strip() != begin:
                date["begin"] = begin.strip()
                begin = date["begin"]
            date_is_iso(begin)
        end = date.get("end")
        if end:
            if end.strip() != end:
                date["end"] = end.strip()
                end = date["end"]
            date_is_iso(end)
        return date
    except DateException as e:
        raise e


def find_timestamp(client, tree):
    for ao in tree:
        if ao.get("dates"):
            if ao["dates"][0].get("begin"):
                if ao["dates"][0]["begin"].endswith("T00:00:00+00:00"):
                    print(ao["uri"])


def update_timestamp(client, tree):
    for ao in tree:
        if ao.get("dates"):
            if ao["dates"][0].get("begin"):
                begin_string = ao["dates"][0]["begin"]
                if begin_string.endswith("T00:00:00+00:00"):
                    new_string = begin_string.replace("T00:00:00+00:00", "")
                    ao["dates"][0]["begin"] = new_string
                    client.aspace.client.post(ao["uri"], json=ao)


class TreeUpdater:
    """Updates all children in a resource's tree."""

    def __init__(self):
        self.config_file = "local_settings.cfg"
        self.config = ConfigParser()
        self.config.read(self.config_file)
        self.as_client = ArchivesSpaceClient(
            self.config["ArchivesSpace"]["baseurl"],
            self.config["ArchivesSpace"]["username"],
            self.config["ArchivesSpace"]["password"],
        )

    def check_children(self):
        # TODO: do we want to run this every time? do we want to run this maybe over the weekend or on demand?
        children = self.as_client.get_all_children(self.resource)
        count = 0
        for child in children:
            count += 1
            if count % 500 == 0:
                logging.info(f"{count} child - {child['display_string']}")
            fields_with_whitespace = leading_trailing(child)
            for field in fields_with_whitespace:
                self.as_client.update_aspace_field(child, field, child[field].strip())
                child = self.as_client.get_json_response(child["uri"])
                logging.info(f"{child['display_string']} stripped of whitespace")
            if child.get("title"):
                without_linebreaks = (
                    child["title"].replace("\r\n", " ").replace("\n", " ")
                )
                if child["title"] != without_linebreaks:
                    self.as_client.update_aspace_field(
                        child, "title", without_linebreaks
                    )
                    child = self.as_client.get_json_response(child["uri"])
                    logging.info(f"Line breaks removed from {child['display_string']}")
            new_dates = []
            dates = child["dates"]
            if dates:
                try:
                    for date in dates:
                        date = check_date(date)
                        new_dates.append(date)
                    if new_dates != dates:
                        logging.info(f"{child['display_string']} dates updated")
                        self.as_client.update_aspace_field(child, "dates", new_dates)
                        child = self.as_client.get_json_response(child["uri"])
                except DateException as e:
                    raise e
