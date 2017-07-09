import xlrd, json

def load_data(fname):
	wb = xlrd.open_workbook(fname)
	sheet = wb.sheet_by_index(0)
	indicator = sheet.col(0)
	match = sheet.col(1)
	count = sheet.col(2)
	
	rel = {"":{}}
	current_indicator = ""
	
	for i in range(1, len(indicator)):
		if indicator[i].ctype == 0:
			rel[current_indicator][match[i].value] = count[i].value
		elif indicator[i].ctype == 1:
			current_indicator = indicator[i].value
			rel[current_indicator] = {match[i].value:count[i].value}
	return rel

f1 = "silva_gast.xls"
f2 = "silva_spingo.xls"

def gen_log(f1, f2):
	rel1 = load_data(f1)
	rel2 = load_data(f2)
	fchange = "Change.%s.%s.html"%(f1.split('.')[0], f2.split('.')[0])
	changelog = open(fchange, 'w')

	changelog.write('''<html>
  <head>
  </head>
  <body prefix="vo: https://orion.tw.rpi.edu/~blee/VersionOntology.owl#">
    <h2 property="http://purl.org/dc/terms/title">
      <span about="Version1" property="http://www.w3.org/2000/01/rdf-schema#label" typeof="vo:Version">%s</span> to
      <span about="Version2" property="http://www.w3.org/2000/01/rdf-schema#label" typeof="vo:Version">%s</span>
      <script type="application/ld+json">
'''%(f1, f2))
	
	context = "https://orion.tw.rpi.edu/~blee/provdist/GCMD/VO.jsonld"
	host = "http://orion.tw.rpi.edu/~blee/provdist/MBVL/%s#"%(fchange)
	json1 = {
		"@context":context,
		"@type":"vo:Version",
		"@id":"Version1",
		"label":f1
	}

	json2 = {
		"@context":context,
		"@type":"vo:Version",
		"@id":"Version2",
		"label":f2
	}
	json.dump([json1,json2], changelog, indent=4, sort_keys=True)
	changelog.write('''
      </script>
    <h2>
''')

	for i in rel1.keys():
		changelog.write('''
    <div about="%s%s">
      <span style="font-weight:bold" property="http://www.w3.org/2000/01/rdf-schema#label">%s</span>
      <table>
        <tr>
          <th>type</th>
          <th>classification</th>
          <th>Count 1</th>
          <th>Count 2</th>
        </tr>\n
'''%(host, i, i))
		print i
		for j in set(rel1[i].keys())-set(rel2[i].keys()):
			print " removed", j
			changelog.write('''
        <tr>
          <td>---</td>
          <td>%s</td>
          <td>%i</td>
        </tr>
'''%(j, rel1[i][j]))
		for j in set(rel1[i].keys())&set(rel2[i].keys()):
			if rel1[i][j] != rel2[i][j]:
				print " modify", j, rel1[i][j], rel2[i][j]
				changelog.write('''
        <tr>
          <td>>>></td>
          <td>%s</td>
          <td>%i</td>
          <td>%i</td>
        </tr>
'''%(j, rel1[i][j], rel2[i][j]))
		for j in set(rel2[i].keys())-set(rel1[i].keys()):
			print " added", j
			changelog.write('''
        <tr>
          <td>+++</td>
          <td>%s</td>
          <td></td>
          <td>%i</td>
        </tr>
'''%(j, rel2[i][j]))
		changelog.write('''
      </table>
    </div>
''')
	changelog.write('''
  </body>
</html>
''')
	changelog.close()

gen_log(f1, f2)
