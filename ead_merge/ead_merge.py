import subprocess
import re
import os.path
import GoogleSheetAPITools as gs


def main():

    saxon_path = 'saxon-9.8.0.12-he.jar'
    xslt1_path = 'ead_merge.xsl'
    xslt2_path = 'ead_cleanup.xsl'


    data_folder1 = '/path/to/exported/legacy/ead/files'
    data_folder2 = '/path/to/as/exported/ead'
    output_folder = '/path/to/output/folder'

    the_sheet='1js0KawsDP1CIwTcYKdqM0XftPCTPgPrB2H80xdgaKlc'

    the_tab='migrate-grid'
    default_range = str(the_tab + '!A1:Z1390')


    try:
        print("Gathering data from spreadsheet...")
        the_mig_data = get_migration_grid(the_sheet, default_range)
    except:
        print("*** Error: there was a problem collecting data from the spreadsheet.***")
        quit()


    for a_record in the_mig_data:

        the_bibid = a_record.pop(0)
        the_rel_path = a_record.pop(0)
        the_flags = a_record

        print('BibID: ' + the_bibid)

        the_params = ['asXMLFolder=' + data_folder2 + ' ']
        for a_flag in the_flags:
            the_params.append('m_' + a_flag + '=Y')
        the_params = ' '.join(the_params)

        the_path1 = str(data_folder1 + '/'+ the_rel_path)
        the_path2 = str(data_folder2 + '/'+ the_bibid + '_ead.xml')

        # Check to see if the two files exist before processing. 
        if (not(os.path.isfile(the_path1))): 
            print('*** Error: File ' + the_path1+ ' not found! ***')
            continue

        if (not(os.path.isfile(the_path2))): 
            print('*** Error: File ' + the_path2+ ' not found! ***')
            continue 

        out_file = str(output_folder + '/' + the_bibid + '_MERGED-CLEAN_ead.xml')
        
        print('Processing file: ' + the_rel_path + " to: " + out_file + ' with params: ' + the_params)

        saxon_process_pipe(saxon_path, the_path1, xslt1_path, xslt2_path, out_file, the_params, ' ')


    quit()


def get_migration_grid(theSheet,theRange):

    the_data = []

    x = gs.getSheetData(theSheet, theRange)

    the_values = x["values"]
    the_heads = the_values[0]

    for a_row in the_values:
        my_bibid = a_row[0]
        my_path = a_row[3]
        my_row_data = [my_bibid,my_path]

        for index, item in enumerate(a_row):
            if item == "X":
                the_name = the_heads[index]
                my_row_data.append(the_name)
        
        the_data.append(my_row_data)
    del the_data[0:2]
    return the_data


def saxon_process(saxonPath, inFile, transformFile, outFile, theParams):
    cmd = 'java -jar ' + saxonPath + ' ' + inFile  + ' ' + transformFile + ' ' + theParams + ' ' + '--suppressXsltNamespaceCheck:on' + ' > ' + outFile
    p = subprocess.Popen([cmd], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    result = p.communicate()
    return result[0]


def saxon_process_pipe(saxonPath, inFile, transformFile1, transformFile2, outFile, theParams1, theParams2):
    # This is a 2-step transform; stdout from first is input to second.
    # TODO: redo this in Xproc?
    cmd = 'java -jar ' + saxonPath + ' ' + inFile  + ' ' + transformFile1 + ' ' + theParams1 + ' ' + '--suppressXsltNamespaceCheck:on' + ' | java -jar ' + saxonPath + ' - ' + ' ' + transformFile2 + ' ' + theParams2 + ' ' + '--suppressXsltNamespaceCheck:on' + ' > ' + outFile

    print('Executing command: ' + cmd)
    p = subprocess.Popen([cmd], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    result = p.communicate()
    return result[0]


if __name__ == '__main__':
    main()
