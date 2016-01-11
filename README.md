# Overview

Ancestry.com provided an OCR-scanned text file that consists of their collection of the California Great Register for many California counties between the years of 1906-1968.  Ancestry created this text from a collection of scanned images of the microfilm versions of the register.  Before 1906 the registers were handwritten, and so those are not included.  One file consists of every county’s entire scanned history.  Each page of each county’s register is a separate line in the master file.

There are two steps to cleaning this data, (1) subsetting and (2) extracting the data.

## Subsetting

The master data file is cut into separate, county-level files.  This is not technically necessary, but it allowed for visual inspection of each county’s format more easily.

## Extracting

Each county file consists of several lines.  Each line is a page from the record.  Not all pages contain relevant voter registration data.  Each page consists of several rows of information.  To extract the rows of voter data in a structure suited to tabular representation, we developed heuristics to create rows and columns from the raw page string.

Extracting the rows from each page is problematic for two reasons.  First, we don’t know ground truth about basic statistics for each county (e.g. number of rows we should be looking for, number of rows per page, etc).  This means we don’t know how good or bad our heuristics are, and thus we make assertions about what is a “successful” row- or column-wise extraction.

Second, the scanned text is noisy with many scanning errors.  Most problems stem from the fact that the OCR software does not preserve newline characters, and so most data is concatenated into one long string.  Much of the data can be recovered with simple regex heuristics, e.g.:  

1. Find the partisan identity for the row (e.g. “Dem” or “Rep”) 
2. Insert newline at the end of the matching partisan identity substring

Given that OCR has some transcription errors (e.g. “Deo”, “Den”, “Dea”, “De”, “D e m”, etc.), we create additional heuristics that filter the data in a specific order, resulting in a cleaned .csv file ready to upload to a SQL server:

1. Split on whitespace; if line length > 10, insert new lines after common misspellings of delimiters

However, cases where we currently lack heuristics are enumerated below:

1. Some counties have multiple columns to a page for some years.  That results in columns that are concatenated with no clear delimiter to split them.

2. Whitespace is overdetected, resulting in extremely long string lengths that fail to match the regex.

3. Because the pages are hand-scanned, there are rotation issues with the images that resulted in OCR transcription errors.  There is a complete loss of row structure for these pages.

# Requirements - TBD
## File directory: TBD

# Extraction process

### Row-wise

Given a string that represents a single page, insert corrective newline characters where appropriate to reconstruct the number of rows originally on the page.  

### Column-wise

Given an object that represents a list of row strings, insert corrective delimiters where appropriate to reconstruct the number of columns originally on the page

# Files description

- **main.py** - runs the main task that calls subsetter and extractor in sequence.  
- subsetter.py - contains code that creates the new county-level files.  This file only needs to be called once, and so currently this method is commented out in main.py (should auto-detect that it doesn’t need to be run again)
- **extractor.py** - contains code that extracts row and column structure from the county-level string that represents pages of scanned voter data

# Class and method description

- **Page** - Every line in a county file is converted to a Page object.  A Page object has attributes that describe values or quantities about the Page and where it comes from (e.g. which roll number and id, what’s the number of lines extracted).
- **ExtractionTask** - Extracting the data as rows and columns is described as an ExtractionTask.  The parent class abstracts most of the generic behaviors and attributes of an ExtractionTask (e.g. success and failure rates, task attributes such as the county, statistics such as number of pages found, average number of rows and columns extracted) There are a number of objects that inherit from ExtractionTask, each one representing a specific county.  This is because heuristics have to be created bespoke for each county.  Bespoke county-level heuristics are created by member methods in each county’s ExtractionTask class.
- **get_rows()** - Contains the heuristics needed to pull out rows from each page.  This method is defined by each county ExtractionTask class.
- **get_columns()** - Contains the heuristics needed to pull out columns from each row.  This method is defined by each county ExtractionTask class.




