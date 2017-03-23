import glob, rdflib
from rdflib import Literal, URIRef, Namespace
from rdflib.namespace import RDF, SKOS

GCMD = Namespace("http://gcmdservices.gsfc.nasa.gov/kms/concept/")

#GCMDfiles = sorted(glob.glob("./*.rdf"))
GCMDfiles = ['GCMD8_4_1.rdf']

for f in GCMDfiles:
	load_list = [GCMD['1eb0ea0a-312c-4d74-8d42-6f1ad758f999']]
	UUID = []
	g = rdflib.Graph().parse(f)
	for i in range(3):
		row = []
		for ident in load_list[:]:
			j = load_list.pop(0)
			print j
			row.append(j)
			for s in g.objects(ident, SKOS.narrower):
				load_list.append(s)
		UUID.append(row)
	print ''
	for row in UUID:
		row_label = [g.value(i, SKOS.prefLabel) for i in row] 
		print ', '.join(row_label)
	#print "%s has %s statements."%(f,len(g))
	#ident = g.value(predicate = SKOS.prefLabel, object = Literal("Science Keywords", lang='en'))
	#print "Id of Science Keywords is %s."%ident
