import requests
import os
from sheetFeeder import dataSheet
import csv


def main():

    my_name = __file__
    script_name = os.path.basename(my_name)

    # This makes sure the script can be run from any working directory and still find related files.
    my_path = os.path.dirname(__file__)

    the_output_sheet = dataSheet(
        '1sjpjLt_I54h9l-ABwueYdN6xVAm01S6rKZB3BgMQv3k', 'output!A:Z')

    # The table of xlinks with format:
    # bibid|container_id|href|title|text
    aCSV = os.path.join(my_path, 'output/output_all_f.txt')

    with open(aCSV) as the_csv:
        the_data = [row for row in csv.reader(the_csv, delimiter='|')]

    the_heads = the_data.pop(0)
    the_heads += ['STATUS', 'REDIRECT_LOCATION', 'REDIRECT_STATUS']
    the_new_data = [the_heads]

    for a_row in the_data:
        print(a_row)
        if 'clio.columbia.edu' in a_row[2]:
            print('Skipping CLIO record ' + a_row[2])
        else:
            response = get_response(a_row[2])
            if response['status'] != 200:
                new_row = a_row
                while len(new_row) < 5:
                    new_row.append("")
                new_row.append(response['status'])
                if 'location' in response:
                    redirect_response = get_response(response['location'])
                    new_row += [response['location'],
                                redirect_response['status']]

                print(new_row)
                the_new_data.append(new_row)

    # Write output to sheet.
    the_output_sheet.clear()
    the_output_sheet.appendData(the_new_data)


def get_response(url):
    try:
        x = requests.head(url)
        status = x.status_code

        if status in [301, 302]:
            location = x.headers['Location']
        else:
            location = ""

    # Note: RequestException is the parent of all other named exceptions and includes them.
    except requests.exceptions.RequestException as e:
        status = "ERROR: " + str(e)
        location = ""

    response = {'status': status}
    if location:
        response['location'] = location
    return response


if __name__ == "__main__":
    main()
