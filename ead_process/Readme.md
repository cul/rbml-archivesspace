# rbml-archivesspace/ead_process

ead_process.py is a script to select data from two different XML sources, and populate a Google Sheet to review individual elements from both side by side. This was developed as a pre-migration QC process for CUL migration of legacy finding aids into ArchivesSpace.

Dependencies:

* sheetFeeder - https://github.com/dwhodges2/sheetFeeder
* lxml
* re

Variables to assign:
* data_folder1: relative path to one set of XML
* data_folder2: relative path to second set of XML
* file_list1 and file_list2: plain-text lists of filenames (with paths relative to above as needed)
* the_sheet: id of Google Sheet
* range1 and range2: names of tab in the_sheet and range sufficient to erase/replace everything
* legacyQs and asQs: 2 dicts of tag names and Xpath expressions to reach them (namespaced, as needed); the keys will become head in the respective sheets



Optionally, a "secrets" file can be used to privately store the id of a Google Sheet to interact with.

