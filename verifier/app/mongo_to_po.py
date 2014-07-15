import polib
import sys
import os.path
from pymongo import MongoClient
import models

##############################
# This module takes the data in mongodb and writes out any approved sentence translations to the po files
# make sure you copy the files first
# Usage: python mongo_to_po.py path/to/*.po <-all>
#############################


# writes any approved translations out to file
def write_po(po_fn, db, all):
    po = polib.pofile(po_fn)

    for entry in po.untranslated_entries():
        if all is False: 
            t = db['translations'].find({"status":"approved", "sentenceID":entry.tcomment})
        else:
            t = db['translations'].find({"sentenceID":entry.tcomment})
            
        if t.count() > 1:
            print("multiple approved translations with sentenceID: "+entry.tcomment)
            continue
        if t.count() is 1:        
            print t[0]
            entry.msgstr = t[0]['translation'].strip().encode("utf-8")
            print entry.msgstr

    print "po.translated_entries()", po.translated_entries()
    # Save translated po file into a new file.
    po.save(po_fn)

def write_entries(mongodb, all, path):

    if not os.path.exists(path):
        print path, "doesn't exsit"
        return

    if os.path.isfile(path):
        write_po(path, mongodb, all)
        return

    # path is a directory now
    print "walking directory", path

    # Write parallel sentences into two files
    for root, dirs, files in os.walk(path):
        for filename in files:
            if filename.endswith(".po"):
                write_po(os.path.join(root,filename), mongodb, all)


def main():
    if len(sys.argv) <= 5:
        print "Usage: python", ' '.join(sys.argv), "path/to/*.po <all> <port> <dbname>"
        return
    all = False

    if len(sys.argv) > 2 and sys.argv[3] is "all":
        all = True

    db = MongoClient('localhost', int(sys.argv[4]))[sys.argv[5]]
    write_entries(db, all, sys.argv[1])

if __name__ == "__main__":
    main()

