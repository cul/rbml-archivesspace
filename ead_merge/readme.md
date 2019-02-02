ead_merge.py is a script to merge legacy EAD XML with ArchivesSpace-exported EAD XML. The use case is when collection-level data is managed in AS but archival description is managed elsewhere, and the objective is to create EADs ready to import into AS. 

Prerequisites: 
 * Python subprocess module
 * Python re module (regex)
 * GoogleSheetAPITools - https://github.com/dwhodges2/googlesheet_tools
 * A Google sheet prepared with non-dsc elements marked to migrate (see screenshot) and relative file paths for legacy EAD files
 * Saxon 9-HE or other XSLT 2.0 processor
 * A folder of legacy XML files with BibIDs
 * A folder of corresponding AS-exported EAD files, named by BibID

In addition to copying the dsc from legacy into the new document, the XSLT can optionally migrate specific elements per the spreadsheet (e.g., revisiondesc, abstract, bioghist, etc.), replacing the corresponding elements from the AS export. Additional templates can be added to make corrections or manipulations as needed, with mode="legacy" targeting elements from the legacy source tree, and mode="asead" targeting elements from the AS source tree. 

TODO: 
 * complete list of parameters allowed to pass to stylesheet.
 * document parameter usage.
 * add Xspec unit testing.
