import glob, json, rdflib, re
from rdflib import URIRef, Literal, Namespace
from rdflib.namespace import RDF, SKOS

def makeTree(GCMDf1, GCMDf2, GCMDf3):
	GCMD = Namespace("http://gcmdservices.gsfc.nasa.gov/kms/concept/")
	
	#GCMDfile = ['GCMD8_3.rdf', 'GCMD8_4.rdf','GCMD8_4_1.rdf']
	print GCMDf1, GCMDf2, GCMDf3
	number = re.search('GCMD(.*).rdf', GCMDf2).group(1).replace("_","")
	output = open(''.join(['/home/blee/d3-process-map/data/gcmd/objects', number, '.json']), 'w')
	
	g0 = rdflib.Graph()
	g0.parse(GCMDf1)
	g1 = rdflib.Graph()
	g1.parse(GCMDf2)
	g2 = rdflib.Graph()
	g2.parse(GCMDf3)
	
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
	output.close()

if __name__ == "__main__":
        GCMDfiles = sorted(glob.glob("*.rdf"))
        for i in range(len(GCMDfiles)-2):
                print "Starting",GCMDfiles[i-1],"and",GCMDfiles[i] #It's done this way because GCMDJun1220012 sorts to the last item
                makeTree(GCMDfiles[i-1],GCMDfiles[i], GCMDfiles[i+1])

