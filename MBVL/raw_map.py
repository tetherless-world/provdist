import urllib

class entry:
	query = None
	dist = None
	freq = None
	tax = None
	poss = None

	def __lt__(self, other):
		if self.query == other.query:
			return self.freq < other.freq
		else:
			return self.query < other.query

def is_number(s):
	try:
		float(s)
		return True
	except ValueError:
		return False

def file_parse(f_name):
	f = open(f_name, 'r')
	found = {}
	for i in mock:
		found[i] = [[],[],0]
	ambiguous = []
	fp = []
	fn_count = 0
	fn = []
	results = {}
	total = 0
	if f_name.split('_')[1] == 'spingo':
		if f_name == "silva_spingo":
			family[4] = 'Clostridiaceae_1'
		else:
			family[2] = 'Bacillaceae 1'
			family[4] = 'Clostridiaceae 1'
		for line in f:
			x = line.split('\t')
			entry_id = x[0].split('|')[0]
			results[entry_id] = entry()
			results[entry_id].query = x[0]
			results[entry_id].freq = int(results[entry_id].query.split('|')[-1].split(':')[1])
			results[entry_id].dist = float(x[1])
			results[entry_id].tax = x[2:]

			total += results[entry_id].freq

			if not is_number(results[entry_id].tax[-1]):
				results[entry_id].poss = results[entry_id].tax[-1].split(',')
				results[entry_id].tax = results[entry_id].tax[:-1]
				if results[entry_id].tax[-2] != 'AMBIGUOUS':
					print results[entry_id].tax[-2]

			clean_tax = [x for x in results[entry_id].tax if not is_number(x)]
			if len(clean_tax) < 7:
				clean_tax[0:0] = ['Pass', 'Pass', 'Pass', 'Pass']
			del clean_tax[5]
			results[entry_id].tax = clean_tax

			if clean_tax[4] == 'AMBIGUOUS':
				fn_count += 1
				ambiguous.append(entry_id)
			elif not clean_tax[4] in family:
				fp.append((entry_id, 'family'))
			elif clean_tax[5] == 'AMBIGUOUS':
				for i in range(len(family)):
					if clean_tax[4] == family[i]:
						found[mock[i]][0].append(entry_id)
			elif not clean_tax[5] in genus:
				fp.append((entry_id, 'genus'))
			elif clean_tax[6] == 'AMBIGUOUS':
				for i in range(len(genus)):
					if clean_tax[5] == genus[i]:
						found[mock[i]][1].append(entry_id)
			elif not ' '.join(clean_tax[6].split('_')) in mock:
				fp.append((entry_id, 'species'))
			else:
				found[' '.join(clean_tax[6].split('_'))][2] += 1

	elif f_name.split('_')[1] == 'gast':
		skip = False
		if f_name == "rdp_gast":
			family[2] = 'Bacillaceae 1'
			family[4] = 'Clostridiaceae 1'
		for line in f:
			if not skip:
				skip = True
				continue
			x = line.split('\t')
			entry_id = x[0].split('|')[0]
			results[entry_id] = entry()
			results[entry_id].query = x[0]
			results[entry_id].freq = int(results[entry_id].query.split('|')[-1].split(':')[1])
			results[entry_id].dist = float(x[2])
			results[entry_id].tax = x[1].split(';')

			total += results[entry_id].freq
			temp_tax = results[entry_id].tax

			if len(temp_tax) < 5:
				fn_count += 1
				ambiguous.append(entry_id)
			elif not temp_tax[4] in family:
				fp.append((entry_id, 'family'))
			elif len(temp_tax) < 6:
				for i in range(len(family)):
					if temp_tax[4] == family[i]:
						found[mock[i]][0].append(entry_id)
			elif not temp_tax[5] in genus:
				fp.append((entry_id, 'genus'))
			elif len(temp_tax) < 7:
				for i in range(len(genus)):
					if temp_tax[5] == genus[i]:
						found[mock[i]][1].append(entry_id)
			elif not ' '.join(results[entry_id].tax[5:7]) in mock:
				fp.append((entry_id, 'species'))
			else:
				found[' '.join(results[entry_id].tax[5:7])][2] += 1

	fp_file = open("fp_"+f_name+".txt", 'w')
	for fid, frank in fp:
		fp_file.write("\t".join([fid, str(results[fid].freq), frank, str(results[fid].tax)])+"\n")
	fp_file.close()

	for i in found.keys():
		if sum([len(found[i][0]), len(found[i][1]), found[i][2]]) == 0:
			fn.append(i)
	print fn
	ttl_output(f_name, fp, fn, found, results)
	total = len(results.keys())
	print "\t".join(["False Positives:", str(len(fp))])
	print "\t".join(["Ambiguous:", str(len(ambiguous))])
	print "\t".join(["Total:", str(len(results.keys()))])
	coverage = sum([len(found[i][0])+len(found[i][1])+found[i][2] for i in found.keys()])
	print "\t".join(["Coverage:", str(coverage)])
	print "\t".join(["Percentage:", str(float(coverage)/total*100)])
	for k in sorted(mock):
		print "\t".join([k+":", str(len(found[k][0])), str(len(found[k][1])), str(found[k][2])])
	
	return results

def ttl_output(f_name, false_positive, false_negative, found, results):
	fp_file = open("fp_"+f_name+".ttl", 'w')
	fp_file.write("""@prefix vo: <http://orion.tw.rpi.edu/~blee/VersionOntology.owl#> .
@prefix mbvl: <http://example.com/MBVL/> .
@prefix next: <http://example.com/MBVL/%s> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<http://example.com/MBVL/db> a vo:Version .
<http://example.com/MBVL/%s> a vo:Version .\n"""%(f_name, f_name))
	for i in range(len(false_positive)):
		fid, j = false_positive[i]
		clean_fid = urllib.quote(fid.split()[0])
		if results[fid].freq > 10:
			fp_file.write("""mbvl:db vo:absentFrom mbvl:AddChange%i .
next:%s a vo:Attribute .
mbvl:%s vo:hasAttribute next:%s .
mbvl:AddChange%i a vo:AddChange ;
	vo:resultsIn next:%s .\n
"""%(i, clean_fid, f_name, clean_fid, i, clean_fid))
	fp_file.close()

def get_output(tax1, alg1, tax2, alg2):
	if alg1 == 'silva_spingo':
		t1 = [x for x in tax1 if not is_number(x)]
		del t1[5]
	elif alg1 == 'rdp_spingo':
		t1 = [x for x in tax1 if not is_number(x)]
		print t1
		del t1[1]
		t1[0:0] = ['Pass', 'Pass', 'Pass', 'Pass']
	else:
		t1 = tax1

	if alg2 == 'silva_spingo':
		t2 = [x for x in tax2 if not is_number(x)]
		del t2[5]
	elif alg2 == 'rdp_spingo':
		t2 = [x for x in tax2 if not is_number(x)]
		del t2[1]
		t2[0:0] = ['Pass', 'Pass', 'Pass', 'Pass']
	else:
		t2 = tax2

	if alg1.split('_')[1] != alg2.split('_')[1]:
		for j in range(7):
			if t1[j] == 'Pass':
				continue
			if j >= len(t2):
				if t1[j] != 'AMBIGUOUS':
					return "\t".join([ '---', rank[j], str(t1[j:])])
			elif j == 6:
				if t1[j] == 'AMBIGUOUS':
					return "\t".join(['+++', rank[j], str(t2[j:])])
				elif t1[j] != '_'.join(t2[5:7]):
					return "\t".join([ '>>>', rank[j], t1[j], str(tax2[5:])])
			elif t1[j] == 'AMBIGUOUS':
				return "\t".join([ '+++', rank[j], str(t2[j:])])
			elif t1[j] != t2[j]:
				return "\t".join([ '>>>', rank[j], str(t1[j]), str(t2[j:])])
		return None
	elif alg1.split('_')[1] == 'spingo':
		for j in range(7):
			if t1[j] == 'Pass' or t2[j] == 'Pass':
				continue
			if t1[j] == 'AMBIGUOUS':
				if t2[j] == 'AMBIGUOUS':
					return None
				else:
					return "\t".join(['+++', rank[j], str(t2[j:])])
			elif t2[j] == 'AMBIGUOUS':
				return "\t".join(['---', rank[j], str(t1[j:])])
			elif t1[j] != t2[j]:
				return "\t".join(['>>>', rank[j], str(t1[j]), str(t2[j])])
		return None
	elif alg1.split('_')[1] == 'gast':
		if len(t1) > len(t2):
			return "\t".join(['---', rank[len(t2)], str(t1[len(t2):])])
		elif len(t1) < len(t2):
			return "\t".join(['+++', rank[len(t1)], str(t2[len(t1):])])
		else:
			for j in range(len(t1)):
				if t1[j] != t2[j]:
					return "\t".join(['>>>', rank[j], str(t1[j]), str(t2[j])])
		return None
	else:
		return -1

mock = ['Acinetobacter baumannii',
	'Actinomyces odontolyticus',
	'Bacillus cereus',
	'Bacteroides vulgatus',
	'Clostridium beijerinckii',
	'Deinococcus radiodurans',
	'Enterococcus faecalis',
	'Escherichia coli',
	'Helicobacter pylori',
	'Lactobacillus gasseri',
	'Listeria monocytogenes',
	'Neisseria meningitidis',
	'Porphyromonas gingivalis',
	'Propionibacterium acnes',
	'Pseudomonas aeruginosa',
	'Rhodobacter sphaeroides',
	'Staphylococcus aureus',
	'Staphylococcus epidermidis',
	'Streptococcus agalactiae',
	'Streptococcus mutans',
	'Streptococcus pneumoniae']

genus = [x.split()[0] for x in mock]

family = ['Moraxellaceae',
	  'Actinomycetaceae',
	  'Bacillaceae',
	  'Bacteroidaceae',
	  'Clostridiaceae',
	  'Deinococcaceae',
	  'Enterococcaceae',
	  'Enterobacteriaceae',
	  'Helicobacteraceae',
	  'Lactobacillaceae',
	  'Listeriaceae',
	  'Neisseriaceae',
	  'Porphyromonadaceae',
	  'Propionibacteriaceae',
	  'Pseudomonadaceae',
	  'Rhodobacteraceae',
	  'Staphylococcaceae',
	  'Staphylococcaceae',
	  'Streptococcaceae',
	  'Streptococcaceae',
	  'Streptococcaceae']

rank = ['Kingdom', 'Phylum', 'Class', 'Order', 'Family', 'Genus', 'Species', 'Strain']

if __name__ == "__main__":
	fList = ['silva_spingo', 'silva_gast', 'rdp_spingo', 'rdp_gast']
	#f1_name = fList[1]
	#f2_name = fList[3]
	#f1 = file_parse(f1_name)
	#f2 = file_parse(f2_name)

	for i in fList:
		f1 = file_parse(i)
	#out = file('silva_rdp_gast.txt', 'w')
	#for i in sorted(f1.keys()):
	#	x = get_output(f1[i].tax, f1_name, f2[i].tax, f2_name)
	#	if not x == None:
	#		out.write("\t".join([i,x])+"\n")
	#out.close()
