import google.oauth2.credentials
from googleapiclient.discovery import build


class GoogleSheetsClient(object):
    def __init__(
        self, access_token, refresh_token, client_id, client_secret, spreadsheet_id
    ):
        """Sets up client to work with a spreadsheet using the Google Sheets API.

        Args:
            access_token (str): OAuth 2.0 access token
            refresh_token (str): OAuth 2.0 refresh token
            client_id (str): OAuth 2.0 client ID
            client_secret (str): OAuth 2.0 client secret
            spreadsheet_id (str): the spreadsheet to request
        """
        credentials = google.oauth2.credentials.Credentials(
            access_token,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            scopes=["https://www.googleapis.com/auth/spreadsheets"],
        )
        self.service = build("sheets", "v4", credentials=credentials)
        self.spreadsheet_id = spreadsheet_id

    def get_sheet_info(self):
        """Return data about a spreadsheet."""
        request = self.service.spreadsheets().get(
            spreadsheetId=self.spreadsheet_id, includeGridData=False
        )
        response = request.execute()
        return response

    def get_sheet_tabs(self):
        """Return a list of tab names for a given sheet."""
        sheet_data = self.get_sheet_info()
        sheet_tabs = [s["properties"]["title"] for s in sheet_data["sheets"]]
        return sheet_tabs


class DataSheet(GoogleSheetsClient):
    def __init__(
        self,
        access_token,
        refresh_token,
        client_id,
        client_secret,
        spreadsheet_id,
        data_range,
    ):
        """Work with a range in a spreadsheet using Google Sheets API.

        Args:
            access_token (str): OAuth 2.0 access token
            refresh_token (str): OAuth 2.0 refresh token
            client_id (str): OAuth 2.0 client ID
            client_secret (str): OAuth 2.0 client secret
            spreadsheet_id (str): the spreadsheet to request
            data_range (str): the A1 notation of a range to search for a logical table of data
        """
        super(DataSheet, self).__init__(
            access_token,
            refresh_token,
            client_id,
            client_secret,
            spreadsheet_id,
        )
        self.data_range = data_range

    def get_sheet_data(self):
        """Return sheet data as list of rows."""
        request = (
            self.service.spreadsheets()
            .values()
            .get(
                spreadsheetId=self.spreadsheet_id,
                range=self.data_range,
                valueRenderOption="FORMATTED_VALUE",
                dateTimeRenderOption="SERIAL_NUMBER",
            )
        )
        the_data = request.execute()
        response = the_data["values"] if "values" in the_data else []
        return response

    def clear_sheet(self):
        clear_values_request_body = {
            # TODO: Add desired entries to the request body.
        }
        request = (
            self.service.spreadsheets()
            .values()
            .clear(
                spreadsheetId=self.spreadsheet_id,
                range=self.data_range,
                body=clear_values_request_body,
            )
        )
        response = request.execute()
        return response

    def append_sheet(self, data):
        """Append rows to end of detected table.

        Note: the range is only used to identify a table; values will be appended at the end of table, not at end of range.
        https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/append
        https://developers.google.com/sheets/api/reference/rest/v4/ValueInputOption
        https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/append#InsertDataOption
        """
        request = (
            self.service.spreadsheets()
            .values()
            .append(
                spreadsheetId=self.spreadsheet_id,
                range=self.data_range,
                valueInputOption="USER_ENTERED",
                insertDataOption="OVERWRITE",
                body={"values": data},
            )
        )
        response = request.execute()
        return response
