import polib
import sys
import os.path
from pymongo import MongoClient
import models

################################
# This module takes the po files and writes the sentences to mongodb
# This is meant to be used after translate_po.py
# The file should have each entry from the given username translated and each other entry untranslated
# Usage: python po_to_mongo /path/to/*.po username status language
################################

def write_mongo(po_fn, userID, status, language, po_root):
    po = polib.pofile(po_fn)
    rel_fn = os.path.relpath(po_fn, po_root)
    rel_fn = os.path.splitext(rel_fn)[0]
    f = models.File({ u'file_path': rel_fn,
                      u'priority': 0,
                      u'source_language': u'en',
                      u'target_language': language })
    i = 0
    for entry in po.translated_entries():
        t = models.Sentence({ u'source_language': u'en', 
                              u'source_sentence': entry.msgid.encode('utf-8'), 
                              u'sentenceID': entry.tcomment.encode('utf-8'), 
                              u'sentence_num': i, 
                              u'fileID': f._id, 
                              u'target_sentence': entry.msgstr.encode('utf-8'), 
                              u'target_language': language, 
                              u'userID': userID,
                              u'status': status, 
                              u'update_number': 0, 
                              u'num_approves': 0})
        print t.state
        t.save()
        i += 1

def extract_entries(mongodb, path, username, status, language):

    if not os.path.exists(path):
        print path, "doesn't exist"
        return

    userID=mongodb['veri']['users'].find_one({'username': username})[u'_id']

    if os.path.isfile(path):
        write_mongo(path, userID, status, language, os.path.dirname(path))
        return

    # path is a directory now
    print "walking directory", path

    # Write parallel sentences into two files
    for root, dirs, files in os.walk(path):
        for filename in files:
            if filename.endswith(".po"):
                write_mongo(os.path.join(root,filename), userID, status, language, path)


def main():
    if len(sys.argv) < 5:
        print "Usage: python", ' '.join(sys.argv), "<path/to/*.po> <username> <status> <language>"
        return
    mongodb = MongoClient()
    extract_entries(mongodb, sys.argv[1],sys.argv[2], sys.argv[3], sys.argv[4])

if __name__ == "__main__":
    main()

