from os.path import join, dirname, abspath, isfile
from os import sep as separator
import xlrd, sys, json
import glob
import re


def index_convert(index1):
	if index1 < 17:
		return index1
	elif index1 < 24:
		return index1+1
	elif index1 < 26:
		return 26+(3*(index1-24))
	elif index1 < 28:
		return 44+(3*(index1-26))
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

def test_alignment():
	for i in range(0, 54):
		print 'version2: {:5} version1: {:5}'.format(i, index_convert(i))

def compare_print(mode, key, val1, val2, v1_file, v1_index = 0, v2_index = 0, changelog = None):
	if changelog:
		if mode == 'r':
			out = u'''        <tr  about="Change{}{}" typeof="vo:ModifyChange">
          <td align="right" rev="vo:Undergoes" resource="v1:Attribute{}{}v1" typeof="vo:Attribute">{:2}({})</td>
          <td property="vo:resultsIn" resource="v2:Attribute{}{}v2" typeof="vo:Attribute">{:2}</td>
          <td>{:>10}</td>
          <td>{:>10}</td>
          <span about="Version1" property="vo:hasAttribute" resource="v1:Attribute{}{}v1"></span>
          <span about="Version2" property="vo:hasAttribute" resource="v2:Attribute{}{}v2"></span>
        </tr>\n'''.format(key, v2_index, key, v1_index, v1_index, v1_file, key, v2_index, v2_index, val1, val2, key, v1_index, key, v2_index)
		elif mode == 'j':
			out = u'''        <tr  id="ModifyChange{}{}">
          <td align="right">{:2}({})</td>
          <td>{:2}</td>
          <td>{:>10}</td>
          <td>{:>10}</td>
          <script type="application/ld+json">\n'''.format(key, v2_index, v1_index, v1_file, v2_index, val1, val2)
		elif mode == 't':
			out = u"{:2}({})\t{:2}\t{:>10}\t{:>10}\n".format(v1_index, v1_file, v2_index, val1, val2)
		elif mode == 'u':
			out = u"""<http://example.com/NG/Version1> vo:hasAttribute <http://example.com/NG/Version1/%s> ;
        vo:hasAttribute <http://example.com/NG/Version1/Column%i> .
<http://example.com/NG/Version1/%s> a vo:Attribute ;
        vo:undergoes <http://example.com/Changelog#ModifyChange%s%i> .
<http://example.com/NG/Version1/Column%i> a vo:Attribute ;
        vo:undergoes <http://example.com/Changelog#ModifyChange%s%i> .
<http://example.com/Changelog#ModifyChange%s%i> a vo:ModifyChange ;
        vo:resultsIn <http://example.com/NG/Version2/%s> ;
        vo:resultsIn <http://example.com/NG/Version2/Column%i> .
<http://example.com/NG/Version2> vo:hasAttribute <http://example.com/NG/Version2/%s> ;
        vo:hasAttribute <http://example.com/NG/Version2/Column%i> .

"""%(key, v1_index, key, key, v2_index, v1_index, key, v2_index, key, v2_index, key, v2_index, key, v2_index)
		changelog.write(out.encode('utf8'))
		if mode == 'j':
			json1 = {
"@context":context,
"@type":"vo:Attribute" ,
"@id":"".join(["http://ngdb.com/v1/Attribute", key, str(v1_index)]) ,
"label":key ,
"undergoes":"".join([host, "ModifyChange", key, str(v2_index)]) ,
"@reverse" :    { "hasAttribute" : "Version1" }
}
			json2 = {
"@context":context,
"@type":"vo:ModifyChange",
"@id":"".join([host, "ModifyChange", key, str(v2_index)]) ,
"resultsIn":"".join(["http://ngdb.com/v2/Attribute", key, str(v2_index)])
}
			json3 = {
"@context":context,
"@type":"vo:Attribute" ,
"@id":"".join(["http://ngdb.com/v2/Attribute", key, str(v2_index)]) ,
"label":key ,
"@reverse" :    { "hasAttribute" : "Version2" }
}
			json.dump([json1, json2, json3], changelog, indent=4, sort_keys=True)
			changelog.write('''
          </script>
        </tr>
''')
	else:
		print '{:5}  version1: {:10} version2: {:10}'.format(key, val1, val2)

labels = {17:"SAMPLING - DEPTH - >,<",
		  25:"[He] - ppm - >,<", 27:"[He] - ppm - err", 28:"[He] - mkcc/ - >,<", 30:"[He] - mkcc/ - err", 31:"[He] - mol/ - >,<", 32:"[He] - mol/ - L H2O", 33:"[He] - mol/ - err",
		  34:"[He+Ne] - ppm - >,<", 35:"[He+Ne] - ppm", 36:"[He+Ne] - ppm - err", 37:"[He+Ne] - mkcc/ - >,<", 38:"[He+Ne] - mkcc/ - g H2O", 39:"[He+Ne] - mkcc/ - err", 40:"[He+Ne] - mol/ - >,<", 41:"[He+Ne] - mol/ - L H2O", 42:"[He+Ne] - mol/ - err",
		  43:"[Ne] - ppm - >,<", 45:"[Ne] - ppm - err", 46:"[Ne] - mkcc/ - >,<", 48:"[Ne] - mkcc/ - err", 49:"[Ne] - mol/ - >,<", 50:"[Ne] - mol/ - L H2O", 51:"[Ne] - mol/ - err",
		  52:"[20Ne] - ppm - >,<", 54:"[20Ne] - ppm - err", 55:"[20Ne] - mkcc/ - >,<", 56:"[20Ne] - mkcc/ - g H2O", 57:"[20Ne] - mkcc/ - err", 58:"[20Ne] - mol/ - >,<", 59:"[20Ne] - mol/ - L H2O", 60:"[20Ne] - mol/ - err",
		  61:"[Ar] - ppm - >,<", 63:"[Ar] - ppm - err", 64:"[Ar] - mkcc/ - >,<", 65:"[Ar] - mkcc/ - g H2O", 66:"[Ar] - mkcc/ - err", 67:"[Ar] - mol/ - >,<", 68:"[Ar] - mol/ - L H2O", 69:"[Ar] - mol/ err",
 		  70:"[Kr] - ppm - >,<", 72:"[Kr] - ppm - err", 73:"[Kr] - mkcc/ - >,<", 74:"[Kr] - mkcc/ - g H2O", 75:"[Kr] - mkcc/ - err", 76:"[Kr] - mol/ - >,<", 77:"[Kr] - mol/ - L H2O", 78:"[Kr] - mol/ err",
		  79:"[Xe] - ppm - >,<", 81:"[Xe] - ppm - err", 82:"[Xe] - mkcc/ - >,<", 83:"[Xe] - mkcc/ - g H2O", 84:"[Xe] - mkcc/ - err", 85:"[Xe] - mol/ - >,<", 86:"[Xe] - mol/ - L H2O", 87:"[Xe] - mol/ err",
		  89:"3He/4He - (R/Ra)me - err", 91:"3He/4He - (R/Ra)corr - err", 93:"3He/4He - Rme - E-8 - err", 96:"3He/4He - Rcorr - E-8 - err", 97:"Rank",
		  98:"He/Ne - >,<", 100:"He/Ne - >,<", 101:"4He/20Ne - >,<", 103:"4He/20Ne - err", 105:"20Ne/22Ne - err", 107:"21Ne/22Ne - (xE-2) - err", 108:"21Ne/20Ne", 109:"21Ne/20Ne - err",
		  110:"22Ne/20Ne", 111:"22Ne/20Ne - err", 113:"38Ar/36Ar - err", 115:"40Ar/36Ar - err", 116:"delta(40Ar)rad", 117:"delta(40Ar)rad - err",
		  118:"He/Ar - He/ - /Ar(air) - >,<", 119:"He/Ar - He/ - /Ar(air)", 120:"He/Ar - He/ - /Ar(air) - err", 121:"He/Ar - 4He/ - /36Ar - >,<", 122:"He/Ar - 4He/ - /36Ar", 123:"He/Ar - 4He/ - /36Ar - err",
		  124:"He/Ar - 4He/ - /40Ar(air) - >,<", 125:"He/Ar - 4He/ - /40Ar(air)", 126:"He/Ar - 4He/ - /40Ar(air) - err",
		  127:"f(He)=(He/Ar)s/(He/Ar)air - >,<", 128:"f(He)=(He/Ar)s/(He/Ar)air", 129:"f(He)=(He/Ar)s/(He/Ar)air - err",
		  130:"Ne/Ar - Ne/ - /Ar(air) - >,<", 131:"Ne/Ar - Ne/ - /Ar(air)", 132:"Ne/Ar - Ne/ - /Ar(air) - err", 133:"Ne/Ar - 20Ne/ - /36Ar - >,<", 134:"Ne/Ar - 20Ne/ - /36Ar", 135:"Ne/Ar - 20Ne/ - /36Ar - err",
		  136:"Ne/Ar - 20Ne/ - /40Ar(air) - >,<", 137:"Ne/Ar - 20Ne/ - /40Ar(air)", 138:"Ne/Ar - 20Ne/ - /40Ar(air) - err", 139:"Ne/Ar - 22Ne/ - /36Ar - >,<", 140:"Ne/Ar - 22Ne/ - /36Ar", 141:"Ne/Ar - 22Ne/ - /36Ar - err",
		  142:"Ne/Ar - 22Ne/ - /40Ar(air) - >,<", 143:"Ne/Ar - 22Ne/ - /40Ar(air)", 144:"Ne/Ar - 22Ne/ - /40Ar(air) - err",
		  145:"f(Ne)=(Ne/Ar)s/(Ne/Ar)air - >,<", 146:"f(Ne)=(Ne/Ar)s/(Ne/Ar)air", 147:"f(Ne)=(Ne/Ar)s/(Ne/Ar)air - err",
		  148:"Kr/Ar - Kr/ - /Ar(air) - >,<", 149:"Kr/Ar - Kr/ - /Ar(air)", 150:"Kr/Ar - Kr/ - /Ar(air) - err", 151:"Kr/Ar - 84Kr/ - /36Ar - >,<", 152:"Kr/Ar - 84Kr/ - /36Ar", 153:"Kr/Ar - 84Kr/ - /36Ar - err",
		  154:"Kr/Ar - 84Kr/ - /40Ar(air) - >,<", 155:"Kr/Ar - 84Kr/ - /40Ar(air)", 156:"Kr/Ar - 84Kr/ - /40Ar(air) - err",
		  157:"f(Kr)=(Kr/Ar)s/(Kr/Ar)air - >,<",158:"f(Kr)=(Kr/Ar)s/(Kr/Ar)air", 159:"f(Kr)=(Kr/Ar)s/(Kr/Ar)air - err",
		  160:"Xe/Ar - Xe/ - /Ar(air) - >,<", 161:"Xe/Ar - Xe/ - /Ar(air)", 162:"Xe/Ar - Xe/ - /Ar(air) - err", 163:"Xe/Ar - 132Xe/ - /36Ar - >,<", 164:"Xe/Ar - 132Xe/ - /36Ar", 165:"Xe/Ar - 132Xe/ - /36Ar - err",
		  166:"Xe/Ar - 132Xe/ - /40Ar(air) - >,<", 167:"Xe/Ar - 132Xe/ - /40Ar(air)", 168:"Xe/Ar - 132Xe/ - /40Ar(air) - err",
		  169:"f(Xe)=(Xe/Ar)s/(Xe/Ar)air - >,<", 170:"f(Xe)=(Xe/Ar)s/(Xe/Ar)air", 171:"f(Xe)=(Xe/Ar)s/(Xe/Ar)air - err",
		  173:"H2 - >,<", 175:"H2 - ppm - err", 176:"O2 - >,<", 178:"O2 - ppm - err", 179:"N2 - >,<", 181:"N2 - ppm - err", 182:"CO2 - >,<", 184:"CO2 - ppm - err", 185:"CH4 - >,<", 187:"CH4 - ppm - err",
		  188:"H2S - >,<", 190:"H2S - ppm - err"}

context = "https://orion.tw.rpi.edu/~blee/provdist/GCMD/VO.jsonld"
host = "http://orion.tw.rpi.edu/~blee/provdist/NobleGas/changelog_json.html#"
#test_alignment()


#print v2_row[0].value
#print indicator_map[v2_row[0].value]

#v1_workbook = xlrd.open_workbook(v1_file)
#v1_sheet = v1_workbook.sheet_by_index(0)
#v1_row = v1_sheet.row(4)

def write_modify(r1, r2, workbook, f_out, mode):
	if mode == 'r':
		out = u'''  <div about="Version1" rel="vo:hasAttribute">
    <div resource="v2:%s" typeof="vo:Attribute">
      <span style="font-weight:bold" property="http://www.w3.org/2000/01/rdf-schema#label">%s</span>
      <table rel="vo:Undergoes">
'''%(r2[0].value, r2[0].value)
	elif mode == 'j':
		out = u'''
    <div about="v2:%s">
      <span style="font-weight:bold" property="http://www.w3.org/2000/01/rdf-schema#label">%s</span>
      <table>
'''%(r2[0].value, r2[0].value)
	elif mode == 't':
		out = u"%s\n"%(r2[0].value)
	elif mode == 'u':
		out = u""

	if mode == 'r' or mode == 'j':
		out = out+'''        <tr>
          <th>Column v1</th>
          <th>Column v2</th>
          <th>Version 1</th>
          <th>Version 2</th>
        </tr>\n'''
	elif mode == 't':
		out = out+"Column v1\tColumn v2\tVersion 1\tVersion 2\n"
	f_out.write(out.encode('utf8'))
		#print '# Searching...'
		#print '# Comparing...'
	for i in range(0,54):
		if r2[i].value != r1[index_convert(i)].value:
			#compare_print(j, v1_row[index_convert(j)].value, v2_row[j].value)
			compare_print(mode, r2[0].value, r1[index_convert(i)].value, r2[i].value, workbook.split('/')[-1], index_convert(i), i, f_out)
	if mode == 'r' or mode == 'j':
		f_out.write('  </table></div><br>\n')
	elif mode == 't' or mode == 'u':
		f_out.write("\n")

def write_removed(v2, col, row, f_out, mode):
	if mode == 'r' or mode == 'j':
		f_out.write('''
      <h3>Columns invalidated by %s</h3>
      <table about="Version2">
'''%(v2.split('/')[-1]))
	elif mode == 't':
		f_out.write("\nColumns invalidated by %s\n"%(v2.split('/')[-1]))

	print "Removed Column"
	for i in col:
        	v1_value = labels.get(i, "")
		if mode == 'r':
			out = u'''        <tr resource="InvlidateChange%i" rev="vo:invalidatedBy" typeof="vo:InvalidateChange">
		<td resource="Attribute%i" rev="vo:Undergoes" typeof="vo:Attribute">%i</td>
          <td about="Attribute%i" property="http://www.w3.org/2000/01/rdf-schema#label">%s</td>
          <span about="Version1" property="vo:hasAttribute" resource="Attribute%i"/>
        </tr>
'''%(i, i, i, i, v1_value, i)
		elif mode == 'j':
			out = u'''        <tr id="InvlidateChange%i" about="InvlidateChange%i">
          <td>%i</td>
          <td>%s</td>
          <script type="application/ld+json">
'''%(i, i, i, v1_value)
		elif mode == 't':
			out = u"%i\t%s\n"%(i, v1_value)
		elif mode == 'u':
			out = u"""<http://example.com/NG/Version1> vo:hasAttribute <http://example.com/NG/Version1/Column%s> .
<http://example.com/NG/Version1/%s> vo:undergoes <http://example.com/Changelog#InvalidateChange%i> .
<http://example.com/Changelog#InvalidateChange%i> a vo:InvalidateChange ;
	vo:invalidatedBy <http://example.com/NG/Version2> .

"""%(i, i, i, i)
		f_out.write(out.encode('utf8'))
		if mode == 'j':
			json1 = {
"@context":context,
"@type":"vo:Attribute" ,
"@id":"".join(["http://ngdb.com/v1/Attribute", str(i)]) ,
"label": v1_value,
"undergoes":"".join([host, "InvalidateChange", str(i)]) ,
"@reverse" :    { "hasAttribute" : "Version1" }
}
			json2 = {
"@context":context,
"@type":"vo:InvalidateChange" ,
"@id": "".join([host, "InvalidateChange", str(i)]) ,
"invalidatedBy"  :   "Version2"
}
			json.dump([json1, json2], f_out, indent=4, sort_keys=True)
			f_out.write('''
          </script>
        </tr>
''')
			

	if mode == 'r' or mode == 'j':
		f_out.write('''      </table>
      <h3>Rows invalidated by %s</h3>
      <table about="Version2">
'''%(v2.split('/')[-1]))
	elif mode == 't':
		f_out.write("\nRows invalidated by %s\n"%(v2.split('/')[-1]))
	elif mode == 'u':
		f_out.write("\n")

	print "Removed Row"
	workbook_name = ''
	for i, j in sorted(row, key=lambda x: x[0]):
	        if workbook_name != j:
			workbook_name = j
			v1_workbook = xlrd.open_workbook(workbook_name)
			v1_sheet = v1_workbook.sheet_by_index(0)
			v1_col = v1_sheet.col(0)
			v1_col = [k.value for k in v1_col]
		v1_index = v1_col.index(i)
		if mode == 'r':
			out = u'''        <tr resource="InvlidateChange%i" rev="vo:invalidatedBy" typeof="vo:InvalidateChange">
          <td resource="Attribute%i" rev="vo:Undergoes" typeof="vo:Attribute">%i(%s)</td>
          <td about="Attribute%i" property="http://www.w3.org/2000/01/rdf-schema#label">%s</td>
          <span about="Version1" property="vo:hasAttribute" resource="Attribute%i"/>
        </tr>
'''%(v1_index, v1_index, v1_index, workbook_name.split('/')[-1], v1_index, i, v1_index)
		elif mode == 'j':
			out = u'''        <tr id="InvlidateChange%i" about="InvlidateChange%i">
          <td>%i(%s)</td>
          <td>%s</td>
          <script type="application/ld+json">
'''%(v1_index, v1_index, v1_index, workbook_name.split('/')[-1], i)
		elif mode == 't':
			out = u"%i(%s)\t%s\n"%(v1_index, workbook_name.split('/')[-1], i)
		elif mode == 'u':
			out = u"""<http://example.com/NG/Version1> vo:hasAttribute <http://example.com/NG/Version1/%s> .
<http://example.com/NG/Version1/%s> vo:undergoes <http://example.com/Changelog#InvalidateChange%s> .
<http://example.com/Changelog#InvalidateChange%s> a vo:InvalidateChange ;
	vo:invalidatedBy <http://example.com/NG/Version2> .

"""%(i, i, i, i)
		f_out.write(out.encode('utf8'))
		if mode == 'j':
			json1 = {
"@context":context,
"@type":"vo:Attribute" ,
"@id":"".join(["http://ngdb.com/v1/Attribute", str(i)]) ,
"label": str(i),
"undergoes":"".join([host, "InvalidateChange", str(i)]) ,
"@reverse" :    { "hasAttribute" : "Version1" }
}
			json2 = {
"@context":context,
"@type":"vo:InvalidateChange" ,
"@id": "".join([host, "InvalidateChange", str(i)]) ,
"invalidatedBy"  :   "Version2"
}
			json.dump([json1, json2], f_out, indent=4, sort_keys=True)
			f_out.write('''
          </script>
        </tr>
''')
	if mode == 'r' or mode == 'j':
		f_out.write('''      </table>

''')
	elif mode == 't' or mode == 'u':
		f_out.write("\n")


def write_added(v2, col, row, f_out, mode):
	if mode == 'r' or mode == 'j':
		f_out.write('''
      <h3>Columns added by %s</h3>
      <table about="Version1" rel="vo:absentFrom">
'''%(v2.split('/')[-1]))
	elif mode == 't':
		f_out.write("\nColumns added by %s\n\n"%(v2.split('/')[-1]))
	
	print "Added Column"
	for i in col:
		print i#, v2_value
		if mode == 'r':
			f_out.write('''        <tr about="AddChange%i" typeof="vo:AddChange">
          <td property="vo:resultsIn" resource="Attribute%i" typeof="vo:Attribute">%i</td>
          <td about="Attribute%i" property="http://www.w3.org/2000/01/rdf-schema#label"></td>
          <span about="Version2" property="vo:hasAttribute" resource="Attribute%i"/>
        </tr>
'''%(i, i, i, i, i))
		elif mode == 'j':
			f_out.write('''        <tr id="AddChange%i" about="v2:Attribute%i">
          <td>%i</td>
          <td></td>
          <script type="application/ld+json">
'''%(i, i, i))
			json1 = {
"@context":context,
"@type":"vo:AddChange" ,
"@id": "".join([host, "AddChange", str(i)]) ,
"resultsIn" :   "".join([ "http://ngdb.com/v2/Attribute", str(i)]),
"@reverse"  :   { "absentFrom": "Version1" }
}
			json2 = {
"@context":context,
"@type":"vo:Attribute" ,
"@id":"".join(["http://ngdb.com/v2/Attribute", str(i)]) ,
"label":"" ,
"@reverse" :    { "hasAttribute" : "Version2" }
}
			json.dump([json1, json2], f_out, indent=4, sort_keys=True)
			f_out.write('''
          </script>
        </tr>
''')
		elif mode == 't':
			f_out.write("%i\t\n"%(i))	
		elif mode == 'u':
			f_out.write("""<http://example.com/NG/Version1> vo:absentFrom <http://example.com/Changelog#AddChange%i> .
<http://example.com/Changelog#AddChange%i> a vo:AddChange ;
	vo:resultsIn <http://example.com/NG/Version2/Column%s> .
<http://example.com/NG/Version2> vo:hasAttribute <http://example.com/NG/Version2/Column%s> .

"""%(i, i, i, i))
	if mode == 'r' or mode == 'j':
		f_out.write('''      </table>
	      <h3>Rows added by %s</h3>
	      <table about="Version1" rel="vo:absentFrom">
'''%(v2.split('/')[-1]))
	elif mode == 't':
		f_out.write("\nRows added by %s\n\n"%(v2.split('/')[-1]))
	elif mode == 'u':
		f_out.write("\n")
	
	print "Added Row"
	for i, j in row:#i is the id, j is the file
	        if mode == 'r':	                #print i, v2_sheet.cell(i,0).value
			out = u'''        <tr about="AddChange%i" typeof="vo:AddChange">
          <td property="vo:resultsIn" resource="Attribute%i" typeof="vo:Attribute">%i</td>
          <td about="Attribute%i" property="http://www.w3.org/2000/01/rdf-schema#label">%s</td>
          <span about="Version2" property="vo:hasAttribute" resource="Attribute%i"/>
        </tr>
'''%(i, i, i, i, j, i)
		elif mode == 'j':
			out = u'''        <tr id="AddChange%i" about="v2:Attribute%i">
          <td>%i</td>
          <td property="http://www.w3.org/2000/01/rdf-schema#label">%s</td>
          <script type="application/ld+json">
'''%(i, i, i, j)
		elif mode == 't':
			out = u"%i\t%s\n"%(i, j)
		elif mode == 'u':
			out = u"""<http://example.com/NG/Version1> vo:absentFrom <http://example.com/Changelog#AddChange%i> .
<http://example.com/Changelog#AddChange%i> a vo:AddChange ;
	vo:resultsIn <http://example.com/NG/Version2/%s> .
<http://example.com/NG/Version2> vo:hasAttribute <http://example.com/NG/Version2/%s> .

"""%(i, i, i, i)
                f_out.write(out.encode('utf8'))
		if mode == 'j':
			json1 = {
"@context":context,
"@type":"vo:AddChange" ,
"@id": "".join([host, "AddChange", str(i)]) ,
"resultsIn" :   "".join([ "http://ngdb.com/v2/Attribute", str(i)]),
"@reverse"  :   { "absentFrom": "Version1" }
}
			json2 = {
"@context":context,
"@type":"vo:Attribute" ,
"@id":"".join(["http://ngdb.com/v2/Attribute", str(i)]) ,
"label": j ,
"@reverse" :    { "hasAttribute" : "Version2" }
}
			json.dump([json1, json2], f_out, indent=4, sort_keys=True)
			f_out.write('''
          </script>
        </tr>
''')

	if mode == 'r' or mode == 'j':
		f_out.write('''      </table>
''')
	elif mode == 't' or mode == 'u':
		f_out.write("\n")
	
def write_header(f_out, mode):
	if mode == 'j' or mode == 'r':
		f_out.write('''<html>
  <head>
  </head>
  <body vocab="http://www.w3.org/nw/prov#" prefix="vo: https://orion.tw.rpi.edu/~blee/VersionOntology.owl# v1: http://ngdb.com/v1/ v2: http://ngdb.com/v2/">
''')
	if mode == 'j':
		f_out.write('''  <script type="application/ld+json">
''')
		json1 = {
"@context":context,
"@type":"vo:Version",
"@id":"Version1",
"label":"ngdbv1"
}
		json2 = {
"@context":context,
"@type":"vo:Version",
"@id":"Version2",
"label":"DB_final-55-7262_2015_03_08.xlsx"
}
		json.dump([json1,json2], f_out, indent=4, sort_keys=True)
		f_out.write("\n  </script>\n")
	if mode == 'u':
		f_out.write("""@prefix vo: <http://orion.tw.rpi.edu/~blee/VersionOntology.owl#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<http://example.com/NG/Version1> a vo:Version ;
        skos:prefLabel "ngdbv1" .

<http://example.com/NG/Version2> a vo:Version ;
        skos:prefLabel "DB_final-55-7262_2015_03_08.xlsx" .

""")

def write_footer(f_out, mode):
	if mode == 'r':
		f_out.write('</body>\n</html>')

def get_indicator_map(excel_files):
	indicator_map = {}
	for excel_file in excel_files:
		print 'Importing: ' + excel_file
		file_workbook = xlrd.open_workbook(excel_file)
		file_sheet = file_workbook.sheet_by_index(0)
		indicators = file_sheet.col(0)
		for i in range(4, file_sheet.nrows):
			indicator_map[indicators[i].value] = excel_file
	return indicator_map

def compare(v1s, v2, fn_out, mode):
	indicator_map = get_indicator_map(v1s)
	i_keys = indicator_map.keys()
	v2_workbook = xlrd.open_workbook(v2)
	f_out = open(fn_out, 'w')

	v2_sheet = v2_workbook.sheet_by_index(0)
	v2_keys = [i.value for i in v2_sheet.col(0)]

	converted = [index_convert(i) for i in range(0,54)]
	new_col = [i for i in range(0, v2_sheet.ncols) if index_convert(i) == -1]
	new_row = [(i, v2_sheet.cell(i,0).value) for i in range(3, v2_sheet.nrows) if v2_sheet.cell(i,0).value not in i_keys]
	old_col = [i for i in range(0,194) if i not in converted]
	old_row = [(i, indicator_map.get(i, None)) for i in i_keys if i not in v2_keys]

	write_header(f_out, mode)
	write_added(v2, new_col, new_row, f_out, mode)
	write_removed(v2, old_col, old_row, f_out, mode)

	if mode == 'r' or mode == 'j':
		f_out.write('''
      <h3>Change Log</h3>
''')
	elif mode == 't':
		f_out.write("Change Log\n")

	workbook_name = ''
	for i in range(3,v2_sheet.nrows):
		v2_row = v2_sheet.row(i)
		#workbook_name = v1_file
		if v2_row[0].value in [j for i, j in new_row] or v2_row[0].value in [i for i, j in old_row]:
			continue
		if workbook_name == indicator_map.get(v2_row[0].value, None):
			pass
		else:
			workbook_name = indicator_map.get(v2_row[0].value, None)
			v1_workbook = xlrd.open_workbook(workbook_name)
			v1_sheet = v1_workbook.sheet_by_index(0)
			v1_col = v1_sheet.col(0)
			v1_col = [j.value for j in v1_col]
		#print v2_row[0].value
		v1_index = v1_col.index(v2_row[0].value)
		v1_row = v1_sheet.row(v1_index)
		write_modify(v1_row, v2_row, workbook_name, f_out, mode)
	
	write_footer(f_out, mode)
	f_out.close()

if __name__ == "__main__":
	if '-json' in sys.argv:
		mode = 'j'
		out_name = 'changelog_json.html'
	elif '-rdfa' in sys.argv:
		mode = 'r'
		out_name = 'changelog_test.html'
	elif '-txt' in sys.argv:
		mode = 't'
		out_name = 'changelog.txt'
	elif '-ttl' in sys.argv:
		mode = 'u'
		out_name = 'changelog.ttl'

	v2_dir = join(separator, 'data', 'NGdata', 'v2')
	v1_dir = join(separator, 'data', 'NGdata', 'v1')
	
	excel_files = glob.glob(join(v1_dir, '*.xlsx'))
	
	v1_file = join(v1_dir, 'America_906.xlsx')
	v2_file = join(v2_dir, 'DB_final-55-7262_2015_03_08.xlsx')

	compare(excel_files, v2_file, out_name, mode)
