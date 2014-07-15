import polib
import sys
import os.path
import structures
from translate_docs import translate_doc

'''
This module translates a directory of po files
It takes the directory, writes the source language to a file, then translates that to another file, and then writes that out in the same order as it ingested the directory
It translates the untranslated entries and empties the translated ones to isolate the machine translated ones
Thus it is important not to change the directory structure mid running this program
Usage: python translate_po.py config_train.yaml path/to/*.po 
MAKE SURE TO COPY THE DIRECTORY OF PO FILES BEFORE TRANSLATING THEM, anything that was already translated will be deleted by this, this is intentional
The goal of this module is to make a directory tree with translations ONLY by Moses.
Then those translations can be looked at separately from approved or human translated sentences
'''


def write_text_file(text_doc,po_file):
    '''This function writes a po file out to a text file
    :Parameters:
        - 'text_doc': the text document to write the po file sentences to
        - 'po_file': the po_file to write out 
    :Returns:
        - list of lists of configuration arguments
    '''
    print "processing", po_file
    po = polib.pofile(po_file)
    for entry in po.untranslated_entries():
        text_doc.write(entry.msgid.encode('utf-8')+'\n')

def extract_untranslated_entries(path):
    '''This function extracts all of the untranslated entries in the directory structure
    :Parameters:
        - 'path': the path to the top directory of the docs
    '''

    if not os.path.exists(path):
        print path, "doesn't exsit"
        return

    # path is a directory now
    print "walking directory", path

    #extract entries into temp
    open("temp","w").close()
    with open("temp", "a") as temp:
        if os.path.isfile(path):
            write_text_file(temp, path)
            return
        # Write parallel sentences into two files
        for root, dirs, files in os.walk(path):
            for filename in files:
                if filename.endswith(".po"):
                    write_text_file(temp,  os.path.join(root,filename))


def fill_target(target_po_file, translated_lines, start):
    '''Fills a new po file with the translated lines
    :Parameters:
        - 'target_po_file': the path to the current po file
        - 'translated_lines': the translations of the po file sentences
        - 'start': the starting line  of the file
    :Returns:
        - The start of the sentences for the next file
    '''

    po = polib.pofile(target_po_file)
    i = -1
    for entry in po:
        if entry.translated() is False:
            i += 1
            entry.msgstr = unicode(translated_lines[start+i].strip(), "utf-8")
        else:
            entry.msgstr = ""

    # Save translated po file.
    po.save(target_po_file)
    return start + i + 1

def translate_po(path, config):
    ''' first extracts the entries, then translates them, and then fills in all of the files
    :Parameters:
        - 'path': the path to the top level directory of the po_files
        - 'sconfig': yaml configuration dictionary
    '''
    extract_untranslated_entries(path)
    trans_fn = translate_doc("temp",config)
    start = 0

    with open(trans_fn, "r") as trans:
        trans_lines = trans.readlines()

    if os.path.isfile(path):
        fill_target(new_path,trans_lines, start)
        return

    # fill in the directories in same order as they were read
    for root, dirs, files in os.walk(path):
        for filename in files:
            if filename.endswith(".po"):
                start = fill_target(os.path.join(root,filename), trans_lines, start)
    

def main():
    if len(sys.argv) != 3:
        print "Usage: python", ' '.join(sys.argv), "config path/to/*.po"
        return
    y = structures.BuildConfiguration(sys.argv[1])
    translate_po(sys.argv[2],  y)

if __name__ == "__main__":
    main()

