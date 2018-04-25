import dbfread
import csv
from glob import glob

data = "/data/ice/shape_files/pit_iop_v2_summary.dbf"
table = dbfread.DBF(data)

txt = glob("/data/ice/ascii/*strat.csv")
print txt

db = []
for fn in txt:
	f = open(fn)
	ll = f.readlines()
	d = [[c.strip() for c in r.split(',')] for r in ll[2:]]
	db.extend(d)
	f.close()

def load_data():
	for f in ff:
		with open(f) as in_file:
			ll = in_file.readlines()
			cr = csv.reader(ll[2:])
			for l in cr:
				db.append([c.strip() for c in l])

len(set([(d[0], d[1], d[6], d[7]) for d in db]))
