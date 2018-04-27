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
changelog = open('DTDI/CUlog.txt', 'w')
changelog.write('''%s to %s
'''%(filename1, filename2))

changelog.write("\n")

workbook = xlrd.open_workbook(v1_file)
sheet_v1 = workbook.sheet_by_name('Database')
#Maps the Excel key to it's appropriate row number
v1_indicators = { }
for a, b in list(enumerate(sheet_v1.col(2)[1:])):
	if b.value not in v1_indicators:
		v1_indicators[b.value]=[a+1]
	else:
		v1_indicators[b.value].append(a)
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

changelog.write('''Columns added to %s\n'''%(filename2))

print "Added"
for i in range(0,sheet_v2.ncols):
	v1_index = indexConvert(i)
	v2_value = formatText(sheet_v2.cell(0,i).value)
	if v1_index == -1:
		print i, v2_value
		changelog.write('''%i\t%s
'''%(i, v2_value))
changelog.write("\n")

changelog.write('''Rows added to %s\n'''%(filename2))

print "Added"
for i in v2_indicators.keys():
	if i not in v1_indicators.keys():
		print v2_indicators[i], i
		out = u'''%i\t%s
'''%(v2_indicators[i], i)
		changelog.write(out.encode('utf8'))
changelog.write("\n")

########################################
####                                ####
####            REMOVE              ####
####                                ####
########################################

changelog.write('''Columns added to %s
Column #\tHeader
'''%(filename1))

print "Removed"
for i in [5, 32]:
	v1_value = formatText(sheet_v1.cell(0,i).value)
	changelog.write('''%i\t%s
'''%(i, v1_value))
changelog.write('''
''')

changelog.write('''Rows added to %s
Row #\tMineral
'''%(filename1))

print "Removed"
for i in v1_indicators.keys():
	if i not in v2_indicators.keys():
		for j in v1_indicators[i]:
			print j, i
			out = u'''%i\t%s
'''%(j, i)
			changelog.write(out.encode('utf8'))
changelog.write('''
''')

########################################
####                                ####
####           MODIFY               ####
####                                ####
########################################

changelog.write('''
Change Log
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
	changelog.write('''
%s
Column v1\tColumn v2\tVersion 1\tVersion 2\n'''%(v2_key))
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
				changelog.write('''{:2}\t({:2})\t{:>10}\t{:>10}\n'''.format(index, i, formatted_v1, formatted_v2))


#		else:
#			changelog.write('''      <tr property="vo:undergoes" typeof="vo:Change">
#        <td></td>
#        <td>(<span property="vo:PostIndicator">{:2}</span>)</td>
#        <td></td>
#        <td>{:>10}</td>
#      </tr>\n'''.format(i, formatted_v2))
	changelog.write("\n")

changelog.close()
#print v1_row
#print v2_row
