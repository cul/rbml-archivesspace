import sheetFeeder as gs
import subprocess
import re
import os


# Script to extract information from EAD via XSLT and report as rows in a Google sheet.

# Requirements:
#  • sheetFeeder (https://github.com/dwhodges2/sheetFeeder)
#  • XSLT that produces a pipe (|) delimited text row for each processed file.
#  • XSLT should also return a pipe-delimeted header row when run with param "header" = "Y". 
#  • Saxon, preferably v9 or better, to run XSLT transform.
#  • A collection of XML files.
#  • A Google Sheet with necessary permissions to write to.

def main():

    data_folder = 'path/to/xml/files'
    the_sheet = '[sheet id]' # Google sheet id
    the_range = 'data!A:Z' # Range to write to
    the_xslt = 'path/to/xslt/file'
    saxon_path='saxon-9.8.0.12-he.jar'

    # Build the data set.
    the_data =build_xslt_report(data_folder,the_xslt,saxon_path)

    # Clear the sheet and write data.
    gs.sheetClear(the_sheet,the_range)
    print('Writing data to Google Sheet ...')
    gs.sheetAppend(the_sheet,the_range,the_data)

    print('Done!')






def build_xslt_report(files_path,xslt_path,saxon_path):
    # Build list of files to process.
    the_file_paths = []
    for root, dirs, files in os.walk(os.path.abspath(files_path)):
        for file in files:
            the_file_paths.append(os.path.join(root, file))

    the_data = []

    # send any file with header=Y param to retrieve the headers as the first row.
    the_headers = saxon_process(saxon_path, the_file_paths[0], xslt_path, "header='Y'")

    the_headers = delim_to_list(the_headers,'|')
    the_data.append(the_headers)

    cnt = 0
    for f in the_file_paths:
        cnt = cnt + 1
        print(str(cnt) + " : processing" + f + "...")
        x = saxon_process(saxon_path, f, xslt_path, ' ')
        the_row = delim_to_list(x,'|')
        the_data.append(the_row)

    return the_data



def saxon_process(saxonPath, inFile, transformFile, theParams):
    cmd = 'java -jar ' + saxonPath + ' ' + inFile  + ' ' + transformFile + ' ' + theParams + ' ' + '--suppressXsltNamespaceCheck:on' 
    p = subprocess.Popen([cmd], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    result = p.communicate()
    return result[0]



def delim_to_list(the_str,the_delim):
        x = the_str.strip().decode('utf-8')
        # x = x
        the_list = x.split(the_delim)
        return the_list


if __name__ == '__main__':
    main()

