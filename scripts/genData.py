import random
import pickle
import copy
from faker import Faker

import name_generator

PAGE_SIZE=50
NUM_PAGES=100

fields= ["name","occ","addr","aff","gender","city"]
vary = ["occ","addr","gender","city"]
def genData():
    foo = name_generator.NameGenerator()
    fake = Faker()
    for i in range(10):
        middle = copy.deepcopy(vary)
        random.shuffle(middle)
        if random.random() < .95:
            middle.remove("gender")
        if random.random() < .95:
            middle.remove("city")
        fmt = ["name"]
        for ent in middle:
            fmt.append(ent)
        fmt.append("aff")
        for j in range(1):
            out = ""
            for elt in fmt:
                if elt == "name":
                    if random.random() < .51:
                        firstname, lastname = foo.generate_name("f")
                        if random.random() < .5:
                            title = "Ms."
                        else:
                            title = "Mrs."
                    else:
                        firstname, lastname = foo.generate_name("m")
                        title = "Mr."
                    out+=lastname+" "+title+" "+firstname
                if elt == "addr":
                    address = fake.address().split('\n', 1)[0]
                    out+=" "+address
            print out

        # firstname, lastname = foo.generate_name("m")
        # print firstname, lastname
        # firstname, lastname = foo.generate_name("f")
        # print firstname, lastname
    return

if __name__ == "__main__":
    genData()
