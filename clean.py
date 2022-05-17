import fileinput
from fastbook import *
from fastai.data.external import *
import ntpath
import csv

learn_inf = load_learner('models/clean-res18.pkl', cpu=True)
d = set()

with open("categorized.csv", "r") as f:
    reader = csv.reader(f)
    d = {rows[0]+ "-" + rows[1] for _, rows in enumerate(reader)}
    

print("found {} categorized images".format(len(d)))

inserted = 0

batch = []


def splitFileName(file):
    _, tail = ntpath.split(file)
    id = tail.replace(".png", "")
    parts = id.split("-")
    return id, parts


def predictBatch(tst_files, output):
    test_dl = learn_inf.dls.test_dl(tst_files)
    preds, _, decoded = learn_inf.get_preds(
        dl=test_dl, with_decoded=True, reorder=False)

    for i, pred in enumerate(preds):
        _, parts = splitFileName(tst_files[i])
        confidence = pred[decoded[i]]
        percent = float(confidence)
        label = learn_inf.dls.vocab[decoded[i]]
        output.write( parts[0] + "," + parts[1] + ',' +
              label + ',' + str(percent) + "\n")


with open("categorized.csv", "a") as f:
    for i, line in enumerate(fileinput.input()):
        file = line.strip()
        id, parts = splitFileName(file)

        if i % 10000 == 0:
            print("{}/{}".format(inserted, i))

        if id not in d:
            batch.append(file)
            inserted += 1

        if len(batch) > 10000:
            print("predicting batch")
            predictBatch(batch, f)
            print("done")
            batch = []

    if len(batch) > 0:
        print("predicting batch")
        predictBatch(batch, f)
        print("done")
        batch = []

 