# Script to bulk suppress unused enumeration values, e.g., unused extent types that were unwanted byproducts of import.
# Requirements:
# * TSV file of scraped values from an enumeration page, showing which have "Not used" in 3rd column. 
# * ASFunctions library and API dependencies.
# To scrape data from an enumeration html, use regex like:
# (?s) *<tr>.*?<a class="btn btn-xs .*? data-method="post" href="/enumerations/\d+/enumeration_value/(\d+)\?position=\d+">.*?<div class="enum-value-search" data-url=".*?value%22%3A%22(.*?)%22%2C.*?"><a href=".*?">(.*?)</a>.*?</tr>
# Extract results as \1\t\2\t\3

import ASFunctions as asf
import csv
from pprint import pprint
import json



def main():

    server='Prod'
    asf.setServer(server)


    enum_num = 14 # extent_extent_type enumeration
    extent_data = asf.getEnumeration(enum_num)

    extent_usage_csv = '/Users/dwh2128/Documents/ACFA/TEST/ACFA-111-extents-cleanup/extent-values-prod3.tsv'

    output_folder = 'output/enumerations'

    # Paths for reporting before/after data
    out_path_old = output_folder + '/' + str(enum_num) + 'PROD_old.json'
    out_path_new = output_folder + '/' + str(enum_num) + 'PROD_new.json'


    # Save copy of existing object
    print('Saving data to ' + out_path_old + '....')
    with open(out_path_old, "w+") as f:
        f.write(extent_data)


    # Load list from csv
    csv.register_dialect('my_dialect', delimiter='\t', quoting=csv.QUOTE_NONE)
    data = []
    with open(extent_usage_csv) as the_csv_data:
        for row in csv.reader(the_csv_data, 'my_dialect'):
            data.append(row)

    # A list of ids of extent values to remove
    unused_extents = [ x[0] for x in data if x[2] == 'Not used.' ]


    for e in unused_extents:
        print('suppressing ' + str(e))
        # mode='suppress' to suppress, mode='unsuppress' to unsuppress
        post = asf.suppressEnumerationValue(e,mode='suppress')
        print(post)

    extent_data_new = asf.getEnumeration(enum_num)

    # Save updated object
    print('Saving data to ' + out_path_new + '....')
    with open(out_path_new, "w+") as f:
        f.write(extent_data_new)



if __name__ == '__main__':
    main()

