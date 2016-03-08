import sys, os, codecs, re, logging, csv
from collections import defaultdict, OrderedDict
from pprint import pprint
import rules
import rules

# XXX Move this to a config file or something similar.
INDIR = '/Users/rweiss/Documents/Stanford/ancestry/CaliforniaGreatRegister/cleaned'
OUTDIR = '/Users/rweiss/Box Sync/CaliforniaGreatRegisters/staging_data'

class Page(dict):

	def __init__(self, rawtext, logger=None):
		self.logger = logger or logging.getLogger(__name__)
		self._id = None
		self._rollnum = None
		self._precinct = ""
		self._precinctno = ""
		self._text = None
		self._numlines = 0
		self._rawtext = rawtext # XXX Consider collapsing into "text"
		self._numrows = 0
		self._errors = defaultdict(int)

		try:
			self._parsed = self.parse_file()	
		except ValueError as e:
			self.logger.debug(e)
		except IndexError as e:
			self.logger.debug(e)

	def __str__(self):
		return self._rawtext

	@property
	def id(self):
	    return self._id

	@property
	def rollnum(self):
	    return self._rollnum

	@property
	def precinct(self):
	    return self._precinct

	@property
	def precinctno(self):
	    return self._precinctno
	
	@property
	def rawtext(self):
	    return self._rawtext

	@property
	def text(self):
	    return self._text

	'''Checks to see if the line from rawtext has ancestry header data.'''
	def has_valid_data(self):
		if self._parsed:
			return True
		else:
			return False

	'''Reads the header for each page and sets page attributes accordingly.'''
	def parse_file(self):
		lines = self.rawtext.split(u'|')
		match = re.match(r'(\w+(?:county))_(\d+)-(\d+)',lines[0])
		if not match:
			match = re.match(r'(\w+(?:county))(?:_\d+)?_(\d+)-(\d+)',lines[0])
		if match:
			county = match.group(1).split('county')[0]					
			self._id = match.group(3)
			self._rollnum = match.group(2)
			self._text = ''.join(lines[4:])
			if int(self._rollnum) > 14 and county == 'sanbernardino':
				return False
			return True
		else:
			return False

class ExtractionTask(object):

	def __init__(self, county=None, logger=None):
		self.logger = logger or logging.getLogger(__name__)
		self._county_file = None
		self._county = county
		self._errors = defaultdict(int)
		self._ratios = []
		self._failed_pages = []
		self._text = None
		self._total_pages = 0
		self._page_path = os.path.join(INDIR, county + '.txt')		
		self._ppr = defaultdict(int)
		self._extracted_pages = []
		self._roll_counts  = {'total': defaultdict(int),'failed': defaultdict(int)}
		self.logger.info('creating {county} extractor'.format(county=county))

	@property
	def county(self):
	    return self._county

	@property
	def text(self):
	    return self._text
	
	
	'''
	Opens the appropriate county file, stores the lines in the instantiated ExtractionTask object, and counts the number of lines found in the file.
	'''
	def load_data(self):
		with codecs.open(self._page_path, 'r', 'utf8') as infile:
			self._county_file = infile.readlines()

		self._total_pages = len(self._county_file)
		self.logger.info('loaded {num} pages for {county}'.format(
			county=self._county, num=self._total_pages))

	'''Opens success file and writes results to county-specific files'''
	def write_successes(self):
		ordered_fieldnames = ['county','rollnum','pagenum','name','address','occupation','precinct','precinctno', 'pid']
		filepath = os.path.join(OUTDIR, '{county}_successes.txt'.format(
			county=self.county))
		first_entry = os.path.exists(filepath)

		with codecs.open(filepath, 'a', 'utf8') as outfile:
			writer = csv.DictWriter(outfile, fieldnames=ordered_fieldnames)
			if not first_entry:
				writer.writeheader()
			for page in self._extracted_pages:
				for row in page['rows']:
					if row:
						writer.writerow(row)
					else:
						# XXX log error, get index too
						continue

#						outfile.write("{id},{rollnum},{row}\n".format(id=page.id, rollnum=page.rollnum, row=row))
						#self.logger.debug('line length is {x} n-grams'.format(x=len(row.split(' '))))
	
	'''Opens stats file and writes results for each county's extraction performance'''
	def write_stats(self):
		ordered_fieldnames = sorted(OrderedDict(self._stats))
		filepath = os.path.join(OUTDIR, 'county_stats.txt'.format(
			county=self.county))
		first_entry = os.path.exists(filepath)
		with codecs.open(filepath, 'a', 'utf8') as outfile:
			writer = csv.DictWriter(outfile, fieldnames=ordered_fieldnames)
			if not first_entry:
				writer.writeheader()
			writer.writerow(self._stats)

	'''Opens failures file and writes results for each county's failed pages'''
	def write_failed_pages(self):
		filepath = os.path.join(OUTDIR, '{county}_failures.txt'.format(
			county=self.county))
	
		if len(self._failed_pages) > 0:
			self.logger.info('writing {county} failures to file'.format(county=self.county))
			with codecs.open(filepath, 'a', 'utf8') as outfile:
				for line in self._failed_pages:
					outfile.write("%s\n" % line)

	'''Creates all output files, happens at the end of a county parse task.'''
	def write_summary(self):
		self.write_successes()
		self.write_failed_pages()
		self.write_stats()

	'''Computes a few task and average page statistics for each county.'''
	def collect_county_stats(self):
		self.collect_roll_stats()
		if self._failed_pages:
			num_failed_pages = len([page for page in self._failed_pages])
		else:
			num_failed_pages = 0
		num_successes = float(self._total_pages - num_failed_pages)
		extraction_ratios = self._ratios
		num_rows = [int(el[2]) for el in extraction_ratios if el[2] > 0]
		ratios = [int(el[3])/float(el[2]+1) for el in extraction_ratios]
		avg_rows = sum(num_rows) / num_successes		
		avg_ratios = sum(ratios) / len(ratios)
		avg_ppr = sum(dict(self._ppr).values())/len(dict(self._ppr).keys())
		self._stats = dict(self._errors)
		self._stats.update(
			{'avg_rows': str.format('{0:.2f}', avg_rows),
			'avg_ratios': str.format('{0:.2f}', avg_ratios),
			'avg_ppr': str.format('{0:.2f}', avg_ppr),
			'pages_failed': int(num_failed_pages),
			'county': self._county,
			'total_pages': int(self._total_pages)})		

	'''Computes a few task and average page statistics for each county.'''
	def collect_roll_stats(self):
		filepath = os.path.join(OUTDIR, 'roll_stats.txt'.format(
			county=self.county))

		counts = defaultdict(dict)
		for el in self._roll_counts.keys():
			for k, v in self._roll_counts[el].items():
				counts[k][el] = v

		counts = dict(counts)

		first_entry = os.path.exists(filepath)
		with codecs.open(filepath, 'a', 'utf8') as outfile:
			if not first_entry:
				outfile.write('county,rollnum,totalpages,failedpages\n')
			for k, v in counts.items():
				if 'failed' not in v.keys():
					v['failed'] = 0
				outfile.write('{c},{r},{t},{f}\n'.format(
					c=self.county,r=k,t=v['total'],f=v['failed']))
			
	def extract_rows(self, page):
		page.update(rules.extract_newlines(page=page, task=self))
		page.update(rules.extract_precinct(page=page, task=self))
		page = rules.postprocess_rows(self, page)

		if page['rows']:			
			self.logger.debug('{county},{id},{rollnum},{num}'.format(
				county=self._county, num=len(page['rows']), id=page.id, rollnum=page.rollnum))
 		else:
 			page._errors['no_rows_found'] += 1
 			return False

 		return True	

	def extract_columns(self, page):
 		results = []

	 	for row in page['rows']:
	 		result = rules.extract_address(row, self, page)
			result = rules.extract_name(result, self, page)
			result = rules.postprocess_columns(result, page, self)
			results.append(result)
		
		if len(results) > 1:
			page['rows'] = results
		else:
 			page._errors['no_columns_found'] += 1
 			self._failed_pages.append(page)
 			return False

 		return page

	'''
	Kicks off the extraction task.  Tries to convert each line to a Page object.  
	If successful, tries to extract the rows from the page.  Then for each 
	successful row found, tries to extract columns from each row found.
	'''
	def start(self):
		self.load_data()
		self.logger.info('starting {county} extraction'.format(county=self.county))
		current_roll = 0
		counts = defaultdict(int)
		
		for line in self._county_file:
			page = Page(line)
			next_roll = page.rollnum
			self._roll_counts['total'][next_roll] += 1
			if next_roll != current_roll:
				current_roll = next_roll				
				self.logger.info('starting roll number {rollnum}'.format(rollnum=current_roll))
		
			if page.has_valid_data():				
				page_has_rows = self.extract_rows(page=page)
				if page_has_rows:		
					formatted_page = self.extract_columns(page)					
					if formatted_page:
						self._ppr[formatted_page.rollnum] += 1
						self._ratios.append((formatted_page.id, formatted_page.rollnum, len(formatted_page['rows']), len(formatted_page.text)))
						self._extracted_pages.append(formatted_page)
				else:
					self.logger.debug('{county},{x},{y}'.format(county=self.county, x=page.id, y=page.rollnum))
					self._failed_pages.append(page)
					self._ppr[page.rollnum] += 1
					self._ratios.append((page.id, page.rollnum, 1, 1))

					self._roll_counts['failed'][page.rollnum] +=1 
					counts[page.rollnum] += 1
					continue
			#break
		self._roll_counts['failed'] = counts
		#pprint(dict(counts))

		self.logger.info('{county} extraction complete, {x} page(s) failed to parse'.format(county=self.county, x=len([page for page in self._failed_pages ])))
#		self.logger.info('{county} extraction complete, {x} page(s) failed to parse, {y} pages had parsing errors'.format(county=self.county, x=len(self._failed_pages, y=))) XXX needs number of pages that had a bad row
		self.collect_county_stats()
		self.write_summary()

def run(counties):
	logger = logging.getLogger(__name__)

	for county in counties:
		task = ExtractionTask(county=county)		
		logger.info("starting processing job for {county}".format(county=county))
		task.start()