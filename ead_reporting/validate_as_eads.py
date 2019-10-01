import subprocess
import csv
import os
import re
import datetime
from sheetFeeder import dataSheet

# Script to transform an xml (e.g., EAD) file to delimited text using a designated XSLT file, and send the data to a google sheet using sheetFeeder.

def main():

    my_name = __file__

    # This makes sure the script can be run from any working directory and still find related files.
    my_path = os.path.dirname(__file__)


    now1 = datetime.datetime.now()
    start_time = str(now1)
    end_time = '' #set later


    print('Script ' + my_name + ' begun at ' + start_time + '. ')


    # The Google Sheet to send data to
    the_data_sheet = dataSheet('1tQY9kR5YOh1e7i4dVRsl_GMxpNnUgCkb5X8qJQBAsG0','validation!A:Z')

    # Set path to schema validator (Jing)
    jing_path = os.path.join(my_path, "../resources/jing-20091111/bin/jing.jar")

    schema_filename = 'cul_as_ead.rng'
    schematron_filename = 'cul_as_ead.sch'
    schema_path = os.path.join(my_path, schema_filename)
    schematron_path = os.path.join(my_path,schematron_filename)


    # Use in notification email to distinguish errors/warnings
    icons = {'facesmiling':'\U0001F600',
            'redx':'\U0000274C',  # use for parse errors
            'exclamation':'\U00002757',
            'warning':'\U000026A0',  # use for schema validation errors
            'qmark':'\U00002753'}


    data_folder = '/cul/cul0/ldpd/archivesspace/ead_cache'
    # data_folder = '/opt/dcps/archivesspace/test/ead' # for testing


    # Load files from directory into a list
    the_file_paths = []
    for root, dirs, files in os.walk(os.path.abspath(data_folder)):
        for file in files:
            the_file_paths.append(os.path.join(root, file))

    # The column heads for the report spreadsheet
    the_heads = ['file','well-formed?','valid?','schema output','schematron output', 'warning type']

    the_results = []

    the_results.append(the_heads)

    # counters
    parse_errors = 0
    validation_errors = 0
    sch_warnings = 0

    for a_file in the_file_paths:
        the_file_data = []
        file_name = a_file.split('/')[-1]
        # print('Processing ' + file_name)
        validation_result = jing_process(jing_path, a_file, schema_path)

        if 'fatal:' in validation_result:
            print(icons['redx'] + ' FATAL ERROR: ' + file_name + ' could not be parsed!')
            wf_status = False
            validation_status = False
            parse_errors += 1
        else:
            wf_status = True
            if 'error:' in validation_result:
                validation_status = False
                print(icons['warning'] + ' ERROR: ' + file_name + ' contains validation errors.')
                validation_errors +=1
            else:
                validation_status = True

        if validation_result:
            validation_result_clean = clean_output(validation_result,incl_types=False)[0]
        else:
            validation_result_clean = validation_result


        if wf_status == False:
            schematron_result_clean = '-'
            warning_types = []

        else:
            # print('Result from schematron: ')
            schematron_result = jing_process(jing_path,a_file, schematron_path)

            if 'error:' in schematron_result:
                print('WARNING: ' + file_name + ' has Schematron rule violations.')
                sch_warnings +=1

            if schematron_result:
                x = clean_output(schematron_result,incl_types=True)
                schematron_result_clean = x[0]
                warning_types = x[1]
            else:
                schematron_result_clean = ''
                warning_types = ''


        the_file_data = [file_name,wf_status,validation_status,validation_result_clean, schematron_result_clean, ', '.join(warning_types)]

        the_results.append(the_file_data)


    the_data_sheet.clear()
    the_data_sheet.appendData(the_results)


    # generate log and add to log tab, if exists.
    the_tabs = the_data_sheet.initTabs

    now2 = datetime.datetime.now()
    end_time = str(now2)
    my_duration = str(now2 - now1)

    the_log = 'EADs from ' + data_folder + ' evaluated by ' + schema_filename + ' and ' + schematron_filename +  '. Parse errors: ' + str(parse_errors) + '. Schema errors: ' + str(validation_errors) + '. Schematron warnings: ' + str(sch_warnings) + '. Start: ' + start_time  +  '. Finished: ' + end_time + ' (duration: ' + my_duration + ').'


    if 'log' in the_tabs:
        log_range = 'log!A:A'
        # today = datetime.datetime.today().strftime('%c')
        dataSheet(the_data_sheet.id,log_range).appendData([[the_log]])
    else: 
        print('*** Warning: There is no log tab in this sheet. ***')

    print(' ')

    # print(the_log)

    print('Parse errors: ' + str(parse_errors))
    print('Schema errors: ' + str(validation_errors) )
    print('Schematron warnings: ' + str(sch_warnings) )

    print(' ')



    print(' ')
    print('Script done. Check report sheet for more details: ' + the_data_sheet.url )

    quit()



def jing_process(jingPath, filePath, schemaPath):
    # Process an xml file against a schema (rng or schematron) using Jing.
    # Tested with jing-20091111.
    # https://code.google.com/archive/p/jing-trang/downloads
    # -d flag (undocumented!) = include diagnostics in output.
    cmd = 'java -jar ' + jingPath + ' -d ' + schemaPath + ' ' + filePath
    # print(cmd)
    p = subprocess.Popen([cmd], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    result = p.communicate()
    return result[0].decode('UTF-8')


def clean_output(in_str,incl_types=True):
    out_str = in_str
    if incl_types==True:
        # parse diagnostics terms (error types) to new list
        # (the schematron must enclose them in {curly braces} for this to work)
        err_types = re.findall( r'\{(.*?)\}', in_str)
        err_types = list(set(err_types))
        # remove diagnostics strings, as they have been captured above
        out_str = re.sub(r' *\{.*?\}\n?',r'', out_str, flags=re.MULTILINE)
    else:
        err_types = []
    # remove file path from each line, leaving line number
    out_str = re.sub(r'^ */.*?\.xml:(.*)$',r'\1', out_str, flags=re.MULTILINE)
    # cleanup 
    out_str = re.sub(r': error: (assertion failed|report):\s+',r': ', out_str, flags=re.MULTILINE)
    out_str = re.sub(r'\n$',r'', out_str)
    # returns a list in format [<str>,<list>]
    return [out_str,err_types]


# def schema_validate(filePath, schemaPath):
#     # Use xmllint. Has somewhat better error reporting, but won't work for schematron. :(
#     cmd = 'xmllint --noout --relaxng ' + schemaPath + ' ' + filePath
#     p = subprocess.Popen([cmd], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
#     result = p.communicate()
#     return result[1].decode('UTF-8')

if __name__ == '__main__':
    main()
