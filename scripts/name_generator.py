# name_generator.py
"""Copyright 2010 Joshua Grigonis
This file is written by Joshua Grigonis.
Redistribution or reuse is not permitted without express written consent.

contact: josh.grigonis@gmail.com
"""
import os
import random
import string
import numpy as np

class SimpleNameGenerator(object):
    """A class for generating first and last names

    This class depends on 3 external files that are expected to have 1 name
    per line.  It uses a file for male first names, female first names, and
    then another file for last names.  If your names are not dependent on
    the sex, you could use the same file for male and female first names.

    """
    def __init__(self, female_name_file='names.female.first.txt', \
                 male_name_file='names.male.first.txt', \
                 last_name_file='names.last.txt'):
        """Create the object using the 3 external files.

        This function will call 2 methods, 1 to read in the data from the
        three text files, and another to make the name lists.

        """
        self.female_name_file = female_name_file
        self.male_name_file = male_name_file
        self.last_name_file = last_name_file
        self.read_data()
        self.make_name_lists()

    def read_data(self):
        """Read in the data from each of the 3 files."""
        with open(self.male_name_file, 'r') as m:
            self.male_name_data = m.readlines()
        with open(self.female_name_file, 'r') as f:
            self.female_name_data = f.readlines()
        with open(self.last_name_file, 'r') as l:
            self.last_name_data = l.readlines()
    def make_name_lists(self):
        """Create lists of names based on the data members.

        Our assumption is that the lines may contain multiple strings, but
        that the name is the first string.

        """
        self.male_names = []
        for line in self.male_name_data:
            self.male_names.append(string.split(line)[0])
        self.female_names = []
        for line in self.female_name_data:
            self.female_names.append(string.split(line)[0])
        self.last_names = []
        for line in self.last_name_data:
            self.last_names.append(string.split(line)[0])

    def generate_name(self, sex):
        """Generate a name, based on the sex.

        We just pick a random choice from the correct sex names list and
        tuple it together with a random choice from the last names list.

        """
        if sex in ["m", "male"]:
            return random.choice(self.male_names), random.choice(self.last_names)
        else:
            return random.choice(self.female_names), random.choice(self.last_names)

class NameAndFrequency(object):
    """This class just holds a name and the starting cumulative frequency and the
    ending cumulative frequency.

    """
    def __init__(self, name, start, end):
        """Init the data members."""
        self.name = name
        self.start = start
        self.end = end
    def __str__(self):
        """Return the object as a string."""
        return self.name + " " + str(self.start) + " " + str(self.end)

class NameGenerator(SimpleNameGenerator):
    """Extends the SimpleNameGenerator class to output random names
    based on actual frequency.

    """
    def make_name_lists(self):
        """Create a NameAndFrequency object for each name in each list."""
        self.male_names = []
        self.male_freqs = []
        self.female_names = []
        self.female_freqs = []
        self.last_names = []
        self.last_freqs = []
        self.make_names(self.male_name_data, self.male_names,self.male_freqs)
        self.make_names(self.female_name_data, self.female_names,self.female_freqs)
        self.make_names(self.last_name_data, self.last_names,self.last_freqs)
    def make_names(self, datalist, namelist,freqs):
        """Actually create the NameAndFrequency objects here.

        The name needs to be in the first column, and the cumulative
        frequency value needs to be in the third.

        """
        for line in datalist:
            namelist.append(string.split(line)[0])
            newf = float(string.split(line)[1])
            if newf == 0:
                newf = .0001
            freqs.append(newf)
        s = sum(freqs)
        for i in range(len(freqs)):
            freqs[i] = freqs[i]/s
    def generate_name(self, sex):
        """Generate a random name, based on frequency.

        We pick the correctly sexed name, and a last name from our lists.
        The magic numbers, e.g. 90.483, 90.040, and 90.024 are picked
        from the name list files by manual inspection.  We need to
        subtract -0.001 from the rlast random number as the random float
        will always (?) have extra digits beyond the thousands place
        which we want to ignore.  Many of the names towards the end of
        last names list have less than 0.001 percent frequency, so their
        start range and end range are equal.  If the random number hits
        one of those, we put all the matching names into a list and
        pick a random choice from that list.

        """
        lastname = np.random.choice(self.last_names,1,p=self.last_freqs)[0]
        if sex in ["m", "male"]:
            firstname = np.random.choice(self.male_names,1,p=self.male_freqs)[0]
        else:
            firstname = np.random.choice(self.female_names,1,p=self.female_freqs)[0]
        return firstname, lastname
