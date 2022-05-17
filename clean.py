import fileinput
from fastbook import *
from fastai.data.external import *
import ntpath
import csv

learn_inf = load_learner('models/clean-res18.pkl')
d = set()

with open("categorized.csv", "r") as f:
    reader = csv.reader(f)
    d = {rows[0]+ "-" + rows[1] for _, rows in enumerate(reader)}
    

print("found {} categorized images".format(len(d)))

inserted = 0

with open("categorized.csv", "a") as f:
    for i, line in enumerate(fileinput.input()):
        inputfile = line.strip()
        _, tail = ntpath.split(inputfile)
        id = tail.replace(".png", "")
        parts = id.split("-")

        if i % 1000 == 0:
            print("{}/{}".format(inserted, i))

        if id not in d:
            try:
                img = Image.open(inputfile)
                pred, pred_idx, probs = learn_inf.predict(inputfile)
                confidence = probs[pred_idx]
                percent = float(confidence)
                f.write(parts[0] + "," + parts[1] + "," + pred + "," + str(percent) + "\n")
                inserted += 1
            except:
                print(inputfile + ",notfound")

 