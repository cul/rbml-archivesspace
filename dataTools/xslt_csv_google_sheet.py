import subprocess
import csv
from sheetFeeder import dataSheet

# Script to transform an xml (e.g., EAD) file to delimited text using a designated XSLT file, and send the data to a google sheet using sheetFeeder.

def main():

    # Set path to Saxon processor
    saxon_path = 'saxon-9.8.0.12-he.jar'

    # Set path to XSLT
    the_xslt = 'ead_tbm_csv.xsl'
    the_infile = '/path/to/source/xmlfile_ead.xml'
    the_outpath = '/path/to/output_file.txt'


    # Set Google Sheet id and range
    the_sheet = dataSheet('LmguZqjAk23OPHeDmyy2wvZiXGaiLz7','Test!A:Z')


    # Parameters to pass to XSLT:
    params = {
        'series_scope':7, # series to process; 0 = all series
        'subject':'AUDIO RECORDINGS' # static label for content
    }


    # generate a parameter string from params
    param_str = ''
    for key, value in params.items():
        value = str(value).replace(' ','\ ')
        param_str += str(key) + '=' + str(value) + ' '


    # Send to Saxon with parameters
    saxon_process(saxon_path,the_infile,the_xslt,the_outpath,theParams=param_str)


    # Send result csv to Google Sheet
    y = the_sheet.importCSV(the_outpath, delim='|')

    print(y)




def saxon_process(saxonPath, inFile, transformFile, outFile, theParams=' '):
    cmd = 'java -jar ' + saxonPath + ' ' + inFile  + ' ' + transformFile + ' ' + theParams + ' ' + '--suppressXsltNamespaceCheck:on' + ' > ' + outFile
    p = subprocess.Popen([cmd], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    result = p.communicate()
    return result[0]




if __name__ == '__main__':
    main()
