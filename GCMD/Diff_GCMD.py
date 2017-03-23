import glob, json, rdflib
from rdflib import URIRef, Literal, Namespace
from rdflib.namespace import RDF, SKOS

GCMD = Namespace("http://gcmdservices.gsfc.nasa.gov/kms/concept/")

GCMDfile = ['GCMD8_3.rdf', 'GCMD8_4.rdf','GCMD8_4_1.rdf']
output = open('/home/blee/provdist/GCMD/webGCMD83_84.html', 'w')
#output = codecs.open('/home/blee/GCMD/GCMD8_3to8_4.html', mode='w', encoding='utf-8')

g0 = rdflib.Graph()
g0.parse(GCMDfile[0])
g1 = rdflib.Graph()
g1.parse(GCMDfile[1])

ver = ['8.3', '8.4']
new = g1-g0
old = g0-g1

output.write('''<html>
  <head>
  </head>
  <body vocab="http://www.w3.org/nw/prov#" prefix="vo: http://orion.tw.rpi.edu/~blee/VersionOntology.owl/ v1: http://gcmdservices.gsfc.nasa.gov/kms/concept/ v2: http://gcmdservices.gsfc.nasa.gov/kms/concept/">
    <h2 property="http://purl.org/dc/terms/title"><span about="Version1" property="http://www.w3.org/2000/01/rdf-schema#label" typeof="vo:Version">%s</span> to <span about="Version2" property="http://www.w3.org/2000/01/rdf-schema#label" typeof="vo:Version">%s</span></h2>
'''%(GCMDfile[0], GCMDfile[1]))

output.write('''
      <h3>Concepts added to %s</h3>
      <table about="Version1" rel="vo:absentFrom">
        <tr>
          <th>Link</th>
          <th>Concept</th>
          <th>Change Note</th>
        </tr>
'''%(GCMDfile[1]))

c = 0

for i in new.subjects(RDF.type, SKOS.Concept):
	changeNote = "<br>\n              ".join(g1.objects(i, SKOS.changeNote))
	output.write((u'''        <tr about="AddChange%i" typeof="vo:Change">
            <td property="vo:resultsIn" resource="%s?version=%s" typeof="vo:Attribute">
              <a href="%s?version=%s">Link</a>
            </td>
            <td about="%s?version=%s" property="http://www.w3.org/2004/02/skos/core#prefLabel">%s</td>
            <td property="http://www.w3.org/2004/02/skos/core#changeNote">%s</td>
            <span about="Version2" property="vo:hasAttribute" resource="%s?version=%s"/>
          </tr>
'''%(c, str(i), ver[1], str(i), ver[1], str(i), ver[1], g1.value(i, SKOS.prefLabel), changeNote, str(i), ver[1])).encode('utf8'))
	c += 1

output.write('''      </table>

''')

output.close()
