import concurrent.futures
import fileinput
from fastbook import *
from os.path import exists

newsize = 224

rsz = Resize(newsize, ResizeMethod.Pad, pad_mode='zeros')


def resize_image(line):
    inputfile = line.strip()
    outputfile = inputfile.replace("/500/", '/' + str(newsize) + '/')

    if not exists(outputfile):
        try:
            img = PILImage.create(inputfile)
            img = rsz(img)
            img.save(outputfile)
            print("resized file: ", outputfile)
        except Exception as e:
            print(e)
            print(inputfile)
    else:
        print("did not resize file: ", outputfile)


if __name__ == "__main__":
    with concurrent.futures.ThreadPoolExecutor(max_workers=64) as executor:
        executor.map(resize_image, fileinput.input())
