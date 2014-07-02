import polib
import sys
import os.path
from pymongo import MongoClient
import models

##############################
# This module takes the data in mongodb and writes out any approved sentence translations to the po files
#############################


# writes any approved translations out to file
def write_po(po_fn, mongodb):
    po = polib.pofile(po_fn)

    for entry in po.untranslated_entries():
        t=mongodb['veri']['translations'].find({"status":"approved", "sentenceID":entry.tcomment})
        if t.count()>1:
            print("multiple approved translations with sentenceID: "+entry.tcomment)
            continue
        if t.count()==1:        
            print t[0]
            entry.msgstr = t[0]['translation'].strip().encode("utf-8")
            print entry.msgstr

    print "po.translated_entries()", po.translated_entries()
    # Save translated po file into a new file.
    po.save(po_fn + ".new")

def write_entries(mongodb):
    if len(sys.argv) <= 1:
        print "Usage: python", ' '.join(sys.argv), "path/to/*.po"
        return

    path = sys.argv[1]
    if not os.path.exists(path):
        print path, "doesn't exsit"
        return

    if os.path.isfile(path):
        write_po(path, mongodb)
        return

    # path is a directory now
    print "walking directory", path

    # Write parallel sentences into two files
    for root, dirs, files in os.walk(path):
        for filename in files:
            if filename.endswith(".po"):
                write_po(os.path.join(root,filename),mongodb)


def main():
    mongodb=MongoClient()
    write_entries(mongodb)

if __name__ == "__main__":
    main()

