# rbml-archivesspace/APIFunctions

These scripts interact with the ArchivesSpace API. Current development is focussed on ASFunctions.py, which is intended to be imported as a function library in other scripts. It requires Python 3, while some older individual action scripts are still in Python 2.

Scripts require a `config.ini` file to read URLs and credentials for ASpace servers (most likely, Prod,Dev, and Test). It should be formatted as follows:

~~~~
[PROD]
baseURL = https://your-aspace-domain/api/
baseOAIURL = {OAI URL, eg., https://your-aspace-domain/public/oai}
oaiPrefix = {OAI prefix, e.g., oai:columbia}
user = {username}
password = {password}

[DEV]
(similar to above, for Dev)

[TEST]
(similar to above, for Test)

~~~~


## Examples

```python
import ASFunctions as asf

a = asf.getAccession(3,4959)

b = asf.getArchivalObject(2,369175)

c = asf.getArchivalObjectByRef(repo, 'c0fd586f8cada058182041eb2246abfb')

d = asf.unpublishArchivalObject(2,369175)

e = asf.getDigitalObject(2,3553)

f = asf.getResource(repo,4850)

g = asf.getByDate(2,'2019-08-13',comparator='greater_than',fields=['id','publish'],date_type='ctime', filter='resources')

my_post = asf.postArchivalObject(repo,asid,z)  # z is a JSON object

```
