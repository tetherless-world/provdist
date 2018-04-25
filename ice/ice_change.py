from glob import glob
from datetime import datetime
import csv
import dbfread
import sys

class Version:
	unique_id = None

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return self.unique_id == other.unique_id
		else:
			return self.unique_id == other

class StratVer(Version):

	def __init__(self, headers, values):
		v = [i.strip() for i in csv.reader([values]).next()]
		self.data = {}
		self.load_strat(headers, v)
		self.unique_id = (self.data['PIT_NAME'], self.data['IOP'], int(self.data['TOP']), int(self.data['BOT']))		

	def load_strat(self, headers, v):
		for i in range(len(headers)):
			if i == 2:
				self.data[headers[i]] = datetime.strptime(v[i], "%Y-%m-%d").date()
			elif i > 2 and i < 14:
				if '.' in v[i]:
					self.data[headers[i]] = float(v[i])
				else:
					self.data[headers[i]] = int(v[i])
			else:
				self.data[headers[i]] = v[i]

class SummVer(Version):

	def __init__(self, headers, values):
		v = [i.strip() for i in csv.reader([values]).next()]
		self.data = {}
		self.load_summ(headers, v)
		self.unique_id = (self.data['PIT'], self.data['IOP'])

	def load_summ(self, headers, v):
		for i in range(len(headers)):
			if i == 3:
				try:
					self.data[headers[i]] = datetime.strptime(v[i], "%Y-%m-%d").date()
				except ValueError:
					self.data[headers[i]] = None
			elif (i > 3 and i < 7) or (i > 8 and i < 11) or (i > 11 and i < 34):
				try:
					self.data[headers[i]] = int(v[i])
				except ValueError:
					pass
				try:
					self.data[headers[i]] = float(v[i])
				except ValueError:
					self.data[headers[i]] = v[i]
			else:
				self.data[headers[i]] = v[i]

def helper_factory( section, mode, arg1=None):
	if mode == "strat":
		if section == "names":
			return ("/data/ice/shape_files/pit_iop_v2_strat.dbf", "strat")
		elif section == "key":
			return "Key = (PIT, IOP, TOP, BOT)\n\n"
		elif section == "mapper":
			return strat_col_map
		elif section == "table_ids":
			return [(r['PIT'], r['IOP'], r['TOP'], r['BOT']) for r in arg1]
	elif mode == "summary":
		if section == "names":
			return ("/data/ice/shape_files/pit_iop_v2_summary.dbf", "summary")
		elif section == "key":
			return "Key = (PIT, IOP)\n\n"
		elif section == "mapper":
			return summ_col_map
		elif section == "table_ids":
			return [(r['PIT'], r['IOP']) for r in arg1]

def strat_col_map(index, mode):
	if mode == "ascii":
		if index == "DATE_":
			return "DATE"
		elif index == "PIT":
			return "PIT_NAME"
	elif mode == "shape":
		if index == "DATE":
			return "DATE_"
		elif index == "PIT_NAME":
			return "PIT"
	return index

def summ_col_map(index, mode):
	if mode == "ascii" and index == "DATE_":
			return "DATE"
	elif mode == "shape" and index == "DATE":
			return "DATE_"
	return index

def ice_import(category):
	if category == "strat":
		fn = glob("/data/ice/ascii/*strat.csv")
	elif category == "summary":
		fn = glob("/data/ice/ascii/*summary.csv")

	entries = {}
	for i in fn:
		f = open(i)
		ll = f.readlines()
		headers = [c.strip() for c in csv.reader([ll[0]]).next()]
		for j in ll[2:]:
			if category == "strat":
				sv = StratVer(headers, j)
			elif category == "summary":
				sv = SummVer(headers, j)
			entries[sv.unique_id] = sv
		f.close()
	return headers, entries

def generate_logs(table_name, text_name, f):
	table = dbfread.DBF(table_name)
	table_ids = helper_factory("table_ids", text_name, table)

	headers, text_entries = ice_import(text_name)

	f.write("Shape Entries not in Ascii Files\n")
	for i in table_ids:
		if i not in text_entries.keys():
			f.write(str(i)+"\n")
	f.write("\n")

	f.write("Shape Columns not in Ascii Files\n")
	for i in table.field_names:
		if i not in [column_map(j, "shape") for j in headers]:
			f.write(i+"\n")
	f.write("\n")

	f.write("Ascii Entries not in Shape Files\n")
	for i in sorted(text_entries.keys()):
		if i not in table_ids:
			f.write(str(i)+"\n")
	f.write("\n")

	f.write("Ascii Columns not in Shape Files\n")
	for i in headers:
		if i not in [column_map(j, "ascii") for j in table.field_names]:
			f.write(i+"\n")
	f.write("\n")

	c = 0
	f.write("Modified Entries\n")
	for r in table:
		if text_name == "strat":
			i = (r['PIT'], r['IOP'], r['TOP'], r['BOT'])
		elif text_name == "summary":
			i = (r['PIT'], r['IOP'])

		if i in text_entries.keys():
			v = text_entries[i]
			start = True
			for j in table.field_names:
				if column_map(j, "ascii") not in v.data.keys():
					pass
				elif r[j] == 'NoData' and v.data[column_map(j, "ascii")] == '-999':
					pass
				elif r[j] != v.data[column_map(j, "ascii")]:
					if start:
						f.write("%s\n"%(str(v.unique_id)))
						f.write("Column|\tShape|\tAscii\n")
						start = False
					f.write("%s|\t%s|\t%s\n"%(j, r[j], v.data[column_map(j, "ascii")]))
					#print v.unique_id, j, r[j], v.data[attribute_map(j)]
					c += 1
			if not start:
				f.write("\n")

if __name__ == "__main__":
	if "-strat" in sys.argv:
		table_name, text_name = helper_factory("names", "strat")
	elif "-summ" in sys.argv:
		table_name, text_name = helper_factory("names", "summary")

	change_log = "changelog_"+text_name+".txt"
	f = open(change_log, 'w')
	f.write("Change Log %s to ascii files\n"%(table_name.split('/')[-1]))
	f.write(helper_factory("key", text_name))

	column_map = helper_factory("mapper", text_name)
	generate_logs(table_name, text_name, f)
	f.close()
