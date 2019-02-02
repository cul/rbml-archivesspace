import subprocess
import re
import GoogleSheetAPITools as gs


def main():

    saxon_path = 'saxon-9.8.0.12-he.jar'
    xslt1_path = '/Users/dwh2128/Documents/ACFA/TEST/ASI-49/ead_merge.xsl'

    data_folder1 = '/Users/dwh2128/Documents/ACFA/exist-local/backups/for_migration/ead-export-20190123'
    data_folder2 = '/Users/dwh2128/Documents/git/python_sandbox/ead_process/xml'
    output_folder = 'XML_out'

    the_sheet='1js0KawsDP1CIwTcYKdqM0XftPCTPgPrB2H80xdgaKlc'
    the_tab='migrate-grid'
    default_range = str(the_tab + '!A1:Z10')


    the_mig_data = get_migration_grid(the_sheet, default_range)

    for a_record in the_mig_data:

        try:
            the_bibid = a_record.pop(0)
            the_rel_path = a_record.pop(0)
            the_flags = a_record
    
            the_params = ['asXMLFolder=' + data_folder2 + ' ']
            for a_flag in the_flags:
                the_params.append('m_' + a_flag + '=Y')
            the_params = ' '.join(the_params)

            the_path = str(data_folder1 + '/'+ the_rel_path)
            out_file = str(output_folder + '/' + the_bibid + '_MERGED_ead.xml')

            print('Processing file: ' + the_rel_path + " to: " + out_file + ' with params: ' + the_params)

            x = saxon_process(saxon_path, the_path, xslt1_path, out_file, the_params)

        except:
            print("*** Error, could not process record ***")

    quit()



def get_migration_grid(theSheet,theRange):

    x = gs.getSheetData(theSheet, theRange)

    the_values = x["values"]
    the_heads = the_values[0]
    the_data = []

    for a_row in the_values:
        my_bibid = a_row[0]
        my_path = a_row[3]
        # print(my_bibid)
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

    #subprocess.call(cmd, shell=True)
    return result[0]


if __name__ == '__main__':
    main()



