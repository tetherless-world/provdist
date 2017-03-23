import glob, json, rdflib
from rdflib import URIRef, Literal, Namespace
from rdflib.namespace import RDF, SKOS

GCMD = Namespace("http://gcmdservices.gsfc.nasa.gov/kms/concept/")

GCMDfile = ['GCMD8_3.rdf', 'GCMD8_4.rdf','GCMD8_4_1.rdf']
output = open('/home/blee/d3-process-map/data/gcmd/objects.json', 'w')

g0 = rdflib.Graph()
g0.parse(GCMDfile[0])
g1 = rdflib.Graph()
g1.parse(GCMDfile[1])
g2 = rdflib.Graph()
g2.parse(GCMDfile[2])

objects = []
new_objects = list((g1-g0).subjects(RDF.type, SKOS.Concept))
old_objects = list((g1-g2).subjects(RDF.type, SKOS.Concept))
print len(old_objects)

for i in g1.subjects(RDF.type, SKOS.Concept):
	uuid = str(i).split('/')[-1]
	name = str(g1.value(i, SKOS.prefLabel))
	depends = [x.split('/')[-1] for x in list(g1.objects(i, SKOS.broader))]
	
	obj = {}
	if i in new_objects and i in old_objects:
		obj['type'] = "New & Removed"
	elif i in new_objects:
		obj['type'] = "New"
	elif i in old_objects:
		obj['type'] = "Old"
	elif g1.value(i, SKOS.broader) != g0.value(i, SKOS.broader):
		obj['type'] = "Moved"
	else:
		obj['type'] = "Concept"
	obj['uuid'] = uuid
	obj['name'] = name
	obj['depends'] = depends
	objects.append(obj)

output.write(json.dumps(objects, indent=4, separators=(',', ': ')))
