import sys
import shutil
import structures
import os
from  bash_command import command

###########################
# This module takes a config files and a pot file and translates the pot file
# Usage: python translate_docs.py config_train.yaml /path/to/po
#########################

def pcommand(c):
    print(c)
    o=command(c)
    print(o.out)
    print(o.err)
    return o

def decode(in_file,out_file,  y):
    print("decoding: " + in_file)
    pcommand("{0}/scripts/tokenizer/tokenizer.perl -l en < {1} > {1}.tok.en -threads {2}".format(y.moses_path, in_file, y.threads))
    pcommand("{0}/scripts/recaser/truecase.perl --model {1}/truecase-model.en < {2}.tok.en > {2}.true.en".format(y.moses_path, y.helper_dir, in_file))
    pcommand("{0}/bin/moses -f {1}/{4}/working/binarised-model/moses.ini < {2}.true.en | {0}/scripts/recaser/detruecase.perl > {3}.tok".format(y.moses_path,y.model_path, in_file, out_file, y.best_run))
    pcommand("{0}/scripts/detokenizer.perl -l en < {1}.tok > {1}".format(y.moses_path, out_file))
    print("translated") 
 
def translate_doc(fn, config):
    new_fn=fn+".translated"
    decode(fn, new_fn, config)
    return new_fn
    
def main():
    y=structures.BuildConfiguration(sys.argv[1])
    translate_doc(sys.arv[2], y)

if __name__ == "__main__":
    main()       