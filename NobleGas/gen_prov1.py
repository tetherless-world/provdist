from os.path import join, dirname, abspath, isfile
from os import sep as separator
import glob
import xlrd
import re

v1_dir = join(separator, 'data', 'NGdata', 'v1')

excel_files = glob.glob(join(v1_dir, '*.xlsx'))

v1_file = open('provdist_v1.ttl', 'w')
v1_file.write('''@prefix version1: <http://ngdb.com/v1/> .
@prefix ref: <http://ngdb.com/reference/> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n\n''')
for excel_file in excel_files:
	file_workbook = xlrd.open_workbook(excel_file)
	file_sheet = file_workbook.sheet_by_index(0)
	indicators = file_sheet.col(0)
	references = file_sheet.col(11)
	for i in range(4, file_sheet.nrows):
		v1_file.write('''version1:%s\ta\tprov:Entity;
\t\trdfs:label "%s";
\t\tprov:wasGeneratedBy version1:compile%s .\n'''%(indicators[i].value, indicators[i].value, indicators[i].value))
		if isinstance(references[i].value, float):
			reference = [str(int(references[i].value))]
		elif isinstance(references[i].value, unicode):
			reference = re.split(',|;', references[i].value)
		else:
			print "What?!"

		v1_file.write('version1:compile%s a prov:Activity'%(indicators[i].value))

		first = True
		for j in range(len(reference)):
			if re.match("([0-9]+)-([0-9]+)", reference[j]):
				x, y = reference[0].split('-')
				for k in range(int(x), int(y)+1):
					v1_file.write(' ;\n\t\tprov:used\tref:%s%02i'%(indicators[i].value[:3], k))
			else:
				v1_file.write(' ;\n\t\tprov:used\tref:%s%02i'%(indicators[i].value[:3], int(reference[j])))
		v1_file.write(' .\n\n')
