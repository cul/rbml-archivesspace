# Migration Scripts

Steps taken to clean collection-level archival MARC records exported from Voyager, prior to import into AS

Step 1: Run XSLT cleanup.xsl across all five xml files. (cleanupOne.xsl)
245$a trailing comma
245$f trailing comma
300 a/f cleanup
520 indicator cleanup
590 to 500 / 590 BAR to 852$j

Step 2: Use the following xpath  piped find-and-replace in project
mode in Oxygen across all five files:

xmlns=""
//record

..
//datafield[@tag='555']

right paren, left paren, ft / feet, in. / inches, v. / volumes, p.
/pages, comma, &, -, approximately, approx., circa, ca.
//datafield[@tag='300'] (NOT PERIOD!!!!)

[,]
//datafield[@tag='245']/subfield[@code='h']

nd/undated
//datafield[@tag='245']/subfield[@code='f'] |
//datafield[@tag='245']/subfield[@code='g']
 
Step 3:
Added to cleanupTwo stylesheet on 5/28:
*Instead of: right paren, left paren, bulk, ca., circa, [, ], nd / undated, period
//datafield[@tag='245']/subfield[@code='f'] |
//datafield[@tag='245']/subfield[@code='g']
Did a string replace.
*Remove 856s with
http://www.columbia.edu/cu/lweb/services/preservation/publicationsPolicy.html
*Get rid of extraneous second 555 field.
 
Step 4:  Load all into project, and F+R
<subfield code="f"/>
with
<subfield code="f">undated</subfield>