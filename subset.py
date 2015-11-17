import re, codecs, os
from collections import defaultdict
from pprint import pprint
from progressbar import ProgressBar

'''
Job constants; change OUTDIR to appropriate
'''
TOTALPAGES = 595890 # Hardcoded total page count, known a priori
OUTDIR = '/Users/rweiss/Documents/Stanford/ancestry/cleaned'

'''
Builds a county dict file that maps county regex to a county-specific file
'''
def build_counties():
	return {
		r'alamedacounty': 'alameda.txt',
		r'alpinecounty': 'alpine.txt',
		r'amadorcounty': 'amador.txt',
		r'buttecounty': 'butte.txt',
		r'calaverascounty': 'calaveras.txt',
		r'colusacounty': 'colusa.txt',
		r'contracostacounty': 'contracosta.txt',
		r'delnortecounty': 'delnorte.txt',
		r'eldoradocounty': 'eldorado.txt',
		r'fresnocounty': 'fresno.txt',
		r'glenncounty': 'glenn.txt',
		r'humboldtcounty': 'humboldt.txt',
		r'imperialcounty': 'imperial.txt',
		r'inyocounty': 'inyo.txt',
		r'kerncounty': 'kern.txt',
		r'kingscounty': 'kings.txt',
		r'lakecounty': 'lake.txt',
		r'lassencounty': 'lassen.txt',
		r'losangelescounty': 'losangeles.txt',
		r'maderacounty': 'madera.txt',
		r'marincounty': 'marin.txt',
		r'mariposacounty': 'mariposa.txt',
		r'mendocinocounty': 'mendocino.txt',
		r'mercedcounty': 'merced.txt',
		r'modoccounty': 'modoc.txt',
		r'monocounty': 'mono.txt',
		r'montereycounty': 'monterey.txt',
		r'napacounty': 'napa.txt',
		r'nevadacounty': 'nevada.txt',
		r'orangecounty': 'orange.txt',
		r'placercounty': 'placer.txt',
		r'plumascounty': 'plumas.txt',
		r'riversidecounty': 'riverside.txt',
		r'sacramentocounty': 'sacramento.txt',
		r'sanbenitocounty': 'sanbenito.txt',
		r'sanbernardinocounty': 'sanbernardino.txt',
		r'sandiegocounty': 'sandiego.txt',
		r'sanfranciscocounty': 'sanfrancisco.txt',
		r'sanjoaquincounty': 'sanjoaquin.txt',
		r'sanluisobispocounty': 'sanluisobispo.txt',
		r'sanmateocounty': 'sanmateo.txt',
		r'santabarbaracounty': 'santabarbara.txt',
		r'santaclaracounty': 'santaclara.txt',
		r'santacruzcounty': 'santacruz.txt',
		r'shastacounty': 'shasta.txt',
		r'sierracounty': 'sierra.txt',
		r'siskiyoucounty': 'siskiyou.txt',
		r'solanocounty': 'solano.txt',
		r'sonomacounty': 'sonoma.txt',
		r'stanislauscounty': 'stanislaus.txt',
		r'suttercounty': 'sutter.txt',
		r'tehamacounty': 'tehama.txt',
		r'trinitycounty': 'trinity.txt',
		r'tularecounty': 'tulare.txt',
		r'tuolumnecounty': 'tuolumne.txt',
		r'venturacounty': 'ventura.txt',
		r'yolocounty': 'yolo.txt',
		r'yubacounty': 'yuba.txt'
	}

'''
Detects county for a page-line, writes line to appropriate file, and updates observation count
'''
def get_countypage_counts(infile, counties):
	pbar = ProgressBar()
	county_page_counts = defaultdict(int)
	#for line in pbar(infile):
	for line in infile:
		for key in counties.keys():
			if re.match(key, line):
				county_page_counts[counties[key]] += 1
				_write_line_to_countyfile(line, counties[key])
	return county_page_counts

'''
Writes county page counts to a meta file
'''
def write_meta_file(pagecounts):
	with open('subset_meta.txt', 'w') as outfile:
		for key, value in pagecounts.iteritems():
			outfile.write("{txtfile},{rawcount},{prop}\n".format(txtfile=key, rawcount=value, prop=float(value)/TOTALPAGES))

'''
Helper function that writes a line to a county-specific file
'''
def _write_line_to_countyfile(line, countyfile):
	with codecs.open(os.path.join(OUTDIR, countyfile), 'a', 'utf8') as outfile:
		outfile.write(line)

'''
Master method to kick off the job
'''
def run(rawfile):
	counties = build_counties()

	with codecs.open(rawfile, 'r', 'utf16') as infile: #gag
		county_page_counts = get_countypage_counts(infile, counties)
		write_meta_file(county_page_counts)

if __name__ == '__main__':
	print "Starting."
	run('46348_CAVoter.txt')
	print "Done."
