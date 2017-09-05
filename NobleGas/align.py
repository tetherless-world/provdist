import xlrd, urllib, sys

def write_header(f_out, mode):
	if mode == 'h':
		f_out.write("""<html>
<head></head>
<style>
table, th, td {
    border: 1px solid black;
    border-collapse: collapse;
}
</style>
<body>

""")
	elif mode == 'r':
		f_out.write("""@prefix vo: <http://orion.tw.rpi.edu/~blee/VersionOntology.owl#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<http://example.com/NG/Version2> a vo:Version ;
	skos:prefLabel "%s" .

<http://example.com/NG/Version3> a vo:Version ;
	skos:prefLabel "%s" .

"""%(f0, f1))

def write_removed(f_out, mode, indicators):
	if mode == 't':
		f_out.write("Removed Rows\n")
	elif mode == 'h':
		f_out.write("""<h3>Removed Rows</h3>
	<table>
""")
	elif mode == 'r':
		c = 0

	for i in indicators:
		if mode == 't':
			f_out.write("".join([i, "\n"]).encode('utf8'))
		elif mode == 'h':
			f_out.write("".join(["\t\t<tr><td>", i, "</td></tr>\n"]).encode('utf8'))
		elif mode == 'r':
			f_out.write("""<http://example.com/NG/Version2> vo:hasAttribute <http://example.com/NG/Version2/%s> .
<http://example.com/NG/Version2/%s> vo:undergoes <http://example.com/Changelog#InvalidateChange%i> .
<http://example.com/Changelog#InvalidateChange%i> a vo:InvalidateChange ;
	vo:invalidatedBy <http://example.com/NG/Version3> .

"""%(i, i, c, c))
			c += 1

	if mode == 't' or mode == 'r':
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
		elif mode == 'r':
			f_out.write("""<http://example.com/NG/Version2> vo:absentFrom <http://example.com/Changelog#AddChange%i> .
<http://example.com/Changelog#AddChange%i> a vo:AddChange ;
	vo:resultsIn <http://example.com/NG/Version3/%s> .
<http://example.com/NG/Version3> vo:hasAttribute <http://example.com/NG/Version3/%s> .

"""%(c, c, i, i))
			
		c += 1
		if c%10 == 0:
			if mode == 't':
				f_out.write("\n")
			elif mode == 'h':
				f_out.write("</tr>\n\t\t<tr>")
	if mode == 't' or mode == 'r':
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
	elif mode == 'r':
		c = 0

	for i in set(index1[3:])&set(index2[3:]):
		r1 = s1.row(index1.index(i))
		r2 = s2.row(index2.index(i))
		changes = []
		for j in range(1,s1.ncols):
			if r1[j].value != r2[j].value:
				if mode == 'r':
					e = """<http://example.com/NG/Version2> vo:hasAttribute <http://example.com/NG/Version2/%s> ;
	vo:hasAttribute <http://example.com/NG/Version2/Column%i> .
<http://example.com/NG/Version2/%s> a vo:Attribute ;
	vo:undergoes <http://example.com/Changelog#ModifyChange%i> .
<http://example.com/NG/Version2/Column%i> a vo:Attribute ;
	vo:undergoes <http://example.com/Changelog#ModifyChange%i> .
<http://example.com/Changelog#ModifyChange%i> a vo:ModifyChange ;
	vo:resultsIn <http://example.com/NG/Version3/%s> ;
	vo:resultsIn <http://example.com/NG/Version3/Column%i> .
<http://example.com/NG/Version3> vo:hasAttribute <http://example.com/NG/Version3/%s> ;
	vo:hasAttribute <http://example.com/NG/Version3/Column%i> .
"""%(i, j, i, c, j, c, c, i, j, i, j)
					c += 1
				else:
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
				f_out.write("\n\t</table><br>\n")

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
