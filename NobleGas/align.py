import xlrd, urllib, sys

def write_header(f_out, mode):
	if mode == 'h':
		f_out.write("""<html>
<head></head>
<body>

""")

def write_removed(f_out, mode, indicators):
	if mode == 't':
		f_out.write("Removed Rows\n")
	elif mode == 'h':
		f_out.write("""<h3>Removed Rows</h3>
	<table>
""")
	for i in indicators:
		if mode == 't':
			f_out.write("".join([i, "\n"]).encode('utf8'))
		elif mode == 'h':
			f_out.write("".join(["\t\t<tr><td>", i, "</td></tr>\n"]).encode('utf8'))

	if mode == 't':
		f_out.write("\n")
	elif mode == 'h':
		f_out.write("	</table>\n\n")

def write_added(f_out, mode, indicators):
	if mode == 't':
		f_out.write("Added Rows\n")
	elif mode == 'h':
		f_out.write("""<h3>Added Rows</h3>
	<table>
		<tr>""")
	c = 0
	for i in indicators:
		if mode == 't':
			f_out.write("".join([i, " "]).encode('utf8'))
		elif mode == 'h':
			f_out.write("".join(["<td>", i, "</td>"]).encode('utf8'))
			
		c += 1
		if c%10 == 0:
			if mode == 't':
				f_out.write("\n")
			elif mode == 'h':
				f_out.write("</tr>\n\t\t<tr>")
	if mode == 't':
		f_out.write("\n")
	elif mode == 'h':
		if c%10 != 0:
			f_out.write("</tr>\n")
		f_out.write("\t</table>\n\n")
	
def get_modify(index, e1, e2, mode):
	if mode == 't':
		return "\t".join(["\t", str(index), unicode(e1.value), unicode(e2.value)])
	elif mode == 'h':
		return u"\t\t<tr><td>%i</td><td>%s</td><td>%s</td>"%(index, e1.value, e2.value)

def write_footer(f_out, mode):
	if mode == 'h':
		f_out.write("""</body>
</html>
""")

def compare(v1, v2, fn_out, mode):
	wb1 = xlrd.open_workbook("".join(['/data/NGdata/v2/', v1]))
	wb2 = xlrd.open_workbook("".join(['/data/NGdata/v3/', v2]))
	f_out = open(fn_out, 'w')

	s1 = wb1.sheet_by_index(0)
	s2 = wb2.sheet_by_index(0)

	index1 = [i.value for i in s1.col(0)]
	index2 = [i.value for i in s2.col(0)]

	old = set(index1[3:])-set(index2[3:])
	new = set(index2[3:])-set(index1[3:])

	write_header(f_out, mode)
	write_removed(f_out, mode, old)
	write_added(f_out, mode, new)

	if mode == 't':
		f_out.write("Modified Rows\n")
	elif mode == 'h':
		f_out.write("""<h3>Modified Rows</h3>
""")
	for i in set(index1[3:])&set(index2[3:]):
		r1 = s1.row(index1.index(i))
		r2 = s2.row(index2.index(i))
		changes = []
		for j in range(1,s1.ncols):
			if r1[j].value != r2[j].value:
				e = get_modify(j, r1[j], r2[j], mode)
				changes.append(e)
		if len(changes) != 0:
			if mode == "t":
				f_out.write("".join(["\t", i, "\n"]).encode('utf8'))
			elif mode == "h":
				out = u"""<span style="font-weight:bold">%s</span>
\t<table>\n"""%(i)
				f_out.write(out.encode('utf8'))

			f_out.write("\n".join(changes).encode('utf8'))

			if mode == 't':
				f_out.write("\n")
			elif mode == 'h':
				f_out.write("\n\t</table>\n")

	write_footer(f_out, mode)

if __name__ == "__main__":

	if '-html' in sys.argv:
		mode = 'h'
		out_name = "isotope2_3.html"
	elif '-ttl' in sys.argv:
		mode = 'r'
		out_name = "isotope2_3.ttl"
	else:
		mode = 't'
		out_name = "isotope2_3.txt"

	f0 = 'DB_final-55-7262_2015_03_08.xlsx'
	f1 = 'NG_DB_final_2017_07_01.xlsx'

	compare(f0, f1, out_name, mode)
