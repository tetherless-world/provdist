from os.path import join, dirname, abspath, isfile
from os import sep as separator
import xlrd
import glob
import re


def index_convert(index1):
	if index1 < 17:
		return index1
	elif index1 < 24:
		return index1+1
	elif index1 < 26:
		return 26+(3*(index1-24))
	elif index1 < 28:
		return 45+(3*(index1-26))
	elif index1 < 32:
		return 53+(9*(index1-28))
	elif index1 < 36:
		return 88+(2*(index1-32))
	elif index1 < 38:
		return 95+(4*(index1-36))
	elif index1 < 41:
		return 102+(2*(index1-38))
	elif index1 < 43:
		return 112+(2*(index1-41))
	elif index1 == 43:
		return 172
	elif index1 < 50:
		return 174+(3*(index1-44))
	elif index1 < 54:
		return 191+(index1-50)
	else:
		print 'Error: Out of bounds'
		return -1


def test_alignment():
	for i in range(0, 54):
		print 'version2: {:5} version1: {:5}'.format(i, index_convert(i))

def compare_print(i, val1, val2, changelog = None):
	formatted_val1 = val1
	formatted_val2 = val2
	if isinstance(val1, unicode):
		formatted_val1 = val1.encode('utf8', 'replace')
	if isinstance(val2, unicode):
		formatted_val2 = val2.encode('utf8', 'replace')
	if changelog:
		changelog.write('''      <tr property="vo:hasChange" typeof="vo:Change">
        <td property="http://www.w3.org/2000/01/rdf-schema#label">{:5}</td>
        <td property="vo:PreData">{:10}</td>
        <td property="vo:PostData">{:10}</td>
      </tr>\n'''.format(i, formatted_val1, formatted_val2))
	else:
		print '{:5}  version1: {:10} version2: {:10}'.format(i, formatted_val1, formatted_val2)

v2_dir = join(separator, 'data', 'NGdata', 'v2')
v1_dir = join(separator, 'data', 'NGdata', 'v1')

excel_files = glob.glob(join(v1_dir, '*.xlsx'))

v2_file = join(v2_dir, 'DB_final-55-7262_2015_03_08.xlsx')
v1_file = join(v1_dir, 'America_906.xlsx')

#test_alignment()

indicator_map = {}
for excel_file in excel_files:
	print 'Importing: ' + excel_file
	file_workbook = xlrd.open_workbook(excel_file)
	file_sheet = file_workbook.sheet_by_index(0)
	indicators = file_sheet.col(0)
	for i in range(4, file_sheet.nrows):
		indicator_map[indicators[i].value] = excel_file

v2_workbook = xlrd.open_workbook(v2_file)
v2_sheet = v2_workbook.sheet_by_index(0)

changelog = open('changelog.html', 'w')
changelog.write('''<html>
<head>
</head>
<body vocab="http://www.w3.org/nw/prov#" prefix="vo: http://example.com/versioning/ v1: http://ngdb.com/v1/ v2: http://ngdb.com/v2/">
''')
workbook_name = ''
for i in range(3,v2_sheet.nrows):
	v2_row = v2_sheet.row(i)
	#workbook_name = v1_file
	if indicator_map.get(v2_row[0].value, None) == None:
		workbook_name = indicator_map.get(v2_row[0].value, None)
		print 'New Entry: '+v2_row[0].value
		changelog.write('  <p resource="v2:{0:5}" typeof="Entity">\n    New Indicator: <span property="http://www.w3.org/2000/01/rdf-schema#label">{0:5}</span>\n    New Values\n  </p>'.format(v2_row[0].value))
		continue
	elif workbook_name == indicator_map.get(v2_row[0].value, None):
		pass
	else:
		workbook_name = indicator_map.get(v2_row[0].value, None)
		v1_workbook = xlrd.open_workbook(workbook_name)
		v1_sheet = v1_workbook.sheet_by_index(0)
	#print v2_row[0].value
	changelog.write('''  <div resource="v2:%s" typeof="Entity">
    <span style="font-weight:bold" property="http://www.w3.org/2000/01/rdf-schema#label">%s</span>
    <table property='vo:hasChangelog' resource='#%s' typeof='Log'>
      <tr>
        <td>Column</td>
        <td>Version 1</td>
        <td>Version 2</td>
      </tr>\n'''%(v2_row[0].value, v2_row[0].value, v2_row[0].value))
	#print '# Searching...'
	for j in range(4, v1_sheet.nrows):
		#print '  version 1: {:5} version 2: {:5}'.format(v1_sheet.cell(j,0).value, v2_row[0].value)
		if v2_row[0].value == v1_sheet.cell(j,0).value:
			#print '    FOUND'
			v1_row = v1_sheet.row(j)
			break
	#print '# Comparing...'
	for j in range(0,54):
		if v2_row[j].value != v1_row[index_convert(j)].value:
			#compare_print(j, v1_row[index_convert(j)].value, v2_row[j].value)
			compare_print(j, v1_row[index_convert(j)].value, v2_row[j].value, changelog)
	changelog.write('  </table></div><br>\n')

changelog.write('</body>\n</html>')
changelog.close()
#print v2_row[0].value
#print indicator_map[v2_row[0].value]

#v1_workbook = xlrd.open_workbook(v1_file)
#v1_sheet = v1_workbook.sheet_by_index(0)
#v1_row = v1_sheet.row(4)

