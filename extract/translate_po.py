import polib
import sys
import os.path
import structures
from translate_docs import translate_doc

####################################
# This module translates a directory of po files
# It takes the directory, writes the source language to a file, then translates that to another file, and then writes that out in the same order as it ingested the directory
# It translates the untranslated entries and empties the translated ones to isolate the machine translated ones
# Thus it is important not to change the directory structure mid running this program
# Usage: python translate_po.py config_train.yaml path/to/old/*.po path/to/new/*.po
# MAKE SURE TO COPY THE DIRECTORY OF PO FILES BEFORE TRANSLATING THEM, this is both for backup and also because the translated po files are meant to be an unapproved intermediary, not a final product
######################################



def write_text_file(text_doc,po_file):
    print "processing", po_file
    po = polib.pofile(po_file)
    for entry in po.untranslated_entries():
        text_doc.write(entry.msgid.encode('utf-8')+'\n')

def extract_untranslated_entries(old_path):

    if not os.path.exists(old_path):
        print old_path, "doesn't exsit"
        return

    # path is a directory now
    print "walking directory", old_path

    #extract entries into temp
    open("temp","w").close()
    with open("temp", "a") as temp:
        if os.path.isfile(old_path):
            write_text_file(temp, old_path)
            return
        # Write parallel sentences into two files
        for root, dirs, files in os.walk(old_path):
            for filename in files:
                if filename.endswith(".po"):
                    write_text_file(temp,  os.path.join(root,filename))


#Fill po file with translated lines
def fill_target(target_po_file, translated_lines, start):

    po = polib.pofile(target_po_file)
    i=-1
    for entry in po:
        if not entry.translated():
            i=i+1
            entry.msgstr = unicode(translated_lines[start+i].strip(), "utf-8")
        if entry.translated():
            entry.msgstr = ""

    # Save translated po file.
    po.save(po_file)
    return start+i+1

def translate_po(old_path, new_path, config):
    extract_untranslated_entries(old_path)
    trans_fn=translate_doc("temp",config)
    start=0

    with open(trans_fn, "r") as trans:
        trans_lines=trans.readlines()

    if os.path.isfile(new_path):
        fill_target(new_path,trans_lines, start)
        return

    # fill in the directories in same order as they were read
    for root, dirs, files in os.walk(new_path):
        for filename in files:
            if filename.endswith(".po"):
                start=fill_target(os.path.join(root,filename), trans_lines, start)
    

def main():
    if len(sys.argv) <= 1:
        print "Usage: python", ' '.join(sys.argv), "config path/to/old/*.po path/to/new/*.po"
        return
    y=structures.BuildConfiguration(sys.argv[1])
    translate_po(sys.argv[2], sys.argv[3], y)

if __name__ == "__main__":
    main()

