import polib
import sys
import os.path
import logging

'''
This module takes a po file and writes it to a parallel corpus
It's useful for taking the po files and using them for training data for build_model.py
Usage: python po_to_corpus.py path/to/*.po
'''
logger = logging.getLogger('po_to_corpus')
logging.basicConfig(level=logging.DEBUG)

def write_po_file(source_doc, target_doc, po_file_name):
    '''This function writes two files in english and spanish from a po file's translated entries
    :Parameters:
        - 'source_doc': doc to put source language text in 
        - 'target_doc': doc to put target language text in 
        - 'po_file_name': po file to take text from 
    '''
    logger.info("processing "+po_file_name)
    po = polib.pofile(po_file_name)
    for entry in po.translated_entries():
        print >> source_doc, entry.msgid.encode('utf-8')
        print >> target_doc, entry.msgstr.encode('utf-8')

def extract_translated_entries(po_path, source_doc_fn, target_doc_fn):
    '''This function traverses the directories and extracts the text from all of the po files into the same docs 
    :Parameters:
        - 'source_doc': doc to put source language text in 
        - 'target_doc': doc to put target language text in 
        - 'po_file_name': po file to take text from 
    '''

    if os.path.exists(po_path) is False:
        logger.error(po_path+" doesn't exist")
        return

    # path is a directory now
    logger.info("walking directory "+po_path)

    with open(source_doc_fn, "w") as source_doc:
        with open(target_doc_fn, "w") as target_doc:
            if os.path.isfile(po_path):   
                write_po_file(source_doc, target_doc, po_path)
    
            # Write parallel sentences into two files
            for root, dirs, files in os.walk(po_path):
                for filename in files:
                    if filename.endswith(".po"):
                        write_po_file(source_doc, target_doc, os.path.join(root, filename))


def main():
    if len(sys.argv) != 4:
        print "Usage: python", ' '.join(sys.argv), "path/to/*.po source_doc target_doc"
        return
    extract_translated_entries(sys.argv[1], sys.argv[2], sys.argv[3])

if __name__ == "__main__":
    main()

