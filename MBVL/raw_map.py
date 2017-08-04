
class entry:
	query = None
	dist = None
	freq = None
	tax = None
	poss = None

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
	if f_name == 'silva_spingo':
		for line in f:
			x = line.split('\t')
			entry_id = x[0].split('|')[0]
			results[entry_id] = entry()
			results[entry_id].query = x[0]
			results[entry_id].freq = int(results[entry_id].query.split('|')[-1].split(':')[1])
			total += results[entry_id].freq
			results[entry_id].dist = float(x[1])
			results[entry_id].tax = x[2:]
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
					found[species.replace('_', ' ')] += 1
			
	elif f_name == 'silva_gast':
		pass
	elif f_name == 'rdp_spingo':
		pass
	elif f_name == 'rpd_gast':
		pass

	print total
	for k in sorted(mock):
		print k, " :\t", found[k]
	

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

if __name__ == "__main__":
	fList = ['silva_spingo', 'silva_gast', 'rdp_spingo', 'rdp_gast']
	file_parse(fList[0])
	
