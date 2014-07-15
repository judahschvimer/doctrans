# Translation Pipeline

### Modules

- demo: bash scripts  used for training, tuning, and running the translator
  - Up to date
    - build_model.py: builds a tranlsation model given a config file
    - create_corpora.py: creates train, tune, and test corpora given a config file
    - datamine.py: goes through log of experiemnts and creates a csv file with the config and results
    - merge_trans.py: merges as many files as you want into one file alternating lines from each, good for comparing translations
    - merge_trane_two.py: same as merge_trans but optimized for two files and annotates the lines
    - translate_docs.py: translates a document with the moses decoder
    - translate_po.py: translates a po file or directory of po files
  - Old (deprecated, but still available):
    - build_model_filter.py: same as build_model.py but also filters the data (make sure it's made up to date if used) 
    - build_model.sh: fully builds a model
    - setup_corpus.sh: sets up the corpora
    - train.sh: trains the model on the corpus in your home directory
    - tune.sh: tunes the model on the corpus in your home directory
    - runTuned.sh: binarizes the files and runs the decoder if the model has been tuned
    - runUntuned.sh: binarizes the files and runs the decoder if the model has not been tuned
    - eval.sh: tests a translation model
    - translate.sh: translates a file with the moses decoder
    - translate_docs_m.py: attempts to use the moses python interface to translate docs. The interface is not complete enough to work yet
- extract: python scripts to extract words for corpora
  - po_to_corpus.py: pulls words from the po files in the mongo docs
  - split_dict.py: splits dictionaries from http://www.dicts.info/uddl.php into parallel corpora

### Setup

This may be of help http://www.statmt.org/moses_steps.html
This also may be of help http://lintaka.wordpress.com/2014/01/17/installing-moses-decoder-on-ubuntu/

Step 1:
Follow instructions here: http://www.statmt.org/moses/?n=Development.GetStarted
Install all dependencies as described at the bottom of the document using apt-get if on Ubuntu
Make sure g++ and Boost are also installed as described in the document
Clone Moses from Github
To install it, ensure that Moses uses the correct Boost package

Step 2:
Install this IRSTLM: http://sourceforge.net/projects/irstlm/ (5.80.03)
Follow these directions: http://www.statmt.org/moses/?n=FactoredTraining.BuildingLanguageModel#ntoc4
In code, make sure that when you call “export IRSTLM=...” you direct it to the proper location
Install Moses with IRSTLM, boost,  and with link=shared so that the python interface works
./bjam --with-boost=/home/judah/boost_1_55_0 --with-irstlm=/home/judah/irstlm-5.80.03 --with-giza=/home/judah/mgizapp-code/mgizapp/bin -j12 -a -q

Step 3:
Install MGIZA as described here: http://www.statmt.org/moses/?n=Moses.ExternalTools#ntoc3
If not already installed, you may need to install cmake for this to work
Make a tools/ directory in mosesdecoder and put all of the files in the mgiza bin/ directory in it
also include merge_alignment.py abd sbt2cooc.pl from the mgiza scripts/ directory

### Workflow

1. Setup Moses, Giza, and IRSTLM as described above
2. Setup your corpora
  1. Use more data for better results, preferably data similar to the documents you will be translating from
  2. Create train, tune, and test corpora, with almost all data going to train
  3. Use create_corpora.py to get good corpora, if you have any translations in po files, use po_to_corpus.py to pull the data out
  4. Put the same data in multiple times (or make it a higher percentage in create_corpora.py) to weight it higher
3. Build your model
  1. Decide what configurations to test and run build_model.py with the appropriate configuration
  2. Wait a while while the test runs
  3. At the end of the test look at the out.csv file for the data on how well each configuration did, the BLEU score is the metric you want to look at
4. Translate your docs
  1. Use translate_po.py to translate your po files.
  2. First copy the files so you have a parallel directory tree, and give translate_po.py one of them to translate
5. Put your docs in MongoDB
  1. Use po_to_mongo.py to move the data into MongoDB
  2. Run this once for every "type" of translation you have. (i.e. Moses, Person1, Person2....), this will make the status and the username correct
6. Run the verifier
  1. Run the verifier web app and have people contribute to it
7. Take the approved data from the verifier
  1. Copy doc directory tree to back it up
  2. Use mongo_to_po.py to copy approved translations into the new doc directory tree
  3. This will inject the approved translations into all of the untranslated sentences
  

To use build_model.py do the following:
Make sure that the config variables in the config file  pointing to the corpora and files are all correct
Create an empty directory for the run files to go into and point to it as the archive_path at the top of the script
Put all of the flags you want to run with (to run once just make all lists only have 1 or 0 items) in the lists in the config

The structures.py and bash_command.py files were written by Sam Kleinman and are useful for reading yaml files and wrapping bash commands in python respectively

### Notes

When running any moses .sh files, run with bash, not just sh

To test, go into the working/train/ folder and run:
grep ' document ' model/lex.f2e | sort -nrk 3 | head

If you want to use EMS:
Follow this: http://www.statmt.org/moses/?n=FactoredTraining.EMS
sudo apt-get install imagemagick libmagickcore-dev
wget gv to install ghostview. Follow the Install readme for how to install. You may need xaw3gd, which you can get as shown below:
sudo apt-get install xaw3dg-dev

Get KDE4 from here:
http://opus.lingfil.uu.se/KDE4.php

### Stuff To Know

Tokenizing- splitting every meaningful linguistic object into a new word. This primarily separates off punctuation
Truecasing- the process of turning everything to a standard case. For most words this means making them lower case, but for others, like MongoDB, it keeps them capitalized but in a standard form. After translation you must go back through (recasing) and make sure the capitalization is correct for the language used. The truecaser first needs to be trained to create the truecase-model before it can be used. The trainer counts the number of times each word is in each form and chooses the most common one as the standard form.

Cleaning- removes long and empty sentances which can cause problems and mis-alignment. Numbers at end are minimum line size and maximum line size: clean-corpus-n.perl CORPUS L1 L2 OUT MIN MAX

Language Model- ensures fluent output, so it is built with the target language in mind. Perplexity is a measure of how probable the language model is. IRSTLM computes the perplexity of the test set. The language model counts n-gram frequencies and also estimates smoothing parameters.
    add-start-end.sh: adds sentance boundary symbols to amke it easier to parse. This creates the sb file.
    build-lm.sh: generates the language model. -i is the input sb file, -o is the output  LM file, -t is a directory for temp files, -p is to prune singleton n-grams, -s is the smoothing method, -n is the order of the language model. The output theoretically is an iARPA file with a .ilm.gz extension, though moses says to use .lm.es. This step may be run in parallel with build-lm-qsub.sh 
    compile-lm.sh: turns the iARPA into an ARPA file. It appears you need the --text flag alone (with no yes after it) to make it work properly. 
    build_binary: binarizes the arpa file so it's faster to use
    More info on IRSTLM here: http://hermes.fbk.eu/people/bertoldi/teaching/lab_2010-2011/img/irstlm-manual.pdf
    MAKE SURE TO ADD export IRSTLM=/home/judah/irstlm-5.80.03 TO YOUR .bash_profile, or write that every time you run it

Training- teaches the model how to make good translations. This uses the MGIZA++ word alignment tool which can be run multi-threaded. Want to use a factored translation model since they perform better and take into account parts of speech. Translation step on the phrasal level and then generation step on the word level to choose the right word in the target langauge.
    nohup- makes sure that training is not interrupted when done over SSH
    nice- makes sure the training doens't hold up the entire computer. run with "nice -n 15"
    -f is the "foreign language" which is the source language
    -e is the "english language" which is the target language. This comes from the convention of translating INTO english, not out of as we are doing.
    --parts n allows training on larger corpora, 3 is typical
    --lm factor:order:filename:type
    factor= factor that the model is modeling. There are separate models for word, lemma, pos, morph
    order= n-gram size
    type=  the type of language model used. 1 is for IRSTLM, 8 is for KenLM.
    --score-options used to score phrase translations with different metrics. goodturing is a good one
    the reordering model is important. a hierarchical model was shown in some studies to be the most accurate

Tuning- changes the weights in the moses.ini file. Takes forever and best to do on a small sample size. you can do either batch tuning which is easy or you can do online tuning where decoded sentances are used for tuning which is a bit more difficult.

Binarize the model-This makes it load the model faster and the decoder starts faster
    -ttable for a standard configuration just use 0 0
    -nscores number of scores used in translation table, to find this, open phrase-table.gz (first use gunzip to unzip it), and then count how many scores there are at the end.
    sed searches and replaces
    note that the extensions are purposefully left off of the replacements doen by sed.

Running at the end is just one line. 
Use the detruecase.perl script to capitalize the beginnings of words appropriately
detruecase.perl < in > out [--headline SGML]
Use the detokenizer.perl script to fix up the tokenization

Use mail -s "Tuning Done" judah.schvimer@mongodb.com <<< "Tuning the model is done"  to find out when long running processes are done running 

### Other Info

TreeTagger:
Part of Speech Tagger that works well with moses
Follow Directions here:
http://www.statmt.org/moses/?n=Moses.ExternalTools#ntoc10
http://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/#Linux
Commands should be made similar to below, certain files may have to be renamed to work: TreeTagger/lib/english-utf8.par should become TreeTagger/lib/english.par, just name appropriate files as it asks for them:
~/mosesdecoder/scripts/training/wrappers/make-factor-pos.tree-tagger.perl -tree-tagger ~/TreeTagger -l en  ~/corpus/tuning/mongo-docs-tune.es-en.en  ~/mongopos
~/mosesdecoder/scripts/training/combine_factors.pl ~/corpus/tuning/mongo-docs-tune.es-en.en mongopos > combined

Syntactic Parser:
The Michael Collins one works well with Moses, get it here:
 mkdir collins/
 cd collins/
 wget http://people.csail.mit.edu/mcollins/PARSER.tar.gz
 tar xzf PARSER.tar.gz
 cd COLLINS-PARSER/code
 make
