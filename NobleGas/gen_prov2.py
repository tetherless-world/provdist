from os.path import join, dirname, abspath, isfile
from os import sep as separator
import xlrd
import glob
import re


def indexConvert(index1):
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

def testAlignment():
	for i in range(0, 54):
		print 'version2: {:5} version1: {:5}'.format(i, indexConvert(i))

def comparePrint(i, val1, val2, changelog = None):
	formatted_val1 = val1
	formatted_val2 = val2
	if isinstance(val1, unicode):
		formatted_val1 = val1.encode('utf8', 'replace')
	if isinstance(val2, unicode):
		formatted_val2 = val2.encode('utf8', 'replace')
	if changelog:
		changelog.write('{0}|{1}|{2}\n'.format(i, formatted_val1, formatted_val2))
	else:
		print '{:5}  version1: {:10} version2: {:10}'.format(i, formatted_val1, formatted_val2)

def generateReference(indicator, references, out_file=None):
	if not isinstance(references, unicode):
		references = '%02i'%(references)
	reference = [x.strip() for x in re.split(',', references)]

	out_file.write('version2:compile%s a prov:Activity'%(indicator))

	for i in range(len(reference)):
		if len(reference[i]) == 2:
			out_file.write(' ;\n\t\tprov:used\tref:%s%s'%(indicator[:3], reference[i]))
		else:
			print indicator, references
			print 'this',reference[i]
	out_file.write(' .\n')

v2_dir = join(separator, 'data', 'NGdata', 'v2')
v2_file = join(v2_dir, 'DB_final-55-7262_2015_03_08.xlsx')

v1_dir = join(separator, 'data', 'NGdata', 'v1')
v1_file = join(v1_dir, 'America_906.xlsx')

excel_files = glob.glob(join(v1_dir, '*.xlsx'))

#testAlignment()

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

v2_turtle = open('provdist_v2.ttl', 'w')
v2_turtle.write('''@prefix version1: <http://ngdb.com/v1/> .
@prefix version2: <http://ngdb.com/v2/> .
@prefix ref: <http://ngdb.com/reference/> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n\n''')
workbook_name = ''
for i in range(3,v2_sheet.nrows):
	v2_row = v2_sheet.row(i)
	new_workbook_name =  indicator_map.get(v2_row[0].value, None)
	#workbook_name = v1_file
	if new_workbook_name == None:
		workbook_name = new_workbook_name
		#print 'New Entry: '+v2_row[0].value
		v2_turtle.write('''version2:%s\ta\tprov:Entity ;
\t\trdfs:label "%s" ;
\t\tprov:wasGeneratedBy version2:compile%s .\n'''%(v2_row[0].value, v2_row[0].value, v2_row[0].value))
		generateReference(v2_row[0].value, v2_row[11].value, v2_turtle)
		continue
	elif workbook_name == new_workbook_name:
		pass
	else:
		workbook_name = new_workbook_name
		v1_workbook = xlrd.open_workbook(workbook_name)
		v1_sheet = v1_workbook.sheet_by_index(0)
		v1_indicators = {b.value:a for a, b in list(enumerate(v1_sheet.col(0)))}
	#print v2_row[0].value
	v2_turtle.write('''version2:%s\ta\tprov:Entity ;
\t\trdfs:label "%s" ;
\t\tprov:wasGeneratedBy version2:compile%s .\n'''%(v2_row[0].value, v2_row[0].value, v2_row[0].value))
	generateReference(v2_row[0].value, v2_row[11].value, v2_turtle)
	#print '# Searching...'
	v1_row = v1_sheet.row(v1_indicators[v2_row[0].value])
	#print '# Comparing...'
	for j in range(0,54):
		if v2_row[j].value != v1_row[indexConvert(j)].value:
			v2_turtle.write('version2:%s prov:wasRevisionOf version1:%s .\n'%(v2_row[0].value, v1_row[0].value))
			break
	v2_turtle.write('\n')

v2_turtle.close()
#print v2_row[0].value
#print indicator_map[v2_row[0].value]

#v1_workbook = xlrd.open_workbook(v1_file)
#v1_sheet = v1_workbook.sheet_by_index(0)
#v1_row = v1_sheet.row(4)

