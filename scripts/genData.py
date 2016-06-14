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

header = "alamedacounty_50-1098|1098|California Voter Registrations, 1900-1968|Roll 50||November 5 1940 OAKLAND PRECINCT NO 316 NAME OOCUPATION ADDRESS AND SEX PARTY "
fields= ["name","occ","addr","aff","gender"]
vary = ["occ","addr","gender"]
def genData():
    foo = name_generator.NameGenerator()
    fake = Faker()
    occGenerator = randomOccGenerator()
    outData = open("rawGen.txt","w")
    labelsOut = open("labelsGen.txt","w")
    for i in range(10):
        print i
        middle = copy.deepcopy(vary)
        random.shuffle(middle) #shuffle the elements of each string for the current page
        if random.random() < .99: ## ESTIMATE: gender in 1% of data
            middle.remove("gender")

        aff_format = 1 ## Affliation format: 1 means one character, 2 means 3 characters
        if random.random() < .5:
            aff_format = 2
        fmt = ["name"]
        for ent in middle:
            fmt.append(ent)
        fmt.append("aff")
        page = ""
        labels = []
        new_header = corrupt(header)
        page +=new_header
        tags = [7] * len(new_header)
        labels.extend(tags)
        for j in range(100):
            new_labels = []
            out = ""
            for elt in fmt:
                if elt == "name":
                    lastname,title,firstname,gender= getName(foo)
                    namestr = lastname+title+firstname
                    tags = [2] * len(namestr)
                    new_labels.extend(tags)
                    out+=namestr+ " "
                    new_labels.append(1)
                if elt == "addr": #generate address
                    address = fake.address().split('\n', 1)[0]
                    tags = [3] * len(address)
                    new_labels.extend(tags)
                    out+=address + " "
                    new_labels.append(1)
                if elt == "occ": #genearte occupation
                    occ = occGenerator.occ()
                    tags = [4] * len(occ)
                    new_labels.extend(tags)
                    out+= occ + " "
                    new_labels.append(1)
                if elt == "gender":
                    tags = [5] * len(gender)
                    new_labels.extend(tags)
                    out+= gender + " "
                    new_labels.append(1)
                if elt == "aff":
                    aff = getAff(aff_format)
                    tags = [6] * len(aff)
                    new_labels.extend(tags)
                    out+= aff + " "
                    new_labels.append(0)
            assert len(out) == len(new_labels), "Incorrect number of labels created"
            out =  corrupt(out)
            labels.extend(new_labels)
            page+=out
        labelstr = ' '.join([str(i) for i in labels])+"\n"
        for c in page:
            outData.write("{}".format(ord(c))+" ")
        outData.write("\n")
        # pasgestr = ' '.join(list(page))+"\n"
        # outData.write(page)
        labelsOut.write(labelstr)
        # print page
        # print len(list(page)),len(labels)
        # firstname, lastname = foo.generate_name("m")
        # print firstname, lastname
        # firstname, lastname = foo.generate_name("f")
        # print firstname, lastname
    return


def getName(foo):
    title = " "
    if random.random() < .51: #51% women
        gender = "female"
        firstname, lastname = foo.generate_name("f")
        if random.random() < .4: #40% chance to include title
            if random.random() < .5: #50% split of ms vs mrs
                title = " Ms. "
            else:
                title = " Mrs. "
    else: #genearte male
        gender = "male"
        firstname, lastname = foo.generate_name("m")
        if random.random() < .4: #40% chance to include title
            title = " Mr. "
    firstname+= " "+random.choice(string.ascii_uppercase)
    return lastname,title,firstname,gender

def getAff(aff_format):
    rnd = random.random()
    if aff_format == 1:
        if rnd < .45: #democrat
            aff = "D"
        elif rnd < .9:
            aff = "R"
        elif rnd < .95:
            aff = "Ds"
        else:
            aff = random.choice(string.ascii_uppercase)
    else:
        if rnd < .45: #democrat
            aff = "Dem"
        elif rnd < .9:
            aff = "Rep"
        elif rnd < .95:
            aff = "Ds"
        else:
            aff = random.choice(string.ascii_uppercase)
    return aff


def corrupt(s):
    s = list(s)
    for i in range(len(s)):
        if random.random() < .01:
            s[i] = random.choice(string.ascii_letters)
        if random.random() < .04:
            s[i] = " "
    return ''.join(s)
if __name__ == "__main__":
    genData()
