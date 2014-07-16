import sys
import shutil
import structures
import os
from  bash_command import command
import logging

'''
This module takes a config files and a pot file and translates the pot file
Usage: python translate_docs.py config_train.yaml /path/to/file protected
'''
logger = logging.getLogger('translate_docs')
logging.basicConfig(level=logging.DEBUG)

def pcommand(c):
    '''This function wraps the command module with code for logging
    :Parameters:
        - 'c': command to run and log
    :Returns:
        - list of lists of configuration arguments
    '''
    logger.info(c)
    o=command(c)
    logger.info(o.out)
    logger.info(o.err)
    return o

def decode(in_file,out_file,  y, protected_file):
    '''This function translates a given file to another file
    :Parameters:
        - 'in_file': file to be translated 
        - 'out_file': filename to be translated to 
        - 'y': yaml configuration dictionary 
        - 'protected_file': regex file to protect expressions from tokenization
    '''
    logger.info("decoding: " + in_file)
    if protected_file is not None:
        pcommand("{0}/scripts/tokenizer/tokenizer.perl -l en < {1} > {1}.tok.en -threads {2} -protected {3}".format(y.moses_path, in_file, y.threads, protected_file))
    else:
        pcommand("{0}/scripts/tokenizer/tokenizer.perl -l en < {1} > {1}.tok.en -threads {2}".format(y.moses_path, in_file, y.threads))
    pcommand("{0}/scripts/recaser/truecase.perl --model {1}/truecase-model.en < {2}.tok.en > {2}.true.en".format(y.moses_path, y.helper_dir, in_file))
    pcommand("{0}/bin/moses -f {1}/{4}/working/binarised-model/moses.ini < {2}.true.en > {3}.true".format(y.moses_path,y.model_path, in_file, out_file, y.best_run))
    pcommand("{0}/scripts/recaser/detruecase.perl < {1}.true > {1}.tok".format(y.moses_path, out_file))
    pcommand("{0}/scripts/tokenizer/detokenizer.perl -l en < {1}.tok > {1}".format(y.moses_path, out_file))
    logger.info("translated") 
 
def translate_doc(fn, config, protected_file=None):
    '''This function translates the file
    :Parameters:
        - 'fn': file to be translated 
        - 'config': yaml configuration dictionary 
    '''
    new_fn = fn + ".translated"
    decode(fn, new_fn, config, protected_file)
    return new_fn
    
def main():
    if len(sys.argv) < 3:
        print "Usage: python", ' '.join(sys.argv), "config_train.yaml /path/to/file protected_file"
        return    

    y = structures.BuildConfiguration(sys.argv[1])
    if len(sys.argv) == 3:
        translate_doc(sys.argv[2], y)
    elif len(sys.argv) == 4:
        translate_doc(sys.argv[2], y, sys.argv[3])

if __name__ == "__main__":
    main()       