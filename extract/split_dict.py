import sys
import re
import logging

'''
This module is useful for taking a dictionary file from http://www.dicts.info/uddl.php and parsing it into a parallel corpus
Usage python split_dict.py dictfile sourceFile targetFile
'''

logger = logging.getLogger('views')
logging.basicConfig(level=logging.DEBUG)

def split_dict(dict_fn, source_fn, target_fn):
     '''This function splits a dictionary in half 
    :Parameters:
        - 'dict_fn': dictionary file  
        - 'source_fn': source filename 
        - 'target_fn': target file name 
    '''
     with open(dict_fn, "r") as dict_f:
        with open(source_fn, "w",1) as source_f:
            with open(target_fn, "w",1) as target_f:
                for line in dict_f:
                    if line[0] == '#':
                        continue
                    halves = re.split(r'\t+', line)
                    if len(halves) < 2:
                        continue          
                    source_words = re.split(r';', halves[0])       
                    target_words = re.split(r';', halves[1])
                    for target_word in target_words:
                        target_word=target_word.strip()
                        for source_word in source_words:
                            source_word = source_word.strip()
                            source_f.write(source_word)
                            source_f.write("\n")
                            target_f.write(target_word)
                            target_f.write("\n")
    

def main():
    if len(sys.argv) !=  4:
        print("Usage: python split_dict.py <dictFile> <sourceFile> <targetFile>")
        sys.exit()
    split_dict(sys.argv[1], sys.argv[2], sys.argv[3])

if __name__ == "__main__":
    main()