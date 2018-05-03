import csv
from datetime import datetime

class dataset:
	def __init__(self, d_id, d_title):
		self.versions = {}
		self.num = int(d_id)
		self.title = d_title

	def add_file(self, v_num, v_pub, v_crt, v_mod, f_name, f_crt, f_rev, f_notes):
		if v_num not in self.versions:
			self.versions[v_num] = eol_ver(v_num, v_pub, v_crt, v_mod)
		self.versions[v_num].add_file(f_name, f_crt, f_rev, f_notes)

	def __repr__(self):
		out = ["%i: %s"%(self.num, self.title)]
		for i in sorted(self.versions.keys()):
			out.append(self.versions[i].string(4))
		return "\n".join(out)

class eol_ver:
	def __init__(self, v_num, t1, t2, t3):
		self.num = v_num
		self.files = []
		self.v_pub = datetime.strptime(t1, "%Y-%m-%d %H:%M:%S")
		self.v_crt = datetime.strptime(t2, "%Y-%m-%d %H:%M:%S")
		self.v_mod = datetime.strptime(t3, "%Y-%m-%d %H:%M:%S")

	def add_file(self, f_name, t1, t2, notes):
		new_f = eol_file(f_name, t1, t2, notes)
		self.files.append(new_f)

	def string(self, indent):
		ind = ' '*indent
		out = [ind+"%s: %s    %s    %s"%(self.num, str(self.v_pub), str(self.v_crt), str(self.v_mod))]
		for i in self.files:
			out.append(i.string(indent+4))
		return "\n".join(out)

	def __repr__(self):
		out = ["%s: %s    %s    %s"%(self.num, str(self.v_pub), str(self.v_crt), str(self.v_mod))]
		for i in self.files:
			out.append("    "+i.__repr__())
		return "\n".join(out)

class eol_file:
	def __init__(self, f_name, t1, t2, notes):
		self.name = f_name
		self.f_create = datetime.strptime(t1, "%Y-%m-%d %H:%M:%S")
		self.f_revise = datetime.strptime(t2, "%Y-%m-%d %H:%M:%S")
		self.f_notes  = notes

	def string(self, indent):
		out = ' '*indent
		return out+self.name

	def __repr__(self):
		return self.name

def import_eol(fname):
	f = open(fname)
	f_reader = csv.reader(f, delimiter='|')
	f_reader.next()
	header = [i.strip() for i in f_reader.next()[1:-1]]
	f_reader.next()

	datasets = {}
	for i in f_reader:
		row = [j.strip() for j in i[1:-1]]
		if len(row) < 10:
			continue
		if int(row[0]) not in datasets:
			datasets[int(row[0])] = dataset(int(row[0]), row[1])

		datasets[int(row[0])].add_file(row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9])
	return datasets

if __name__ == "__main__":
	filedir  = "/data/EOL/"
	#filename = "dataset_files_version_metadata.txt"
	filename = "EOL_dataset_version_metadata.txt"

	datasets = import_eol(filedir+filename)
	print len(datasets.keys())

	num_ver = {}
	for i in datasets.keys():
		how_many_versions = len(datasets[i].versions.keys())
		if how_many_versions not in num_ver:
			num_ver[how_many_versions] = 1
		else:
			num_ver[how_many_versions] += 1
	for i in sorted(num_ver.keys()):
		print i, num_ver[i]
