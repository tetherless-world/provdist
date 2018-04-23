import dbfread
from glob import glob

data = "/data/ice/shape_files/pit_iop_v2_strat.dbf"
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

len(set([(d[0], d[1], d[6], d[7]) for d in db]))
