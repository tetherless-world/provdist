from bs4 import BeautifulSoup
import glob, rdflib, json, re

def extracting(f):
	f = 'ChangelogGCMD70_80.html'
	d = 'Graph'+re.search('ChangelogGCMD(.*).html', f).group(1)+'.ttl'

	fp = open(f)
	soup = BeautifulSoup(fp, 'html5lib')
	fp.close()

	js = soup.find_all('script')
	items = [item for sublist in js for item in json.loads(sublist.text)]

	g = rdflib.Graph()
	g.parse(data = json.dumps(items), format='json-ld')

	g.serialize(destination=d, format='turtle')

l = glob.glob('Changelog*.html')
for i in l:
	print "Extracting: "+i
	extracting(i)
