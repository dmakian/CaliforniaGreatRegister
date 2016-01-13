import sys, os, codecs, re, logging
from collections import defaultdict
from pprint import pprint

#OUTDIR = '/home/rjweiss/shared/CaliforniaGreatRegister/cleaned' # XXX Move this to logging.yaml
OUTDIR = '/Users/rweiss/Documents/Stanford/ancestry/CaliforniaGreatRegister/cleaned'

class Page(object):

	def __init__(self, rawtext, logger=None):
		self.logger = logger or logging.getLogger(__name__)
		self._id = None
		self._rollnum = None
		self._date = None
		self._text = None
		self._numlines = 0
		self._rawtext = rawtext
		try:
			self.parse_file()	
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
	def date(self):
	    return self._date

	@property
	def rawtext(self):
	    return self._rawtext
	
	@property
	def text(self):
	    return self._text

	def has_valid_data(self):
		if self.id and self.rollnum and self.text:
			return True
		else:
			return False

	'''
	Reads the header for each page and sets page attributes accordingly.
	'''
	def parse_file(self):
		lines = self.rawtext.split(u'|')
		match = re.match(r'(\w+(county))_(\d+)-(\d+)',lines[1])
		self._id = match.group(2)
		self._rollnum = match.group(3)
		self._text = ''.join(lines[4:])	

class ExtractionTask(object):

	def __init__(self, county=None, logger=None):
		self.logger = logger or logging.getLogger(__name__)
		self._pagepath = None
		self._countyfile = None
		self._county = county
		self._numlines = defaultdict(int)
		self._avglines = 0
		self._num_failed = 0
		self._failures = []
		self._text = None
		self._totalpages = 0
		self._pagepath = os.path.join(OUTDIR, county + '.txt')		
		self._validdata = []
		self.logger.info('creating {county} extractor'.format(
			county=county))

	@property
	def county(self):
	    return self._county
	
	@property
	def num_succeeded(self):
	    return self._num_processed
	
	@property
	def num_failed(self):
	    return self._num_failed

	'''
	Opens the appropriate county file, stores the lines in the instantiated ExtractionTask object,
	and counts the number of lines found in the file.
	'''
	def load_data(self):
		with codecs.open(self._pagepath, 'r', 'utf8') as infile:
			self._countyfile = infile.readlines()

		self._totalpages = len(self._countyfile)
		self.logger.info('loaded {num} pages for {county}'.format(
			county=self._county, num=self._totalpages))

	'''
	Increments the fail-to-create-page counter.
	'''
	def increment_fail(self, page):
		self.logger.debug('Page {pageid} in roll {rollnum} failed'.format(pageid=page.id, rollnum=page.rollnum))
		self._num_failed += 1
		self._failures.append(page)

	'''
	Creates _successes.txt and _failures.txt files for each county.  Also updates the extractor 
	summary with relevant statistics about row-wise and column-wise extraction for the county, 
	as well as values that summarize the number of pages that had any amount of successful
	row- or column-wise extraction.
	'''
	def create_files(self):
		self.logger.info('writing {county} successes to file'.format(
			county=self.county))
		with codecs.open('{county}_successes.txt'.format( # XXX Writing is slow and sloppy
			county=self.county), 'a', 'utf8') as outfile:
				for page in self._validdata:
					for row in page['rows']:
						outfile.write("{id},{rollnum},{row}\n".format(
						id=page['id'], rollnum=page['rollnum'], row=row))
						self.logger.debug('line length is {x} n-grams'.format(x=len(row.split(' '))))

		self.logger.info('writing {county} failures to file'.format(county=self.county))
		if self._num_failed > 0:
			with codecs.open('{county}_failures.txt'.format(
				county=self.county), 'a', 'utf8') as outfile:
				for line in self._failures:
					outfile.write("%s\n" % line)

		if not os.path.isfile('extractor_summary.txt'):
			with codecs.open('extractor_summary.txt', 'a', 'utf8') as outfile:
				outfile.write('county,pct_pg_failed,n_avg_rows,max_rows\n')

		with codecs.open('extractor_summary.txt', 'a', 'utf8') as outfile:
			biggest = max(self._numlines.keys())
			outfile.write('{county},{rate},{avg},{max}\n'.format(
				county=self.county,rate=float(self._num_failed)/self._totalpages,
				avg=self._avglines, max=biggest))

	'''
	Kicks off the extraction task.  Tries to convert each line to a Page object.  If successful,
	tries to extract the rows from the page.  Then for each successful row found, tries to extract
	columns from each row found.
	'''
	def start(self):
		for line in self._countyfile:
			page = Page(line)
			if page.has_valid_data():
				parsed_page = self.get_rows(page)
				parsed_page['rows'] = self.get_columns(parsed_page['rows'])
				self._validdata.append(parsed_page)
			else:				
				self.increment_fail(page)
#			break

		self._avglines = sum(k*v for k,v in self._numlines.items()) / float(self._totalpages - self._num_failed)
		self.logger.info('{county} parse complete, {x} page(s) failed to parse, average of {y} rows found, max of {z} rows'.format(
			county=self.county, x=self._num_failed, y=int(self._avglines), z=max(self._numlines.keys())))
		self.create_files()

class AlamedaExtractionTask(ExtractionTask):

	def __init__(self, county='alameda', logger=None):		
		ExtractionTask.__init__(self, county=county)				

	#def get_addresspids_per_page(self, page):
		'''
		write regex to detect addresses
		retrieve tuples of (address, nearest PID after)
		return dict of tuples per page
		'''

	def get_rows(self, page): # Extracts rows from a page
		rows = page.text
		result = []
		
		seps = [r'Dem', r'Rep', r'Declines'] # First row extraction
		for sep in seps:
			rows = re.sub(sep, ','+sep.strip()+'\n', rows)		
		rows = rows.split('\n')

		for row in rows: # Second row extraction
			if row.endswith('\r'):
				continue
			if len(row) < 1:
		 		continue
		 	result.append(row)

		self.logger.debug('{num} lines found on page {id} and roll {rollnum}'.format(
			num=len(rows), id=page.id, rollnum=page.rollnum))
		self._numlines[len(result)] += 1
 		return {'id':page.id, 'rollnum':page.rollnum, 'date':page.date, 'rows':result}

 	def get_columns(self, rows): # Extract columns from rows
 		result = []
 		if len(rows) > 0: 			
		 	for row in rows:		 		
		 		row = str(row.strip())			
		 		row = re.sub(r'^(\d+)\s+', '', row) 				
		 		row = re.findall(r'^(.+?)(\d.+)', row)
				if len(row) < 1:
		 			continue		
		 		result.append(','.join(row[0]))
 		return result

	# XXX TBD

class SanFranciscoExtractionTask(ExtractionTask):

	def __init__(self, county='sanfrancisco', logger=None):		
		ExtractionTask.__init__(self, county=county)				

	def get_rows(self, page):
		rows = page.text
		seps = [r'Dem', r'Rep', r'Declines']
		for sep in seps:
			rows = re.sub(sep, ','+sep.strip()+'\n', rows)
		rows = rows.split('\n')
		self.logger.debug('{num} lines found on page {id} and roll {rollnum}'.format(
			num=len(rows), id=page.id, rollnum=page.rollnum))
		self._numlines[len(rows)] += 1
 		return {'id':page.id, 'rollnum':page.rollnum, 'date':page.date, 'rows':rows}

# 	def get_columns(self, rows):

class SanBernardinoExtractionTask(ExtractionTask):

	def __init__(self, county='sanbernardino', logger=None):		
		ExtractionTask.__init__(self, county=county)				

	def get_rows(self, page):
		data = page.text
		seps = [r'Democrat', r'Republican', r'Declines to State']
		for sep in seps:
			rows = re.sub(sep, ','+sep.strip()+'\n', rows)		
		rows = rows.split('\n')
		self.logger.debug('{num} lines found on page {id} and roll {rollnum}'.format(
			num=len(rows), id=page.id, rollnum=page.rollnum))
		self._numlines[len(rows)] += 1
 		return {'id':page.id, 'rollnum':page.rollnum, 'date':page.date, 'rows':rows}

#	def get_columns(self, rows):


def run():
	logger = logging.getLogger(__name__)
	logger.info("starting processing job")

	alameda_task = AlamedaExtractionTask()
	alameda_task.load_data()
	alameda_task.start()

#	sanfrancisco_task = SanFranciscoExtractionTask()
#	sanfrancisco_task.load_data()
#	sanfrancisco_task.start()

#	sanbernardino_task = SanBernardinoExtractionTask()
#	sanbernardino_task.load_data()
#	sanbernardino_task.start()


