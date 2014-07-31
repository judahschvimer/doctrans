import polib
import sys
import os.path
from pymongo import MongoClient
import models
import logging

''''
This module takes the data in mongodb and writes out any approved (or all) sentence translations to the po files
make sure you copy the files first to have a backup in case it messes up
Usage: python mongo_to_po.py path/to/*.po port dbname <all>
'''

logger = logging.getLogger('mongo_to_po')
logging.basicConfig(level=logging.DEBUG)

def write_po(po_fn, db, all):
    ''' writes approved or all trnalstions to file
    :Parameters:
        - 'po_fn': the path to the current po file to write
        - 'db': mongodb database 
        - 'all': whether or not you want all or just approved translations
    '''    
    logger.info("writing "+po_fn)
    po = polib.pofile(po_fn)
    for entry in po.untranslated_entries():
        if all is False: 
            t = db['translations'].find({"status":"approved", "sentenceID":entry.tcomment})
        else:
            t = db['translations'].find({"sentenceID":entry.tcomment})
            
        if t.count() > 1:
            logger.info("multiple approved translations with sentenceID: "+entry.tcomment)
            continue
        if t.count() is 1:        
            entry.msgstr = unicode(t[0]['target-sentence'].strip())

    # Save translated po file into a new file.
    po.save(po_fn)

def write_entries( path, db, all):
    ''' goes through directory tree and writes po files to mongo
    :Parameters:
        - 'path': the path to the top level directory of the po_files
        - 'db': mongodb database 
        - 'all': whether or not you want all or just approved translations
    '''    

    if not os.path.exists(path):
        logger.error("{0} doesn't exist".format(path))
        return

    if os.path.isfile(path):
        write_po(path, db, all)
        return

    # path is a directory now
    logger.info("walking directory {0}".format(path))

    # Write parallel sentences into two files
    for root, dirs, files in os.walk(path):
        for filename in files:
            if filename.endswith(".po"):
                write_po(os.path.join(root,filename), db, all)


def main():
    if len(sys.argv) < 4 or len(sys.argv) > 5:
        print "Usage: python", ' '.join(sys.argv), "path/to/*.po <port> <dbname> <all>"
        return
    all = False

    if len(sys.argv) is 5 and sys.argv[4] is "all":
        all = True

    db = MongoClient('localhost', int(sys.argv[2]))[sys.argv[3]]
    write_entries(sys.argv[1], db, all)

if __name__ == "__main__":
    main()

