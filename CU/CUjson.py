from os.path import join, dirname, abspath, isfile
from os import sep as separator
import xlrd
import glob
import json
import re

#Given the version 2 column, return the appropriate version 1 column number
def indexConvert(index1):
	#Maps Version 2 columns to Version 1 indexes
	indices = {
		0:1,    1:2,  2:3,    3:4,   6:0,
		7:6,    8:30,  9:7,   10:8,  12:9,
		13:10, 14:11, 15:12, 16:13, 17:14,
		18:15, 19:16, 20:17, 21:18, 22:19,
		23:20, 24:21, 25:22, 26:23, 27:24,
		28:25, 29:26, 43:27, 44:28, 45:29,
		46:31, 47:33, 48:34, 49:35, 50:36}
	return indices.get(index1, -1)

#Unicode messes up when printed to a file. This formats it properly
def formatText(text):
	if isinstance(text, unicode):
		formatted_text = text.encode('utf8', 'replace')
		return formatted_text
	else:
		return text

#File definitions
filename1 = 'ParageneticModeTable_Cu_6.8.2016.xlsx'
filename2 = 'ParageneticModeTable_Cu_8.21.2016.xlsx'
v1_file = join(separator, 'data', 'CUdata', filename1)
#v2_file = join(separator, 'data', 'CUdata', 'Cu_dataset_by_chemistry_20160825.xlsx')
v2_file = join(separator, 'data', 'CUdata', filename2)

#Start using the changelog
changelog = open('DTDI/CUjsonlog.html', 'w')
changelog.write('''<html>
  <head>
    <meta charset="utf-8">
  </head>
  <body vocab="http://www.w3.org/nw/prov#" prefix="vo: http://orion.tw.rpi.edu/~blee/VersioningOntology.owl# v1: http://CUdb.com/v1/ v2: http://CUdb.com/v2/">
    <h2 property="http://purl.org/dc/terms/title">
      <span about="Version1" property="http://www.w3.org/2000/01/rdf-schema#label" typeof="vo:Version">%s</span> to 
      <span about="Version2" property="http://www.w3.org/2000/01/rdf-schema#label" typeof="vo:Version">%s</span>
      <script type="application/ld+json">
'''%(filename1, filename2))

context = "https://orion.tw.rpi.edu/~blee/provdist/GCMD/VO.jsonld"
host = "http://orion.tw.rpi.edu/~blee/provdist/CU/DTDI/CUjsonlog.html#"
json1 = {
"@context":context,
"@type":"vo:Version",
"@id":"Version1",
"label":filename1 
}

json2 = {
"@context":context,
"@type":"vo:Version",
"@id":"Version2",
"label":filename2
}
json.dump([json1,json2], changelog, indent=4, sort_keys=True)

changelog.write("\n      </script>\n    </h2>\n")

workbook = xlrd.open_workbook(v1_file)
sheet_v1 = workbook.sheet_by_name('Database')
#Maps the Excel key to it's appropriate row number
v1_indicators = {}
for a, b in list(enumerate(sheet_v1.col(2)[1:])):
	if b.value not in v1_indicators:
		v1_indicators[b.value]=[a+1]
	else:
		v1_indicators[b.value].append(a)
print [(i, len(v1_indicators[i])) for i in v1_indicators.keys() if len(v1_indicators[i]) > 1]
v1_row = sheet_v1.row(3)

workbook = xlrd.open_workbook(v2_file)
#sheet_v2 = workbook.sheet_by_name('all groups sorted')
sheet_v2 = workbook.sheet_by_name('ParageneticModeTable_Cu_8.21.20')
v2_indicators = {b.value:a for a, b in list(enumerate(sheet_v2.col(1)[1:]))}
v2_row = sheet_v2.row(v2_indicators[v1_row[2].value])


########################################
####                                ####
####            ADDED               ####
####                                ####
########################################

changelog.write('''
      <h3>Columns added to %s</h3>
      <table about="Version1" rel="vo:absentFrom">
        <tr>
          <th>Column #</th>
          <th>Header</th>
        </tr>
'''%(filename2))

print "Added"
for i in range(0,sheet_v2.ncols):
	v1_index = indexConvert(i)
	v2_value = formatText(sheet_v2.cell(0,i).value)
	if v1_index == -1:
		changelog.write('''        <tr id="AddChange%i" about="v2:Attribute%i">
          <td>%i</td>
          <td>%s</td>
          <script type="application/ld+json">
'''%(i, i, i, v2_value)) 
		
		json1 = {
"@context":context,
"@type":"vo:AddChange" ,
"@id": "".join([host, "AddChange", str(i)]) ,
"resultsIn" :   "".join([ "http://CUdb.com/v2/Attribute", str(i)]),
"@reverse"  :   { "absentFrom": "Version1" }
}
		json2 = {
"@context":context,
"@type":"vo:Attribute" ,
"@id":"".join(["http://CUdb.com/v2/Attribute", str(i)]) ,
"label":v2_value ,
"@reverse" :    { "hasAttribute" : "Version2" }
}
		json.dump([json1, json2], changelog, indent=4, sort_keys=True)
		changelog.write('''
          </script>
        </tr>
''')
changelog.write('''      </table>
''')

changelog.write('''
      <h3>Rows added to %s</h3>
      <table about="Version1" rel="vo:absentFrom">
        <tr>
          <th>Row # V2</th>
          <th>Header</th>
        </tr>
'''%(filename2))

for i in v2_indicators.keys():
	if i not in v1_indicators.keys():
		print v2_indicators[i], i
		out = u'''        <tr id="AddChange%s" about="v2:Attribute%s">
          <td>%i</td>
          <td>%s</td>
          <script type="application/ld+json">
'''%(i, i, v2_indicators[i], i)
		changelog.write(out.encode('utf8'))
		json1 = {
"@context":context,
"@type":"vo:AddChange" ,
"@id": "".join([host, "AddChange", i]) ,
"resultsIn" :   "".join([ "http://CUdb.com/v2/Attribute", i]),
"@reverse"  :   { "absentFrom": "Version1" }
}
		json2 = {
"@context":context,
"@type":"vo:Attribute" ,
"@id":"".join(["http://CUdb.com/v2/Attribute", i]) ,
"label":i ,
"@reverse" :    { "hasAttribute" : "Version2" }
}
		json.dump([json1, json2], changelog, indent=4, sort_keys=True)
		changelog.write('''
          </script>
        </tr>
''')
changelog.write('''      </table>
''')

		

########################################
####                                ####
####            REMOVE              ####
####                                ####
########################################

changelog.write('''
      <h3>Columns added to %s</h3>
      <table about="Version2">
        <tr>
          <th>Column #</th>
          <th>Header</th>
        </tr>
'''%(filename1))

print "Removed"
for i in [5, 32]:
	v1_value = formatText(sheet_v1.cell(0,i).value)
	changelog.write('''        <tr id="InvalidateColumn%i" about="v1:Column%i">
          <td>%i</td>
          <td>%s</td>
          <script type="application/ld+json">
'''%(i, i, i, v1_value))
	json1 = {
"@context":context,
"@type":"vo:Attribute" ,
"@id":"".join(["http://CUdb.com/v1/Column", str(i)]) ,
"label":v1_value ,
"undergoes":"".join([host, "InvalidateColumn", str(i)]) ,
"@reverse" :    { "hasAttribute" : "Version1" }
}
	json2 = {
"@context":context,
"@type":"vo:InvalidateChange" ,
"@id": "".join([host, "InvalidateColumn", str(i)]) ,
"invalidatedBy" :   "Version2",
}
	json.dump([json1, json2], changelog, indent=4, sort_keys=True)
	changelog.write('''
          </script>
        </tr>
''')
changelog.write('''      </table>

''')

changelog.write('''
      <h3>Rows added to %s</h3>
      <table about="Version2">
        <tr>
          <th>Row # V1</th>
          <th>Header</th>
        </tr>
'''%(filename1))

print "Removed"
for i in v1_indicators.keys():
	if i not in v2_indicators.keys():
		print v1_indicators[i], i
		for j in v1_indicators[i]:
			out = '''        <tr id="InvalidateChange%s%i" about="v1:Attribute%s%i">
          <td>%i</td>
          <td>%s</td>
          <script type="application/ld+json">
'''%(i, j, i, j, j, i)
			changelog.write(out.encode('utf8'))
			json1 = {
"@context":context,
"@type":"vo:Attribute" ,
"@id":"".join(["http://CUdb.com/v1/Attribute", i, str(j)]) ,
"label":i ,
"undergoes":"".join([host, "InvalidateChange", i, str(j)]) ,
"@reverse" :    { "hasAttribute" : "Version1" }
}
			json2 = {
"@context":context,
"@type":"vo:InvalidateChange" ,
"@id": "".join([host, "InvalidateChange", i, str(j)]) ,
"invalidatedBy" :   "Version2",
}
			json.dump([json1, json2], changelog, indent=4, sort_keys=True)
			changelog.write('''
          </script>
        </tr>
''')
changelog.write('''      </table>

''')

########################################
####                                ####
####           MODIFY               ####
####                                ####
########################################

changelog.write('''
      <h3>Change Log</h3>
''')

for j in range(1,sheet_v2.nrows):
	v2_row = sheet_v2.row(j)
	v2_key = v2_row[1].value
	if isinstance(v2_key, unicode):
		v2_key = v2_key.encode('utf8', 'replace')
	v1_index = v1_indicators.get(v2_row[1].value, -1)
	if v1_index == -1:
		print ""
		print v2_key, "not found"
		continue
	else:
		v1_row = sheet_v1.row(v1_index[0])
		if len(v1_index) > 1:
			print "Oh no, it has more than one row"
	changelog.write('''
      <div about="v1:%s"">
        <span style="font-weight:bold" property="http://www.w3.org/2000/01/rdf-schema#label">%s</span>
        <table>
          <tr>
            <th>Column v1</th>
            <th>Column v2</th>
            <th>Version 1</th>
            <th>Version 2</th>
          </tr>\n'''%(v2_key, v2_key))
	for i in range(len(v2_row)):
		formatted_v2 = v2_row[i].value
		if isinstance(formatted_v2, unicode):
	                formatted_v2 = formatted_v2.encode('utf8', 'replace')
	
		index = indexConvert(i)
		if index >= 0:
			formatted_v1 = v1_row[index].value
			if isinstance(formatted_v1, unicode):
				formatted_v1 = formatted_v1.encode('utf8', 'replace')
			if formatted_v1 != formatted_v2:
				changelog.write('''        <tr  id="ModifyChange{}{}">
          <td align="right">{:2}</td>
	  <td >({:2})</td>
	  <td>{:>10}</td>
	  <td>{:>10}</td>
          <script type="application/ld+json">
'''.format(v2_key, i, index, i, formatted_v1, formatted_v2))
				json1 = {
"@context":context,
"@type":"vo:Attribute" ,
"@id":"".join(["http://CUdb.com/v1/Attribute", v2_key, str(index)]) ,
"label":sheet_v1.cell(0,index).value ,
"undergoes":"".join([host, "ModifyChange", v2_key, str(i)]) ,
"@reverse" :    { "hasAttribute" : "Version1" }
}
				json2 = {
"@context":context,
"@type":"vo:ModifyChange",
"@id":"".join([host, "ModifyChange", v2_key, str(i)]) ,
"resultsIn":"".join(["http://CUdb.com/v2/Attribute", v2_key, str(i)])
}
				json3 = {
"@context":context,
"@type":"vo:Attribute" ,
"@id":"".join(["http://CUdb.com/v2/Attribute", v2_key, str(i)]) ,
"label":sheet_v2.cell(0,i).value ,
"@reverse" :    { "hasAttribute" : "Version2" }
}
				json.dump([json1, json2, json3], changelog, indent=4, sort_keys=True)
				changelog.write('''
          </script>
        </tr>\n''')


#		else:
#			changelog.write('''      <tr property="vo:undergoes" typeof="vo:Change">
#        <td></td>
#        <td>(<span property="vo:PostIndicator">{:2}</span>)</td>
#        <td></td>
#        <td>{:>10}</td>
#      </tr>\n'''.format(i, formatted_v2))
	changelog.write("    </table></div><br>\n")

changelog.write("\t</body>\n</html>")
changelog.close()
#print v1_row
#print v2_row
