import polib
import sys
import os.path

#######################################
# This module takes a po file and writes it to a parallel corpus
# It's useful for taking the po files and using them for training data for build_model.py
# Usage: python po_to_corpus.py path/to/*.po
######################################

def write_po_file(source_doc, target_doc, po_file_name):
    print "processing", po_file_name
    po = polib.pofile(po_file_name)
    for entry in po.translated_entries():
        print >> source_doc, entry.msgid.encode('utf-8')
        print >> target_doc, entry.msgstr.encode('utf-8')

def extract_translated_entries():
    if len(sys.argv) <= 1:
        print "Usage: python", ' '.join(sys.argv), "path/to/*.po"
        return

    path = sys.argv[1]
    if not os.path.exists(path):
        print path, "doesn't exsit"
        return

    if os.path.isfile(path):
        return

    # path is a directory now
    print "walking directory", path

    with open("doc.en", "w") as doc_en:
        with open("doc.es", "w") as doc_es:
            # Write parallel sentences into two files
            for root, dirs, files in os.walk(path):
                for filename in files:
                    if filename.endswith(".po"):
                        write_po_file(doc_en, doc_es, os.path.join(root,
                            filename))


def main():
    extract_translated_entries()

if __name__ == "__main__":
    main()

