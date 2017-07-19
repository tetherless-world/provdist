from bs4 import BeautifulSoup
import glob, rdflib, json, re

def extracting(f, d):
	#f = 'ChangelogGCMD70_80.html'
	#d = 'Graph'+re.search('ChangelogGCMD(.*).html', f).group(1)+'.ttl'

	fp = open(f)
	soup = BeautifulSoup(fp, 'html5lib')
	fp.close()

	js = soup.find_all('script')
	items = [item for sublist in js for item in json.loads(sublist.text)]

	g = rdflib.Graph()
	g.parse(data = json.dumps(items), format='json-ld')

	g.serialize(destination=d, format='turtle')

if __name__ == "__main__":
	l = glob.glob('Changelog*.html')
	for i in l:
		d = 'Graph'+re.search('ChangelogGCMD(.*).html', i).group(1)+'.ttl'
		print "Extracting: "+i
		print "\tto", d
		extracting(i, d)
