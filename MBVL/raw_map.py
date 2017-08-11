
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
		found[i] = 0
	results = {}
	total = 0
	if f_name.split('_')[1] == 'spingo':
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

			species = results[entry_id].tax[-2]
			genus = results[entry_id].tax[-4]
			if species != 'AMBIGUOUS':
				if species.replace('_', ' ') in mock:
					#print species
					found[species.replace('_', ' ')] += results[entry_id].freq
			
	elif f_name.split('_')[1] == 'gast':
		skip = False
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

			if len(results[entry_id].tax) >= 7:
				name = ' '.join(results[entry_id].tax[5:7])
				if name in mock:
					found[name] += results[entry_id].freq

	#print "Total: ", total
	#coverage = sum([found[i] for i in found.keys()])
	#print "Coverage: ", coverage, "(",float(coverage)/total*100, "%)"
	#for k in sorted(mock):
	#	print k, " :\t", found[k]
	
	return results

def get_output(tax1, alg1, tax2, alg2):
	if alg1 != alg2:
		for j in range(7):
			if j > 4:
				ss_tax_index = (2*j)+2
			else:
				ss_tax_index = 2*j

			if j >= len(sg[i].tax):
				if tax1[ss_tax_index] != 'AMBIGUOUS':
					return "\t".join([ '---', rank[j], str([x for x in tax1[ss_tax_index:] if not is_number(x)])])
			elif j == 6:
				if tax1[ss_tax_index] == 'AMBIGUOUS':
					return "\t".join(['+++', rank[j], str(tax2[j:])])
				elif ss[i].tax[ss_tax_index] != '_'.join(tax2[5:7]):
					return "\t".join([ '>>>', rank[j], tax1[ss_tax_index], str(tax2[5:])])
			elif tax1[ss_tax_index] == 'AMBIGUOUS':
				return "\t".join([ '+++', rank[j], str(tax2[j:])])
			elif tax1[ss_tax_index] != tax2[j]:
				return "\t".join([ '>>>', rank[j], str(tax1[ss_tax_index]), str(tax2[j:])])
		return None

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

rank = ['Kingdom', 'Phylum', 'Class', 'Order', 'Family', 'Genus', 'Species']

if __name__ == "__main__":
	fList = ['silva_spingo', 'silva_gast', 'rdp_spingo', 'rdp_gast']
	ss = file_parse(fList[0])
	sg = file_parse(fList[1])

	out = file('silva_spingo_gast.txt', 'w')
	for i in sorted(ss.keys()):
		x = get_output(ss[i].tax, 'spingo', sg[i].tax, 'gast')
		if not x == None:
			out.write("\t".join([i,x])+"\n")
	out.close()
