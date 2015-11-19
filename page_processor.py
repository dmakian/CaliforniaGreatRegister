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
		self._rawtext = rawtext
		self.parse_file()		

#	def __repr__(self):
#		return "Page()"

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

	def set_id(self, id):
		self._id = id

	def set_rollnum(self, rollnum):
		self._rollnum = rollnum

	def set_date(self, date):
		self._date = date

	def parse_file(self):
		return True

	def has_valid_data(self):
		if self.id and self.rollnum and self.rawtext:
			return True
		else:
			return False

class PageProcessor(object):

	def __init__(self, county=None, logger=None):
		self.logger = logger or logging.getLogger(__name__)
		self._pagepath = None
		self._countyfile = None
		self._county = county
		self._num_failed = 0
		self._failures = []
		self._text = None
		self._totalpages = 0
		self._pagepath = os.path.join(OUTDIR, county + '.txt')
		self.logger.info('creating page processor for {county} county'.format(county=county))

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

class AlamedaPageProcessor(PageProcessor):

	def __init__(self, county='alameda', logger=None):
		PageProcessor.__init__(self, county=county)
		self._validdata = []
		
	def start(self):
		for line in self._countyfile:
			page = AlamedaPage(line)
			if page.has_valid_data():
				self._validdata.append(self.get_data(page))
			else:				
				self.increment_fail(page)

		self.logger.info('alameda parse complete, {x} page(s) failed'.format(x=self._num_failed))
		self.create_files()

	def get_data(self, page):
		data = split(page.text, ['Dem', 'Rep'])
		self.logger.info('{num} lines found on page {id} and roll {rollnum}'.format(num=len(data), id=page.id, rollnum=page.rollnum))
		#return "{id},{rollnum},{date},{data}".format(id=page.id, rollnum=page.rollnum, date=page.date, data=data)
		return {'id':page.id, 'rollnum':page.rollnum, 'date':page.date, 'data':data}

	def create_files(self):
		# create good data file
		with codecs.open('alameda_successes.txt', 'a', 'utf8') as outfile:
				for page in self._validdata:
					for line in page['data']:
						outfile.write("{id},{rollnum},{date},{data}\n".format(id=page['id'], rollnum=page['rollnum'], date=page['date'], data=line))
#						outfile.write("%s\n" % line)
		# create bad data file
		if self._num_failed > 0:
			with codecs.open('alameda_failures.txt', 'a', 'utf8') as outfile:
				for line in self._failures:
					outfile.write("%s\n" % line)

class AlamedaPage(Page):

	def __init__(self, rawtext, logger=None):
		Page.__init__(self, rawtext)

	def parse_file(self):
		#self.logger.info('converting line to page')
		lines = self.rawtext.split(u'|')
		try:
			self.set_id(lines[1])
		except:
			self.logger.warn('Failed to get page id')
		try:
			self.set_rollnum(lines[3].split(' ')[1])
		except:
			self.logger.warn('Failed to get page roll number')
		self._text = lines[5]
		self.set_date(self._get_date(self.text))
		if self.date and self.id:
			return
		#else:
			#self.logger.error(text)


	def _get_date(self, text):
		datepattern = r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|(Nov|Dec)(?:ember)?)\s(\d{0,2})\s(\d{0,4})'
		match = re.match(datepattern, text)
		if match:
			return match.group(0)
		else:
			return None

	def has_valid_data(self):
		if self.id and self.rollnum and self.text and self.date:
		#if self.date:
			return True
		else:
			return False

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

