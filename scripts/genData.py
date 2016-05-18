import random
import pickle
import copy
from faker import Faker
import csv
import string
import name_generator
from random_occ import randomOccGenerator
PAGE_SIZE=50
NUM_PAGES=100

fields= ["name","occ","addr","aff","gender"]
vary = ["occ","addr","gender"]
def genData():
    foo = name_generator.NameGenerator()
    fake = Faker()
    occGenerator = randomOccGenerator()
    for i in range(1):
        middle = copy.deepcopy(vary)
        random.shuffle(middle)
        if random.random() < .99:
            middle.remove("gender")
        if random.random() < .5:
            aff_chars = 1
        else:
            aff_chars = 3
        fmt = ["name"]
        for ent in middle:
            fmt.append(ent)
        fmt.append("aff")
        page = ""
        for j in range(10):
            out = ""
            for elt in fmt:
                if elt == "name":
                    lastname,title,firstname,gender= getName(foo)
                    out+=lastname+" "+title+" "+firstname + " "
                if elt == "addr": #generate address
                    address = fake.address().split('\n', 1)[0]
                    out+=address + " "
                if elt == "occ": #genearte occupation
                    out+=occGenerator.occ() + " "
                if elt == "gender":
                    out+= gender + " "
                if elt == "aff":
                    aff = getAff()
                    out+= aff + " "
            out =  corrupt(out)
            page+=out
        print page
        # firstname, lastname = foo.generate_name("m")
        # print firstname, lastname
        # firstname, lastname = foo.generate_name("f")
        # print firstname, lastname
    return


def getName(foo):
    title = ""
    if random.random() < .51: #51% women
        gender = "female"
        firstname, lastname = foo.generate_name("f")
        if random.random() < .4: #40% chance to include title
            if random.random() < .5: #50% split of ms vs mrs
                title = "Ms."
            else:
                title = "Mrs."
    else: #genearte male
        gender = "male"
        firstname, lastname = foo.generate_name("m")
        if random.random() < .4: #40% chance to include title
            title = "Mr."
    lastname+= " "+random.choice(string.ascii_uppercase)
    return lastname,title,firstname,gender

def getAff():
    rnd = random.random()
    if rnd < .45: #democrat
        aff = "D"
    elif rnd < .9:
        aff = "R"
    elif rnd < .95:
        aff = "Ds"
    else:
        aff = random.choice(string.ascii_uppercase)
    return aff


def corrupt(s):
    s = list(s)
    for i in range(len(s)):
        if random.random() < .02:
            s[i] = random.choice(string.ascii_letters)
        if random.random() < .05:
            s[i] = " "
    return ''.join(s)
if __name__ == "__main__":
    genData()
