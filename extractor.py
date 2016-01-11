import sys, os, codecs, re
import logging
from collections import defaultdict
from pprint import pprint

OUTDIR = '/home/rjweiss/shared/CaliforniaGreatRegister/cleaned'

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

	def parse_file(self): # XXX Fix this so that it's just going from the file id rather than header
		lines = self.rawtext.split(u'|')
		self._id = lines[1]
		self._rollnum = lines[3].split(' ')[1]
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

	def load_data(self):
		with codecs.open(self._pagepath, 'r', 'utf8') as infile:
			self._countyfile = infile.readlines()

		self._totalpages = len(self._countyfile)
		self.logger.info('loaded {num} pages for {county}'.format(
			county=self._county, num=self._totalpages))

	def increment_fail(self, page):
		self.logger.debug('Page {pageid} in roll {rollnum} failed'.format(pageid=page.id, rollnum=page.rollnum))
		self._num_failed += 1
		self._failures.append(page)

	def create_files(self):
		self.logger.info('writing {county} successes to file'.format(
			county=self.county))
		with codecs.open('{county}_successes.txt'.format(
			county=self.county), 'a', 'utf8') as outfile:
				for page in self._validdata:
					for row in page['rows']:						
							outfile.write("{id},{rollnum},{row}\n".format(
							id=page['id'], rollnum=page['rollnum'], row=row))
							self.logger.debug('line length is {x} n-grams'.format(x=len(line.split(' '))))

		self.logger.info('writing {county} failures to file'.format(county=self.county))
		if self._num_failed > 0:
			with codecs.open('{county}_failures.txt'.format(
				county=self.county), 'a', 'utf8') as outfile:
				for line in self._failures:
					outfile.write("%s\n" % line)

		with codecs.open('extractor_summary.txt', 'a', 'utf8') as outfile:
			#outfile.write('{county},{rate},{avg},{max}\n'.format(
			#	county=self.county,rate=float(self._num_failed)/self._totalpages),avg=self._avglines, max=max(self._numlines.keys()))
			outfile.write('{county},{rate}\n'.format(
				county=self.county,rate=float(self._num_failed)/self._totalpages))

	def start(self):
		for line in self._countyfile:
			page = Page(line)
			if page.has_valid_data():
				self._validdata.append(self.get_rows(page))
			else:				
				self.increment_fail(page)

		self._avglines = sum(k*v for k,v in self._numlines.items()) / float(self._totalpages - self._num_failed)
		self.logger.info('{county} parse complete, {x} page(s) failed to parse, average of {y} rows found, max of {z} rows'.format(
			county=self.county, x=self._num_failed, y=int(self._avglines), z=max(self._numlines.keys())))
		self.create_files()

class AlamedaExtractionTask(ExtractionTask):

	def __init__(self, county='alameda', logger=None):		
		ExtractionTask.__init__(self, county=county)				

	def get_rows(self, page): # XXX Extracts rows from a page
		rows = page.text
		seps = [r'Dem', r'Rep', r'Declines'] # XXX county-specific separate task
		for sep in seps:
			rows = re.sub(sep, ','+sep.strip()+'\n', rows)		
		rows = rows.split('\n')
		self.logger.debug('{num} lines found on page {id} and roll {rollnum}'.format(
			num=len(rows), id=page.id, rollnum=page.rollnum))
		self._numlines[len(rows)] += 1
 		return {'id':page.id, 'rollnum':page.rollnum, 'date':page.date, 'rows':rows}

# 	def get_columns(self, rows): # XXX Extract columns from rows

class SanFranciscoExtractionTask(ExtractionTask):

	def __init__(self, county='sanfrancisco', logger=None):		
		ExtractionTask.__init__(self, county=county)				

	def get_rows(self, page):
		rows = page.text
		seps = [r'Dem', r'Rep', r'Declines'] # XXX county-specific separate task
		for sep in seps:
			rows = re.sub(sep, ','+sep.strip()+'\n', rows)		
		
			for row in rows.split('\n'):
				if len(row.split(' ')) > 10:			
					seps = [r'Deo', r'Den', r'Dea'] # XXX county-specific separate task
					for sep in seps:
						row = re.sub(sep, ','+sep.strip()+'\n', row)			
				#pprint(row)	
		
		print type(rows)			
		pprint(rows)	
		sys.exit()


		self.logger.debug('{num} lines found on page {id} and roll {rollnum}'.format(
			num=len(rows), id=page.id, rollnum=page.rollnum))
		self._numlines[len(rows)] += 1
 		return {'id':page.id, 'rollnum':page.rollnum, 'date':page.date, 'rows':rows}

# 	def parse_data(self, rows):

class SanBernardinoExtractionTask(ExtractionTask):

	def __init__(self, county='sanbernardino', logger=None):		
		ExtractionTask.__init__(self, county=county)				

	def get_rows(self, page):
		data = page.text
		seps = [r'Democrat', r'Republican', r'Declines to State'] # XXX county-specific separate task
		for sep in seps:
			rows = re.sub(sep, ','+sep.strip()+'\n', rows)		
		rows = rows.split('\n')
		self.logger.debug('{num} lines found on page {id} and roll {rollnum}'.format(
			num=len(rows), id=page.id, rollnum=page.rollnum))
		self._numlines[len(rows)] += 1
 		return {'id':page.id, 'rollnum':page.rollnum, 'date':page.date, 'rows':rows}

#	def parse_data(self, rows):


def run():
	logger = logging.getLogger(__name__)
	logger.info("starting processing job")

#	alameda_task = AlamedaExtractionTask()
#	alameda_task.load_data()
#	alameda_task.start()

	sanfrancisco_task = SanFranciscoExtractionTask()
	sanfrancisco_task.load_data()
	sanfrancisco_task.start()

#	sanbernardino_task = SanBernardinoExtractionTask()
#	sanbernardino_task.load_data()
#	sanbernardino_task.start()


