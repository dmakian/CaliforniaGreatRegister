import re, logging, pprint

logger = logging.getLogger(__name__)

REGEXES = {
	'alameda': {
		'delims': [r'D?\s*e\s*m(?:o?c?r?a?t?)?', r'R?\s*e\s*p(?:\s*ubl?\s*i?[c|o]?\s*a?\s*n?)?', r'Dec(?:line(?:s)?)? [T|t]o [S|s]tate', 'Socialist', 'Progressive'],
		#'name_re': re.compile('([A-Z][a-z]*)((?:\s+M[rs|iss]\s+)?(?:[A-Z][a-z]+)(?:\s+[A-Z]\s+)+)'),#\s+((?:Mr?s?)?(?:\w+))'),#, re.IGNORECASE),
		'name_re': re.compile('([A-Z][a-z]+\s)((?:[M?\s*i\s*s\s*s|M?\s*r\s*s]\s)*(?:(?:[A-Z][a-z]*\s){1}(?:[A-Z][a-z]*?\s){1}))'),
		'street_re': re.compile(r'(l[a|i]ne|circle|court|ct|resv|st|at|ave|camp|drive|dr|blvd|boulevard|road|rd|place|terrace|way|highway)', re.IGNORECASE),
		'city_address_re': re.compile('((?:(?:\d+)(?:.+)|[A-Z][a-z]+\s)(?:l[a|i]ne|circle|court|ct|resv|st|at|ave|camp|drive|dr|blvd|boulevard|road|rd|place|terrace|way|highway)(?:(?:.+)(?:box\s\d+))?)', re.IGNORECASE),
		'rural_address_re': re.compile(r'((?:\b[P|p]\s*[O|o])\s*(?:[R|r][F|f][D|d])?\s+(?:[N|n]o\s+\d+)\s+[B|b]o?x\s\d+)\s'),
		'precinct1_re': re.compile('(\w+)(?:(?:\w+|\s+|\d+)P\s*R\s*E\s*C\s*I\s*N\s*C\s*T\s*)(?:-)?(?:\w+(?:\s+)(\d+))?', re.IGNORECASE),
		'precinct2_re': re.compile('(?:REGISTRATION)\s+(?:P\s*R\s*E\s*C\s*I\s*N\s*C\s*T*\s*)*([A-Z]+\s)+(?:[N|n][oO|]\s)(\d+)')
	},
	'sanbernardino': {
		'delims': [r'D?\s*e\s*m(?:o?c?r?a?t?)?', r'R?\s*e\s*p(?:\s*ubl?\s*i?[c|o]?\s*a?\s*n?)?', r'Dec(?:line(?:s)?)? [T|t]o [S|s]tate', 'Socialist', 'Progressive'],
		'name_re': re.compile('([A-Z][a-z]+\s)((?:[M\s*i\s*s\s*s|M\s*r\s*s]\s)*(?:(?:[A-Z][a-z]*\s){1}(?:[A-Z][a-z]*?\s){1}))'),
		'street_re': re.compile(r'(line|livery|drive|court|ct|resv|street|st|at|avenue|ve|camp|dr|blvd|boulevard|road|rd|place|terrace|way|highway)', re.IGNORECASE),
		#'city_address_re': re.compile(r'((?:\d+\s)|\s(?:W|E|N|S)\s(?:\w+\s)*(?:court|ct|street|st|at|avenue|ave|camp|blvd|boulevard|road|rd|place|pl|terrace|highway|way)\s,)', re.IGNORECASE),
		'city_address_re': re.compile('((?:(?:\d+)(?:.+)|[A-Z][a-z]+\s)(?:l[a|i]ne|circle|court|ct|resv|rfd|st|at|ave|camp|drive|dr|blvd|boulevard|road|rd|place|terrace|way|highway)(?:(?:.+)(?:box\s\d+))?)', re.IGNORECASE),
		'rural_address_re': re.compile(r'((?:\b[P|p]\s*[O|o])\s*(?:[R|r][F|f][D|d])?\s+(?:[N|n]o\s+\d+)\s+[B|b]ox\s\d+)\s'),
		'precinct1_re': re.compile('(\w+\s)+(?:P\s*R\s*E\s*C\s*I\s*N\s*C\s*T)(?:(?:\sNO\s)*(\d+))*'),
		'precinct2_re': re.compile('(\w+\s)+(?:P\s*R\s*E\s*C\s*I\s*N\s*C\s*T)(?:(?:\sNO\s)*(\d+))*')
	}
}

# XXX Eventually add rules here for each county
REJECT_RULES = {
	'end_of_page': True, # skip the row if it's empty
	'too_many_addresses': True, # throw away rows with >1 address
	'skipped_header': True, # throw away rows with header information
	'name_failed': False, # throw away row if name not found
	'address_failed': False # throw away row if address not found
}

'''
This function establishes the rules for throwing out pages based on bad rows.
These are conditional on county-level rules.
'''
def postprocess_rows(task, page):
	# XXX Need to stash bad rows somewhere so we can inspect
	precinct1_re = REGEXES[task.county]['precinct1_re']
	precinct2_re = REGEXES[task.county]['precinct2_re']
	street_re = REGEXES[task.county]['street_re']
	results = []

	for row in page['rows']: 
		if row.endswith('\r'): 
			continue # get rid of rows that only have end of page characters
		elif row.startswith(r'\d+'):
			row = re.sub(r'^(\d+\s)', '', row) # remove leading digits (row numbers)
		elif len(row) < 1: # row is empty
			if REJECT_RULES['end_of_page']:
		 		continue 

	 	addresses = re.findall(street_re, row)
	 	if len(addresses) > 1:
	 		e = 'too_many_addresses'
	 		task._errors[e] += 1
	 		page._errors[e] += 1
	 		if REJECT_RULES[e]:
	 			continue 

	 	header = re.search(precinct1_re, row)
	 	if not header:
	 		header = re.search(precinct2_re, row)
	 	if header: 
	 		e = 'skipped_header'
	 		task._errors[e] += 1
	 		page._errors[e] += 1
	 		if REJECT_RULES[e]:	 			
	 			continue 

	 	results.append(row)
	
	if len(results) > 3: #chosen arbitrarily
		page['rows'] = results
	else:
		page['rows'] = []

	return page

'''
This function establishes the rules for throwing away rows based on bad columns.
These are conditional on county-level rules.
'''
def postprocess_columns(row, page, task):
	comma2_re = r'(\,(\s*[A-Z]?\s*\,))'	
	comma2 = re.search(comma2_re, row)
	if comma2:
		row = re.sub(comma2.group(1), ' ' + comma2.group(2), row)

	#cols = row.split(",")
	#if 2 < len(cols) > 2 or cols[0] == '':
	#	task._errors['malformed'] += 1
	#	continue		

	row = row + "," + str(page._precinct) + "," + str(page._precinctno)	
	row = ','.join([el.strip() for el in row.split(",")])
	return row

'''
This function inserts newline characters according to the delimiter regex.
These are conditional on county-level rules. This function also replaces some
common mistakes with corrections.
'''
def extract_newlines(page, task):
	delims = REGEXES[task.county]['delims']
	pagetext = re.sub(r'-', ' ', page.text)
	pagetext = re.sub(r'R\s*F\s*D', 'RFD', pagetext)
	#pagetext = re.sub(r'D?\s*e\s*m(?:o?c?r?a?t?)?', 'Dem', pagetext) # XXX move to preprocess page function?
	#pagetext = re.sub(r'R?\s*e\s*p(?:\s*ubl?\s*i?[c|o]?\s*a?\s*n?)?', 'Rep', pagetext)
	#pagetext = re.sub(r'Dec(?:line(?:s)?)? [T|t]o [S|s]tate', 'Declines', pagetext)

	for delim in delims:
		pagetext = re.sub(delim, "," + delim.strip()+'\n', pagetext)

	page['rows'] = pagetext.split("\n")
	return page

'''
This function finds precinct and precinct numbers and sets the page attribute 
for precinct and precicnt number accordingly.
'''
def extract_precinct(page, task):
	precinct1_re = REGEXES[task.county]['precinct1_re']	
	precinct2_re = REGEXES[task.county]['precinct2_re']	
	pagetext = page.text
	
	precinct = re.search(precinct1_re, pagetext) # XXX append precinct name to each row
	if precinct and 'REGISTRATION' in set(precinct.groups()):
		precinct = re.search(precinct2_re, pagetext) # XXX append precinct name to each row
	if precinct:
		page._precinct = precinct.group(1)
		page._precinctno = precinct.group(2)
	else:
		page._precinct = None
		page._precinctno = None

	return page

'''
Uses county-specific regex to detect full addresses.  Will skip row if the rule
is set to True.
'''
def extract_address(row, task, page):
	city_address_re = REGEXES[task.county]['city_address_re']
	rural_address_re = REGEXES[task.county]['rural_address_re']
	address_found = re.search(city_address_re, row)
	if address_found:
		row = re.sub(address_found.group(1), "," + address_found.group(1).strip() + ",", row)		
	elif address_found and len(address_found.groups()) < 5: # Hack
		address_found = re.search(rural_address_re, row)
		if address_found:
			row = re.sub(address_found.group(1), "," + address_found.group(1).strip() + ",", row)		
	if not address_found:		
		e = 'address_failed'
		page._errors[e] += 1
		task._errors[e] += 1
		
		if REJECT_RULES['address_failed']:
			return None

	return row

'''
Uses county-specific regex to detect full names.Will skip row if the rule
is set to True.
'''
def extract_name(row, task, page):
	name_re = REGEXES[task.county]['name_re']
	name_found = re.search(name_re, row)
	if name_found:
		row = re.sub(name_found.group(0), ','.join(name_found.groups()) + ',', row)
	if not name_found:
		e = 'name_failed'
		task._errors[e] += 1
		page._errors[e] += 1

		if REJECT_RULES['name_failed']:
			return None

	return row