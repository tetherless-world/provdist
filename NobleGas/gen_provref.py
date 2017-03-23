from os.path import join, dirname, abspath, isfile
from os import sep as separator
import xlrd
import glob
import re

v2_dir = join(separator, 'data', 'NGdata', 'v2')
v2_file = join(v2_dir, 'DB_final-55-7262_2015_03_08.xlsx')
workbook = xlrd.open_workbook(v2_file)
ref_sheet = workbook.sheet_by_index(1)

reference_file = open('provdist_ref.ttl', 'w')
reference_file.write('''@prefix ref: <http://ngdb.com/reference/> .
@prefix version2: <http://ngdb.com/v2/> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n\n''')
for index, reference in zip(ref_sheet.col(1)[1:], ref_sheet.col(2)[1:]):
	formatted_index = index.value
	formatted_refer = reference.value
	if isinstance(index.value, unicode):
		formatted_index = index.value.encode('utf8', 'replace').strip()
	if isinstance(reference.value, unicode):
		formatted_refer = reference.value.encode('utf8', 'replace').replace('"','\\"')
	reference_file.write('''ref:%s
\ta prov:Entity;
\trdfs:label "%s";
\trdfs:description "%s" .\n\n'''% (formatted_index, formatted_index, formatted_refer))

reference_file.close()
