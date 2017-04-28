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

#Get the date for the change notes in the new changes made in version 2
#This will help determine if some concepts were changed without being moved
#Their change notes should have a date on the same day as the new additions.
#This is probably a bad way of determining this.
date = g1.value(new.value(predicate=RDF.type, object=SKOS.Concept), SKOS.changeNote).split()[0]
context = "https://orion.tw.rpi.edu/~blee/provdist/GCMD/VO.jsonld"

##################
###   Header   ###
##################

output.write('''<html>
  <head>
  </head>
  <body vocab="http://www.w3.org/nw/prov#" prefix="gcmd: http://gcmdservices.gsfc.nasa.gov/kms/concept/">
    <h2 property="http://purl.org/dc/terms/title">
      <span about="gcmd:concept_scheme/sciencekeywords/?format=xml&version=%s" property="http://www.w3.org/2000/01/rdf-schema#label">%s</span> to 
      <span about="gcmd:concept_scheme/sciencekeywords/?format=xml&version=%s" property="http://www.w3.org/2000/01/rdf-schema#label">%s</span>
'''%(ver[0], GCMDfile[0], ver[1], GCMDfile[1]))

output.write('''      <script type="application/ld+json">
[
	{
		"@context" : "%s" ,
		"type"	:	"vo:Version" ,
		"id"	:	"gcmd:concept_scheme/sciencekeywords/?format=xml&version=%s" ,
                "label" :       "%s"
        },
        {
                "@context" : "%s",
                "type"  :       "vo:Version" ,
                "id"    :       "gcmd:concept_scheme/sciencekeywords/?format=xml&version=%s" ,
                "label" :       "%s"
        }
]
      </script>
    </h2>
'''%(context, ver[0], GCMDfile[0], context, ver[1], GCMDfile[1]))

#################
###   ADDED   ###
#################

output.write('''
      <h3>Concepts added to %s</h3>
      <table about="gcmd:concept_scheme/sciencekeywords/?format=xml&version=%s">
        <tr>
          <th>Link</th>
          <th>Concept</th>
          <th>Change Note</th>
        </tr>
'''%(GCMDfile[1], ver[1]))

c = 0

for i in new.subjects(RDF.type, SKOS.Concept):
	changeNote = "<br>\n              ".join(g1.objects(i, SKOS.changeNote))
	output.write((u'''        <tr id="AddChange%i" about="%s?version=%s">
            <td>
              <a href="%s?version=%s">Link</a>
            </td>
            <td property="http://www.w3.org/2004/02/skos/core#prefLabel">%s</td>
            <td property="http://www.w3.org/2004/02/skos/core#changeNote">%s</td>
'''%(c, str(i), ver[1], str(i), ver[1], g1.value(i, SKOS.prefLabel), changeNote)).encode('utf8'))
	output.write((u'''
            <script type="application/ld+json">
[
	{
		"@context" : "%s" ,
		"type"	:	"vo:AddChange" ,
		"id"	:	"this:AddChange%i" ,
		"resultsIn" :	"gcmd:%s?version=%s" ,
		"@reverse"  :	{ "absentFrom": "gcmd:concept_scheme/sciencekeywords/?format=xml&version=%s" }
	},
	{
		"@context" : "%s" ,
		"type"	:	"vo:Attribute" ,
		"id"	:	"gcmd:%s?version=%s" ,
		"label" :	"%s" ,
		"@reverse" :	{ "hasAttribute" : "gcmd:concept_scheme/sciencekeywords/?format=xml&version=%s" }
	}
]
            </script>
          </tr>
'''%(context, c, i.split('/')[-1], ver[1], ver[0], context, i.split('/')[-1], ver[1], g1.value(i, SKOS.prefLabel), ver[1])).encode('utf8'))
	c += 1

output.write('''      </table>

''')

print date

#################
### REMOVED   ###
#################

output.write('''
      <h3>Concepts removed from %s</h3>
      <table about="gcmd:concept_scheme/sciencekeywords/?format=xml&version=%s">
        <tr>
          <th>Link</th>
          <th>Concept</th>
        </tr>
'''%(GCMDfile[0], ver[0]))

c = 0

for i in old.subjects(RDF.type, SKOS.Concept):#Reverse relations due to ordering and structure
        output.write((u'''        <tr id="InvlidateChange%i" about="%s?version=%s">
          <td>
            <a href="%s?version=%s">Link</a>
          </td>
          <td property="http://www.w3.org/2004/02/skos/core#prefLabel">%s</td>
'''%(c, str(i), ver[0], str(i), ver[0], g0.value(i, SKOS.prefLabel), )).encode('utf8'))
	output.write((u'''          <script type="application/ld+json">
[
	{
		"@context" : "%s" ,
		"type"	:	"vo:Attribute" ,
		"id"	:	"gcmd:%s?version=%s" ,
		"label"	:	"%s" ,
		"undergoes" :	"this:InvalidateChange%i" ,
		"@reverse" :	{ "hasAttribute" : "gcmd:concept_scheme/sciencekeywords/?format=xml&version=%s" }
	},
	{
		"@context" : "%s" ,
		"type"	:	"vo:InvalidateChange" ,
		"id"	:	"this:InvalidateChange%i" ,
		"invalidatedBy"	:	"gcmd:concept_scheme/sciencekeywords/?format=xml&version=%s"
	}
]
          </script>
        </tr>
'''%(context, i.split('/')[-1], ver[0], g1.value(i, SKOS.prefLabel), c, ver[0], context, c, ver[0])).encode('utf8'))
	c += 1
output.write('''      </table>

''')

##################
###   Modify   ###
##################

output.write('''
      <h3>Moved Concepts</h3>
      <table>
        <tr>
          <th>Link v1</th>
          <th>Link v2</th>
          <th>Label</th>
          <th>Old Parent</th>
          <th>New Parent</th>
        </tr>\n
''')

c = 0

for i in g1.subjects(RDF.type, SKOS.Concept):
	if (i, None, None) in g0:
		b0 = g0.value(i, SKOS.broader)
		b1 = g1.value(i, SKOS.broader)
		if b0 != b1:
			output.write((u'''        <tr id="MoveChange%i" about="%s?version=%s">
          <td><a href=%s?version=%s>Link</a></td>
          <td><a href=%s?version=%s>Link</a></td>
          <td property="http://www.w3.org/2004/02/skos/core#prefLabel">%s</td>
          <td about="%s?version=%s" property="http://www.w3.org/2004/02/skos/core#prefLabel">%s</td>
          <td about="%s?version=%s" property="http://www.w3.org/2004/02/skos/core#prefLabel">%s</td>
'''%(c, str(i), ver[1],
     str(i), ver[0],
     str(i), ver[1],
     g1.value(i, SKOS.prefLabel),
     b0, ver[0], g0.value(b0, SKOS.prefLabel),
     b1, ver[1], g1.value(b1, SKOS.prefLabel))  ).encode('utf8'))

			output.write((u'''          <script  type="application/ld+json">
[
	{
		"@context" : "%s" ,
		"type"	:	"vo:Attribute" ,
		"id"	:	"gcmd:%s?version=%s" ,
		"label"	:	"%s" ,
		"undergoes" :	"this:MoveChange%i" ,
		"@reverse" :	{ "hasAttribute" : "gcmd:concept_scheme/sciencekeywords/?format=xml&version=%s" }
	},
	{
		"@context" : "%s" ,
		"type"	:	"vo:ModifyChange" ,
		"id"	:	"this:MoveChange%i" ,
		"resultsIn"	:	"gcmd:%s?version=%s"
	},
	{
		"@context" : "%s" ,
		"type"	:	"vo:Attribute" ,
		"id"	:	"gcmd:%s?version=%s" ,
		"label"	:	"%s" ,
		"@reverse" :	{ "hasAttribute" : "gcmd:concept_scheme/sciencekeywords/?format=xml&version=%s" }
	}
]
          </script>
        </tr>
'''%(context, i.split('/')[-1], ver[0], g0.value(i, SKOS.prefLabel), c, ver[0], 
     context, c, i.split('/')[-1], ver[1], 
     context, i.split('/')[-1], ver[1], g1.value(i, SKOS.prefLabel), ver[1])  ).encode('utf8'))
			c += 1

output.write('''      </table>

''')

##################################
###   NON-STRUCTURAL CHANGES   ###
##################################

output.write('''
      <h3>Non-Structural Changes</h3>
      <table>
        <tr>
          <th>Link v1</th>
          <th>Link v2</th>
          <th>Label</th>
          <th>Change Notes</th>
        </tr>\n
''')

c = 0

for i in g1.subjects(RDF.type, SKOS.Concept):
	if (i, None, None) in g0:
		b0 = g0.value(i, SKOS.broader)
		b1 = g1.value(i, SKOS.broader)
		if b0 == b1:
			new_note = False
			notes = []
			for note in g1.objects(i, SKOS.changeNote):
				note_date = note.split()[0]
				print note_date
				if note_date == date:
					new_note = True
					notes.append(note)
			if new_note:
				output.write((u'''        <tr id="ModifyChange%i" about="%s?version=%s">
          <td><a href=%s?version=%s>Link</a></td>
          <td><a href=%s?version=%s>Link</a></td>
          <td property="http://www.w3.org/2004/02/skos/core#prefLabel">%s</td>
          <td property="http://www.w3.org/2004/02/skos/core#changeNote">%s</td>
'''%(c, str(i), ver[1],
     str(i), ver[0],
     str(i), ver[1],
     g1.value(i, SKOS.prefLabel),
     "<br>\n              ".join(notes)
)).encode('utf8'))
				output.write((u'''
        </tr>
'''%()).encode('utf8'))
				c += 1

output.write('''      </table>

''')
output.write("\t</body>\n</html>")
output.close()
