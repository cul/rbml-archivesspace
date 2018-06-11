# Authority Control

All scripts that call the API require a secrets.py file, formatted as follows:

~~~~
baseURL='https://{API_endpoint}'
user='{username}'
password='{password}'
~~~~

This is a series of scripts for a proposed authority control workflow.

***CLEAN UP PRIOR TO MATCHING NUMBERS***

Extract list of duplicate agents from AS
Extract csv of target and victom AS IDs
Run mergeCreators.py (works, currently written only for people) to dedupe


***INITIAL LOAD OF AUTHORITY NUMBERS***

1) API call to ASpace to extract json files or all subjects and agents
	getSubjects.py etc. (works)

will need to address duplicate records with different sources caused by discrepancy in the 100/600 import syntax; merge.py to combine string-matched records?

2 alt) Skip 2 and 3; script the call in 4 directly against the json (for-each json object that has a source LC or naf)? 

2a) Load json export of agents  / subjects in Basex
	(works)

2b) Extract uri, sort name, and source using xquery:

	xquery version "3.0";

	for $person in /json/_

	let $pm:= $person/names/_/sort__name
	let $uri:= $person/uri
	let $source:= $person/names/_/source
	return
	<r>
	<u>{data($uri)}</u>
	<s>{data($source)}</s>
	<p>{data($pm)}</p>
	</r>

	(works)

3) Open in Excel, filter out local and other non lc/naf sources, and save as tsv
	(maybe could skip this step by putting out original tsv from basex)
	(works)

4) Match strings against authority database to get LC authority numbers
	Variety of ways to do this
		Hit the VIAF API, but pull LC back (names only unfortunately)
			getViaf.py 
			(works; 3.5 hours)
			Matched 6934 of 8659. Reason: some aren't in lc; and probably some VIAF weirdness too.  

		Try to hit the LC api; two ways (http://id.loc.gov/techcenter/searching.html):
			id.loc.gov/authorities/{scheme_name}/label/{term}  -> returns as 202 the url with the auth no
				or
			id.loc.gov/search/?q=aLabel:"Tewksbury, Donald George, 1894-1958" -> returns the record; we'd need to request the right data
			getLC.py (tested, but not at scale)

		Do it locally?

		IN ANY CASE REVIEW THESE BEFORE LOAD

5) Load authority numbers back into the json records.
	insertNewDataIntoJSON.py (needs to be modified for this initial load to match on string and load auth numbers; not a problem)

6) Post the whole shebang back in. Need to post the whole thing back in, it appears.
	use postViaf.py (works) 

***ONGOING AUTHORITY***

Instead of using URI, match on authID. Write out where there is no match; either manually add auth nos, or have it match on string.
Ensure nothing else is going on, because otherwise lock numbers will not match

1) API call to ASpace to get fresh extract of json files on all subjects and agents
	getSubjects.py etc. (works)

2) Extract csv with authno, primary name, sort name, anything else we want from the authority records from LTI (MARCedit, or pymarc, or some string manipulation; should be easy)

3) Script to match csv to json record on authority number, and write in primary name, sort name, etc. Write out modified json files only.
	insertNewDataIntoJSON.py (works)

4) Post the updated json back in. Need to post the whole thing back in, not just certain fields.  However, we could add a note during 3 for modified records, and only post those (or somehow otherwise limit to only touched records)
	use postViaf.py (works)