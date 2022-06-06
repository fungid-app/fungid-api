import concurrent.futures
import fileinput
from fastbook import *
from os.path import exists

newsize = 224

rsz = Resize(newsize, ResizeMethod.Pad, pad_mode='zeros')


def resize_image(line):
    inputfile = line.strip()
    outputfile = inputfile.replace("500", str(newsize))

    if not exists(outputfile):
        img = PILImage.create(inputfile)
        img = rsz(img)
        img.save(inputfile.replace("500", str(newsize)))


if __name__ == "__main__":
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(resize_image, fileinput.input())
