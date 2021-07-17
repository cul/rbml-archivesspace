# Script to copy the latest EAD files and parse, validate them against schema, and evaluate them with XSLT audit stylesheet. Output is piped to a google sheet report using sheetFeeder.


import os
import re
import datetime
from sheetFeeder import dataSheet
import dcps_utils as util
import digester  # for generating composite digest of report info.


def main():

    MY_NAME = __file__
    global SCRIPT_NAME
    SCRIPT_NAME = os.path.basename(MY_NAME)

    # This makes sure the script can be run from any working directory and still find related files.
    MY_PATH = os.path.dirname(__file__)

    sheet_id = '1Ltf5_hhR-xN4YSvNWmPX8bqJA1UjqAaSjgeHBr_5chA'

    parse_sheet = dataSheet(sheet_id, 'parse!A:Z')  # Test
    validation_sheet = dataSheet(sheet_id, 'schema!A:Z')  # Test
    eval_sheet = dataSheet(sheet_id, 'eval!A:Z')  # Test

    # This is a dupe for other reporting
    # the_data_sheet2 = dataSheet(
    #     "198ON5qZ3MYBWPbSAopWkGE6hcUD8P-KMkWkq2qRooOY", "validation!A:Z")

    now1 = datetime.datetime.now()
    start_time = str(now1)
    end_time = ""  # set later

    ################################
    #
    # Rsync files from web application to storage directory
    #
    ################################

    print("====== Syncing files from production cache... ======")
    print(" ")

    # keyPath = "/home/ldpdserv/.ssh/id_dsa"
    fromPath = (
        "ldpdserv@ldpd-nginx-prod1:/opt/passenger/ldpd/findingaids_prod/caches/ead_cache"
    )
    toPath = "/cul/cul0/ldpd/archivesspace/"

    myOptions = "--exclude 'clio*'"

    x = util.rsync_process(fromPath, toPath, myOptions)
    print(x)

    print(" ")

    ################################
    #
    # Perform validation reporting
    #
    ################################

    schema_path = os.path.join(MY_PATH, "../schemas/cul_as_ead.rng")

    csv_out_path = os.path.join(MY_PATH, "temp_out.txt")

    xslt_path = os.path.join(MY_PATH, "../schemas/cul_as_ead2.xsl")  # test

    data_folder = "/cul/cul0/ldpd/archivesspace/ead_cache"
    # data_folder = "/Users/dwh2128/Documents/ACFA/exist-local/backups/cached_eads/ead_rsync_test"  # test
    # data_folder = '/cul/cul0/ldpd/archivesspace/test/ead'  # for testing

    # Use in notification email to distinguish errors/warnings
    icons = {
        "redx": "\U0000274C",
        "exclamation": "\U00002757",
        "warning": "\U000026A0\U0000FE0F",
        "qmark": "\U00002753",
    }

    # check for malformed xml. If there is, then don't do further validation because it will fail once it hits an unparseable file.

    print(" ")
    print("====== Checking well-formedness ... ======")

    parse_errs = []
    try:
        x = util.run_bash('xmllint ' + data_folder +
                          '/* --noout', errorPrefix='PARSE')
        # print(x)
        log_it("All files well-formed.")

    except Exception as e:
        if 'PARSEERROR' in str(e):
            parse_errs = [
                msg_parse(l, icons['redx'])
                for l in str(e).splitlines()
                if 'as_ead' in l]

            # print(parse_errs)
        for e in get_unique_bibids(parse_errs):
            log_it(icons['redx'] + " " +
                   str(e) + " has parsing errors.")

    parse_err_cnt = get_unique_count(parse_errs)

    if parse_errs:

        log_it('There were ' + str(parse_err_cnt) +
               ' unparseable records! Validation of files could not be completed. Fix syntax and run script again.')
        parse_sheet.clear()
        parse_sheet.appendData(parse_errs)
        quit()

    # No parsing errors, so proceed...
    parse_sheet.clear()

    print(" ")
    print("====== Validating files... ======")

    # Validate against schema. Xargs batches files so they won't exceed
    # limit on arguments with thousands of files.

    x = util.run_bash('find ' + data_folder +
                      ' -name "as_ead*"  | xargs -L 128 java -jar ' +
                      util.config['FILES']['jingPath'] + ' -d ' + schema_path, errorPrefix='JING')

    schema_errs = [
        msg_parse(l, icons['exclamation'])
        for l in str(x).splitlines()
        if 'as_ead' in l]

    schema_err_cnt = get_unique_count(schema_errs)

    if schema_errs:
        for e in get_unique_bibids(schema_errs):
            log_it(icons['exclamation'] + " " +
                   str(e) + " has validation errors.")
    else:
        log_it("All files are valid.")

    validation_sheet.clear()
    validation_sheet.appendData(schema_errs)

    print(" ")
    print("====== Evaluating with XSLT ... ======")

    try:
        x = util.saxon_process(xslt_path, xslt_path, csv_out_path,
                               theParams='filePath=' + data_folder)
        eval_sheet.clear()
        eval_sheet.importCSV(csv_out_path, delim='|')

    except Exception as e:
        if "SAXON ERROR" in str(e):
            print("Cancelled!")

    evals = eval_sheet.getDataColumns()[0]
    eval_bibs = set(evals)
    warnings_cnt = len(eval_bibs)

    if evals:
        log_it(icons['warning'] + " " + str(len(evals)) +
               " warnings in " + str(warnings_cnt) + " files.")
    else:
        log_it("There were no problems found!")

    the_tabs = validation_sheet.initTabs

    now2 = datetime.datetime.now()
    end_time = str(now2)

    if "log" in the_tabs:
        log_range = "log!A:A"
        my_duration = str(now2 - now1)

        the_log = (
            "EADs from "
            + data_folder
            + " evaluated by "
            + schema_path
            + " and "
            + xslt_path
            + ". Parse errors: "
            + str(parse_err_cnt)
            + ". Schema errors: "
            + str(schema_err_cnt)
            + ". XSLT warnings: "
            + str(warnings_cnt)
            + ". Start: "
            + start_time
            + ". Finished: "
            + end_time
            + " (duration: "
            + my_duration
            + ")."
        )

        # today = datetime.datetime.today().strftime('%c')
        dataSheet(validation_sheet.id, log_range).appendData([[the_log]])
    else:
        print("*** Warning: There is no log tab in this sheet. ***")

    print(" ")

    # print(the_log)

    log_it("Files with parse errors: " + str(parse_err_cnt))
    log_it("Files with schema errors: " + str(schema_err_cnt))
    log_it("Files with warnings: " + str(warnings_cnt))

    print(" ")

    exit_msg = "Script done. Check report sheet for more details: " + validation_sheet.url
    log_it(exit_msg)

    quit()


def msg_parse(_str, icon):
    # Parses errors/warnings from Jing or XMLLint into
    # array of [[bibid, message], [bibid, message]...]
    pattern = re.compile(r'^.*?as_ead_ldpd_(\d+)\.xml:(.*)$')
    r = pattern.search(_str)
    try:
        return [r.group(1), icon + " " + r.group(2)]
    except:
        return []


def log_it(msg):
    print(msg)
    digester.post_digest(SCRIPT_NAME, msg)


def get_unique_count(_array):
    return len(get_unique_bibids(_array))


def get_unique_bibids(_array):
    return {p[0] for p in _array}


if __name__ == "__main__":
    main()
