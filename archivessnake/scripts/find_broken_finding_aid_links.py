from configparser import ConfigParser

import requests
from utils.google_sheets_client import DataSheet


class BrokenFindingAidLinks(object):
    def __init__(self):
        self.config = ConfigParser()
        self.config.read("local_settings.cfg")
        self.resource_sheet = DataSheet(
            self.config["Google Sheets"]["access_token"],
            self.config["Google Sheets"]["refresh_token"],
            self.config["Google Sheets"]["client_id"],
            self.config["Google Sheets"]["client_secret"],
            "1Rd8cxBakujwmgi7crZ2mJisruAS-HSrHprfJqDyAgjg",
            "Sheet1!A:Z",
        )
        self.links_sheet = DataSheet(
            self.config["Google Sheets"]["access_token"],
            self.config["Google Sheets"]["refresh_token"],
            self.config["Google Sheets"]["client_id"],
            self.config["Google Sheets"]["client_secret"],
            "1sHH97QRIJctzWMbH_Gz7jx7NNSV10LkN12p4kn6nr5Q",
            "Sheet1!A:Z",
        )

    def get_all_ead_links(self):
        data_to_write = []
        headings = [
            "uri",
            "bibid",
            "title",
            "published",
            "link",
            "status code",
            "reason",
            "clio_link",
            "clio_response",
        ]
        data_to_write.append(headings)
        list_of_resources = self.resource_sheet.get_sheet_data()[1:]
        for resource in list_of_resources:
            ead_link = resource[9]
            if ead_link:
                ead_link = ead_link.strip()
                response = self.get_link_response(ead_link)
                try:
                    if response.status_code != 200 or "clio" in response.url:
                        clio_link = f"https://clio.columbia.edu/catalog/{resource[2]}"
                        clio_response = self.get_link_response(clio_link)
                        row_data = [
                            resource[1],
                            resource[2],
                            resource[3],
                            resource[4],
                            ead_link,
                            response.status_code,
                            response.reason,
                            clio_link,
                            clio_response.status_code,
                        ]
                        data_to_write.append(row_data)
                except Exception:
                    pass
        self.links_sheet.append_sheet(data_to_write)

    def get_link_response(self, ead_link, allow_redirects=True):
        try:
            response = requests.get(ead_link, allow_redirects=allow_redirects)
            return response
        except Exception as e:
            print(e, ead_link)
