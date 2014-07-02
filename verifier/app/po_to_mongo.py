import polib
import sys
import os.path
from pymongo import MongoClient
import models

################################
# This module takes the po files and writes the sentences to mongodb
# This is meant to be used after translate_po.py
# The file should have each entry from the given username translated and each other entry untranslated
# Usage: python po_to_mongo username status 
################################

def write_mongo(po_fn, username, status):
    po = polib.pofile(po_fn)
    i=0
    for entry in po.translated_entries():
        t=models.Sentence()
        t.ingest({'source_language':'en', 'source_sentence':entry.msgid.encode('utf-8'), 'sentenceID': entry.tcomment.encode('utf-8'), 'sentence_num':i, 'file_path':po_fn, 'target_sentence':entry.msgstr.encode('utf-8'), 'target_language':'es', 'username':username,'status':status})
        print t.state
        t.save()
        i=i+1

def extract_entries(username, status):
    if len(sys.argv) <= 1:
        print "Usage: python", ' '.join(sys.argv), "path/to/*.po"
        return

    path = sys.argv[1]
    if not os.path.exists(path):
        print path, "doesn't exist"
        return

    if os.path.isfile(path):
        write_mongo(path, username, status)
        return

    # path is a directory now
    print "walking directory", path

    # Write parallel sentences into two files
    for root, dirs, files in os.walk(path):
        for filename in files:
            if filename.endswith(".po"):
                write_mongo(os.path.join(root,filename), username, status)


def main():
    extract_entries(sys.argv[1], sys.argv[2])

if __name__ == "__main__":
    main()

