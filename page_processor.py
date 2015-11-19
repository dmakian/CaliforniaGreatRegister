import sys, os, codecs, re
import logging
from collections import defaultdict

OUTDIR = '/Users/rweiss/Documents/Stanford/ancestry/cleaned'

class Page(object):

	def __init__(self, rawtext, logger=None):
		self.logger = logger or logging.getLogger(__name__)
		self._id = None
		self._rollnum = None
		self._date = None
		self._text = None
		self._numlines = 0
		self._rawtext = rawtext

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

	#XXX Old code
	def set_id(self, id):
		try:
			self._id = id
		except:
			#self.logger.error('Failed to get page id')
			raise ValueError('Failed to get page id')

	def set_rollnum(self, rollnum):
		try:
			self._rollnum = rollnum
		except:
			raise ValueError('Failed to get page roll number')

	def set_date(self, date):
		try:
			self._date = date
		except:
			raise ValueError('Failed to get date')

	def has_valid_data(self):
		if self.id and self.rollnum and self.text and self.date:
			return True
		else:
			return False
	
 	# Override for county-specific date strings
	#def _get_date(self, text):
	#	return None

	#def parse_file(self):
	#	return None

class PageProcessor(object):

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
		self.logger.info('creating page processor for {county} county'.format(
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
		self.logger.info('loaded {num} lines for {county}'.format(
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
					for line in page['data']:
						outfile.write("{id},{rollnum},{date},{data}\n".format(
							id=page['id'], rollnum=page['rollnum'], date=page['date'], data=line))

		self.logger.info('writing {county} failures to file'.format(county=self.county))
		if self._num_failed > 0:
			with codecs.open('{county}_failures.txt'.format(
				county=self.county), 'a', 'utf8') as outfile:
				for line in self._failures:
					outfile.write("%s\n" % line)

		with codecs.open('page_processor_meta.txt', 'a', 'utf8') as outfile:
			#outfile.write('{county},{rate},{avg},{max}\n'.format(
			#	county=self.county,rate=float(self._num_failed)/self._totalpages),avg=self._avglines, max=max(self._numlines.keys()))
			outfile.write('{county},{rate}\n'.format(
				county=self.county,rate=float(self._num_failed)/self._totalpages))

class AlamedaPageProcessor(PageProcessor):

	def __init__(self, county='alameda', logger=None):		
		PageProcessor.__init__(self, county=county)				

	# XXX Move this to base class
	def start(self):
		for line in self._countyfile:
			page = AlamedaPage(line) # XXX detect what page type to use given county type
			if page.has_valid_data():
				self._validdata.append(self.get_data(page))
			else:				
				self.increment_fail(page)

		self._avglines = sum(k*v for k,v in self._numlines.items()) / float(self._totalpages - self._num_failed)
		self.logger.info('alameda parse complete, {x} page(s) failed, average of {y} rows extracted, max of {z} lines seen'.format(
			x=self._num_failed, y=self._avglines, z=max(self._numlines.keys())))
		self.create_files()

	def get_data(self, page):
		data = split(page.text, ['Dem', 'Rep', 'Declines']) # XXX county-specific separate task
		self.logger.info('{num} lines found on page {id} and roll {rollnum}'.format(
			num=len(data), id=page.id, rollnum=page.rollnum))
		self._numlines[len(data)] += 1
 		return {'id':page.id, 'rollnum':page.rollnum, 'date':page.date, 'data':data}

class AlamedaPage(Page):

	def __init__(self, rawtext, logger=None):
		Page.__init__(self, rawtext)		
		self._datepattern = r'(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|(Nov|Dec)(?:ember)?)(\d{0,2}|\w)(\d{0,4})'
		try:
			self.parse_file()	
		except:
			self.logger.error('Failed to parse page data')

	def parse_file(self):
		lines = self.rawtext.split(u'|')
		self._id = lines[1]
		self._rollnum = lines[3].split(' ')[1]
		self._text = ''.join(lines[4:])	
		self.set_date(self._get_date(self.text))

	# Alameda-specific date.
	def _get_date(self, text):
		s =  ''.join(text.split())# remove all whitespace, county specific
		match = re.search(self._datepattern, s)
		if match:
			return match.group(0)
		else:
			return None

def run():
	logger = logging.getLogger(__name__)
	logger.info("starting processing job")
	alameda_processor = AlamedaPageProcessor()
	alameda_processor.load_data()
	alameda_processor.start()

#http://stackoverflow.com/questions/4697006/python-split-string-by-list-of-separators
def split(txt, seps):
    default_sep = seps[0]

    # we skip seps[0] because that's the default seperator
    for sep in seps[1:]:
        txt = txt.replace(sep, default_sep)
    return [i.strip() for i in txt.split(default_sep)]

