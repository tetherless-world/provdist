from os.path import join, dirname, abspath, isfile
from os import sep as separator
import xlrd, sys, json
import glob
import re


def index_convert(index1):
	return index1

def test_alignment():
	for i in range(0, 54):
		print 'version2: {:5} version1: {:5}'.format(i, index_convert(i))

def compare_print(mode, key, val1, val2, v1_file, v1_index = 0, v2_index = 0, changelog = None):
	if changelog:
		if mode == 'r':
			out = u'''        <tr  about="Change{}{}" typeof="vo:ModifyChange">
          <td align="right" rev="vo:Undergoes" resource="v2:Attribute{}{}v2" typeof="vo:Attribute">{:2}({})</td>
          <td property="vo:resultsIn" resource="v3:Attribute{}{}v3" typeof="vo:Attribute">{:2}</td>
          <td>{:>10}</td>
          <td>{:>10}</td>
          <span about="Version2" property="vo:hasAttribute" resource="v2:Attribute{}{}v2"></span>
          <span about="Version3" property="vo:hasAttribute" resource="v3:Attribute{}{}v3"></span>
        </tr>\n'''.format(key, v2_index, key, v1_index, v1_index, v1_file, key, v2_index, v2_index, val1, val2, key, v1_index, key, v2_index)
		elif mode == 'j':
			out = u'''        <tr  id="ModifyChange{}{}">
          <td align="right">{:2}</td>
          <td>{:2}</td>
          <td>{:>10}</td>
          <td>{:>10}</td>
          <script type="application/ld+json">\n'''.format(key, v2_index, v1_index, v2_index, val1, val2)
		elif mode == 't':
			out = u"{:2}\t{:2}\t{:>10}\t{:>10}\n".format(v1_index, v2_index, val1, val2)
		elif mode == 'u':
			out = u"""<http://example.com/NG/Version2> vo:hasAttribute <http://example.com/NG/Version2/%s> ;
        vo:hasAttribute <http://example.com/NG/Version2/Column%i> .
<http://example.com/NG/Version2/%s> a vo:Attribute ;
        vo:undergoes <http://example.com/Changelog#ModifyChange%s%i> .
<http://example.com/NG/Version2/Column%i> a vo:Attribute ;
        vo:undergoes <http://example.com/Changelog#ModifyChange%s%i> .
<http://example.com/Changelog#ModifyChange%s%i> a vo:ModifyChange ;
        vo:resultsIn <http://example.com/NG/Version3/%s> ;
        vo:resultsIn <http://example.com/NG/Version3/Column%i> .
<http://example.com/NG/Version3> vo:hasAttribute <http://example.com/NG/Version3/%s> ;
        vo:hasAttribute <http://example.com/NG/Version3/Column%i> .

"""%(key, v1_index, key, key, v2_index, v1_index, key, v2_index, key, v2_index, key, v2_index, key, v2_index)
		changelog.write(out.encode('utf8'))
		if mode == 'j':
			json1 = {
"@context":context,
"@type":"vo:Attribute" ,
"@id":"".join(["http://ngdb.com/v2/Attribute", key, str(v1_index)]) ,
"label":key ,
"undergoes":"".join([host, "ModifyChange", key, str(v2_index)]) ,
"@reverse" :    { "hasAttribute" : "Version2" }
}
			json2 = {
"@context":context,
"@type":"vo:ModifyChange",
"@id":"".join([host, "ModifyChange", key, str(v2_index)]) ,
"resultsIn":"".join(["http://ngdb.com/v3/Attribute", key, str(v2_index)])
}
			json3 = {
"@context":context,
"@type":"vo:Attribute" ,
"@id":"".join(["http://ngdb.com/v3/Attribute", key, str(v2_index)]) ,
"label":key ,
"@reverse" :    { "hasAttribute" : "Version3" }
}
			json.dump([json1, json2, json3], changelog, indent=4, sort_keys=True)
			changelog.write('''
          </script>
        </tr>
''')
	else:
		print '{:5}  version2: {:10} version3: {:10}'.format(key, val1, val2)

labels = {}

context = "https://orion.tw.rpi.edu/~blee/provdist/GCMD/VO.jsonld"
host = "http://orion.tw.rpi.edu/~blee/provdist/NobleGas/changelog_json.html#"
#test_alignment()


#print v2_row[0].value
#print indicator_map[v2_row[0].value]

#v1_workbook = xlrd.open_workbook(v1_file)
#v1_sheet = v1_workbook.sheet_by_index(0)
#v1_row = v1_sheet.row(4)

def write_modify(r1, r2, workbook, f_out, mode):
	if mode == 'r':
		out = u'''  <div about="Version2" rel="vo:hasAttribute">
    <div resource="v3:%s" typeof="vo:Attribute">
      <span style="font-weight:bold" property="http://www.w3.org/2000/01/rdf-schema#label">%s</span>
      <table rel="vo:Undergoes">
'''%(r2[0].value, r2[0].value)
	elif mode == 'j':
		out = u'''
    <div about="v3:%s">
      <span style="font-weight:bold" property="http://www.w3.org/2000/01/rdf-schema#label">%s</span>
      <table>
'''%(r2[0].value, r2[0].value)
	elif mode == 't':
		out = u"%s\n"%(r2[0].value)
	elif mode == 'u':
		out = u""

	if mode == 'r' or mode == 'j':
		out = out+'''        <tr>
          <th>Column v2</th>
          <th>Column v3</th>
          <th>Version 2</th>
          <th>Version 3</th>
        </tr>\n'''
	elif mode == 't':
		out = out+"Column v2\tColumn v3\tVersion 2\tVersion 3\n"
	f_out.write(out.encode('utf8'))
		#print '# Searching...'
		#print '# Comparing...'
	for i in range(0,54):
		if r2[i].value != r1[i].value:
			#compare_print(j, v1_row[index_convert(j)].value, v2_row[j].value)
			compare_print(mode, r2[0].value, r1[i].value, r2[i].value, workbook.split('/')[-1], i, i, f_out)
	if mode == 'r' or mode == 'j':
		f_out.write('  </table></div><br>\n')
	elif mode == 't' or mode == 'u':
		f_out.write("\n")

def write_removed(v2, col, row, f_out, mode):
	if mode == 'r' or mode == 'j':
		f_out.write('''
      <h3>Columns invalidated by %s</h3>
      <table about="Version2">
'''%(v2.split('/')[-1]))
	elif mode == 't':
		f_out.write("\nColumns invalidated by %s\n"%(v2.split('/')[-1]))

	print "Removed Column"
	for i in col:
        	v1_value = labels.get(i, "")
		if mode == 'r':
			out = u'''        <tr resource="InvlidateChange%i" rev="vo:invalidatedBy" typeof="vo:InvalidateChange">
		<td resource="Attribute%i" rev="vo:Undergoes" typeof="vo:Attribute">%i</td>
          <td about="Attribute%i" property="http://www.w3.org/2000/01/rdf-schema#label">%s</td>
          <span about="Version1" property="vo:hasAttribute" resource="Attribute%i"/>
        </tr>
'''%(i, i, i, i, v1_value, i)
		elif mode == 'j':
			out = u'''        <tr id="InvlidateChange%i" about="InvlidateChange%i">
          <td>%i</td>
          <td>%s</td>
          <script type="application/ld+json">
'''%(i, i, i, v1_value)
		elif mode == 't':
			out = u"%i\t%s\n"%(i, v1_value)
		elif mode == 'u':
			out = u"""<http://example.com/NG/Version2> vo:hasAttribute <http://example.com/NG/Version2/Column%i> .
<http://example.com/NG/Version2/Column%i> vo:undergoes <http://example.com/Changelog#InvalidateChange%i> .
<http://example.com/Changelog#InvalidateChange%i> a vo:InvalidateChange ;
	vo:invalidatedBy <http://example.com/NG/Version3> .

"""%(i, i, i, i)
		f_out.write(out.encode('utf8'))
		if mode == 'j':
			json1 = {
"@context":context,
"@type":"vo:Attribute" ,
"@id":"".join(["http://ngdb.com/v2/Attribute", str(i)]) ,
"label": v1_value,
"undergoes":"".join([host, "InvalidateChange", str(i)]) ,
"@reverse" :    { "hasAttribute" : "Version2" }
}
			json2 = {
"@context":context,
"@type":"vo:InvalidateChange" ,
"@id": "".join([host, "InvalidateChange", str(i)]) ,
"invalidatedBy"  :   "Version3"
}
			json.dump([json1, json2], f_out, indent=4, sort_keys=True)
			f_out.write('''
          </script>
        </tr>
''')
			

	if mode == 'r' or mode == 'j':
		f_out.write('''      </table>
      <h3>Rows invalidated by %s</h3>
      <table about="Version2">
'''%(v2.split('/')[-1]))
	elif mode == 't':
		f_out.write("\nRows invalidated by %s\n"%(v2.split('/')[-1]))
	elif mode == 'u':
		f_out.write("\n")

	print "Removed Row"
	for i, j in sorted(row):#i is row #, j is row id
		if mode == 'r':
			out = u'''        <tr resource="InvlidateChange%s" rev="vo:invalidatedBy" typeof="vo:InvalidateChange">
          <td resource="Attribute%s" rev="vo:Undergoes" typeof="vo:Attribute">%i</td>
          <td about="Attribute%s" property="http://www.w3.org/2000/01/rdf-schema#label">%s</td>
          <span about="Version2" property="vo:hasAttribute" resource="Attribute%s"/>
        </tr>
'''%(j, j, i, j, j, j)
		elif mode == 'j':
			out = u'''        <tr id="InvlidateChange%s" about="InvlidateChange%s">
          <td>%i</td>
          <td>%s</td>
          <script type="application/ld+json">
'''%(j, j, i,  j)
		elif mode == 't':
			out = u"%i\t%s\n"%(i, j)
		elif mode == 'u':
			out = u"""<http://example.com/NG/Version2> vo:hasAttribute <http://example.com/NG/Version2/%s> .
<http://example.com/NG/Version2/%s> vo:undergoes <http://example.com/Changelog#InvalidateChange%s> .
<http://example.com/Changelog#InvalidateChange%s> a vo:InvalidateChange ;
	vo:invalidatedBy <http://example.com/NG/Version2> .

"""%(j, j, j, j)
		f_out.write(out.encode('utf8'))
		if mode == 'j':
			json1 = {
"@context":context,
"@type":"vo:Attribute" ,
"@id":"".join(["http://ngdb.com/v2/Attribute", j]) ,
"label": j,
"undergoes":"".join([host, "InvalidateChange", j]) ,
"@reverse" :    { "hasAttribute" : "Version2" }
}
			json2 = {
"@context":context,
"@type":"vo:InvalidateChange" ,
"@id": "".join([host, "InvalidateChange", j]) ,
"invalidatedBy"  :   "Version3"
}
			json.dump([json1, json2], f_out, indent=4, sort_keys=True)
			f_out.write('''
          </script>
        </tr>
''')
	if mode == 'r' or mode == 'j':
		f_out.write('''      </table>

''')
	elif mode == 't' or mode == 'u':
		f_out.write("\n")


def write_added(v2, col, row, f_out, mode):
	if mode == 'r' or mode == 'j':
		f_out.write('''
      <h3>Columns added by %s</h3>
      <table about="Version2" rel="vo:absentFrom">
'''%(v2.split('/')[-1]))
	elif mode == 't':
		f_out.write("\nColumns added by %s\n\n"%(v2.split('/')[-1]))
	
	print "Added Column"
	for i in col:
		print i#, v2_value
		if mode == 'r':
			f_out.write('''        <tr about="AddChange%i" typeof="vo:AddChange">
          <td property="vo:resultsIn" resource="Attribute%i" typeof="vo:Attribute">%i</td>
          <td about="Attribute%i" property="http://www.w3.org/2000/01/rdf-schema#label"></td>
          <span about="Version3" property="vo:hasAttribute" resource="Attribute%i"/>
        </tr>
'''%(i, i, i, i, i))
		elif mode == 'j':
			f_out.write('''        <tr id="AddChange%i" about="v2:Attribute%i">
          <td>%i</td>
          <td></td>
          <script type="application/ld+json">
'''%(i, i, i))
			json1 = {
"@context":context,
"@type":"vo:AddChange" ,
"@id": "".join([host, "AddChange", str(i)]) ,
"resultsIn" :   "".join([ "http://ngdb.com/v3/Attribute", str(i)]),
"@reverse"  :   { "absentFrom": "Version2" }
}
			json2 = {
"@context":context,
"@type":"vo:Attribute" ,
"@id":"".join(["http://ngdb.com/v3/Attribute", str(i)]) ,
"label":"" ,
"@reverse" :    { "hasAttribute" : "Version3" }
}
			json.dump([json1, json2], f_out, indent=4, sort_keys=True)
			f_out.write('''
          </script>
        </tr>
''')
		elif mode == 't':
			f_out.write("%i\t\n"%(i))	
		elif mode == 'u':
			f_out.write("""<http://example.com/NG/Version2> vo:absentFrom <http://example.com/Changelog#AddChange%i> .
<http://example.com/Changelog#AddChange%i> a vo:AddChange ;
	vo:resultsIn <http://example.com/NG/Version3/Column%s> .
<http://example.com/NG/Version3> vo:hasAttribute <http://example.com/NG/Version3/Column%s> .

"""%(i, i, i, i))
	if mode == 'r' or mode == 'j':
		f_out.write('''      </table>
	      <h3>Rows added by %s</h3>
	      <table about="Version2" rel="vo:absentFrom">
'''%(v2.split('/')[-1]))
	elif mode == 't':
		f_out.write("\nRows added by %s\n\n"%(v2.split('/')[-1]))
	elif mode == 'u':
		f_out.write("\n")
	
	print "Added Row"
	for i, j in row:#i is the row #, j is the id
	        if mode == 'r':	                #print i, v2_sheet.cell(i,0).value
			out = u'''        <tr about="AddChange%s" typeof="vo:AddChange">
          <td property="vo:resultsIn" resource="Attribute%s" typeof="vo:Attribute">%i</td>
          <td about="Attribute%s" property="http://www.w3.org/2000/01/rdf-schema#label">%s</td>
          <span about="Version3" property="vo:hasAttribute" resource="Attribute%s"/>
        </tr>
'''%(j, j, i, j, j, j)
		elif mode == 'j':
			out = u'''        <tr id="AddChange%s" about="v3:Attribute%s">
          <td>%i</td>
          <td property="http://www.w3.org/2000/01/rdf-schema#label">%s</td>
          <script type="application/ld+json">
'''%(j, j, i, j)
		elif mode == 't':
			out = u"%i\t%s\n"%(i, j)
		elif mode == 'u':
			out = u"""<http://example.com/NG/Version2> vo:absentFrom <http://example.com/Changelog#AddChange%s> .
<http://example.com/Changelog#AddChange%s> a vo:AddChange ;
	vo:resultsIn <http://example.com/NG/Version3/%s> .
<http://example.com/NG/Version3> vo:hasAttribute <http://example.com/NG/Version3/%s> .

"""%(j, j, j, j)
                f_out.write(out.encode('utf8'))
		if mode == 'j':
			json1 = {
"@context":context,
"@type":"vo:AddChange" ,
"@id": "".join([host, "AddChange", j]) ,
"resultsIn" :   "".join([ "http://ngdb.com/v3/Attribute", j]),
"@reverse"  :   { "absentFrom": "Version2" }
}
			json2 = {
"@context":context,
"@type":"vo:Attribute" ,
"@id":"".join(["http://ngdb.com/v3/Attribute", j]) ,
"label": j ,
"@reverse" :    { "hasAttribute" : "Version2" }
}
			json.dump([json1, json2], f_out, indent=4, sort_keys=True)
			f_out.write('''
          </script>
        </tr>
''')

	if mode == 'r' or mode == 'j':
		f_out.write('''      </table>
''')
	elif mode == 't' or mode == 'u':
		f_out.write("\n")
	
def write_header(f_out, mode):
	if mode == 'j' or mode == 'r':
		f_out.write('''<html>
  <head>
  </head>
  <body vocab="http://www.w3.org/nw/prov#" prefix="vo: https://orion.tw.rpi.edu/~blee/VersionOntology.owl# v2: http://ngdb.com/v2/ v3: http://ngdb.com/v3/">
''')
	if mode == 'j':
		f_out.write('''  <script type="application/ld+json">
''')
		json1 = {
"@context":context,
"@type":"vo:Version",
"@id":"Version2",
"label":"DB_final-55-7262_2015_03_08.xlsx"
}
		json2 = {
"@context":context,
"@type":"vo:Version",
"@id":"Version3",
"label":"NG_DB_final_2017_07_01.xlsx"
}
		json.dump([json1,json2], f_out, indent=4, sort_keys=True)
		f_out.write("\n  </script>\n")
	if mode == 'u':
		f_out.write("""@prefix vo: <http://orion.tw.rpi.edu/~blee/VersionOntology.owl#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<http://example.com/NG/Version3> a vo:Version ;
        skos:prefLabel "NG_DB_final_2017_07_01.xlsx" .

<http://example.com/NG/Version2> a vo:Version ;
        skos:prefLabel "DB_final-55-7262_2015_03_08.xlsx" .

""")

def write_footer(f_out, mode):
	if mode == 'r':
		f_out.write('</body>\n</html>')

def get_indicator_map(excel_files):
	indicator_map = {}
	for excel_file in excel_files:
		print 'Importing: ' + excel_file
		file_workbook = xlrd.open_workbook(excel_file)
		file_sheet = file_workbook.sheet_by_index(0)
		indicators = file_sheet.col(0)
		for i in range(4, file_sheet.nrows):
			indicator_map[indicators[i].value] = excel_file
	return indicator_map

def compare(v1s, v2, fn_out, mode):
	v1_workbook = xlrd.open_workbook(v1s)
	v1_sheet = v1_workbook.sheet_by_index(0)
	i_keys = {j.value:i for i,j in enumerate(v1_sheet.col(0)[3:],3)}

	v2_workbook = xlrd.open_workbook(v2)
	v2_sheet = v2_workbook.sheet_by_index(0)
	v2_keys = {j.value:i for i,j in enumerate(v2_sheet.col(0)[3:],3)}

	f_out = open(fn_out, 'w')

	new_col = [i for i in range(0, v2_sheet.ncols) if index_convert(i) == -1]
	new_row = [(v2_keys[i], i) for i in v2_keys.keys() if i not in i_keys.keys()]
	old_col = [i for i in range(0, v1_sheet.ncols) if index_convert(i) == -1]
	old_row = [(i_keys[i], i) for i in i_keys.keys() if i not in v2_keys.keys()]

	write_header(f_out, mode)
	write_added(v2, new_col, new_row, f_out, mode)
	write_removed(v2, old_col, old_row, f_out, mode)

	if mode == 'r' or mode == 'j':
		f_out.write('''
      <h3>Change Log</h3>
''')
	elif mode == 't':
		f_out.write("Change Log\n")

	workbook_name = ''
	for i in range(3,v2_sheet.nrows):
		v2_row = v2_sheet.row(i)
		#workbook_name = v1_file
		if v2_row[0].value in [j for i, j in new_row] or v2_row[0].value in [j for i, j in old_row]:
			continue
		v1_row = v1_sheet.row(i_keys[v2_row[0].value])
		write_modify(v1_row, v2_row, workbook_name, f_out, mode)
	
	write_footer(f_out, mode)
	f_out.close()

if __name__ == "__main__":
	if '-json' in sys.argv:
		mode = 'j'
		out_name = 'isotope2_3_json.html'
	elif '-rdfa' in sys.argv:
		mode = 'r'
		out_name = 'isotope2_3_rdfa.html'
	elif '-txt' in sys.argv:
		mode = 't'
		out_name = 'changelog2_3.txt'
	elif '-ttl' in sys.argv:
		mode = 'u'
		out_name = 'changelog2_3.ttl'

	v2_dir = join(separator, 'data', 'NGdata', 'v2')
	v3_dir = join(separator, 'data', 'NGdata', 'v3')
	
	v2_file = join(v2_dir, 'DB_final-55-7262_2015_03_08.xlsx')
	v3_file = join(v3_dir, 'NG_DB_final_2017_07_01.xlsx')

	compare(v2_file, v3_file, out_name, mode)
