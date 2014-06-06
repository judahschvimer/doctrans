corpus: data used for training

LM: language model built from training data

demo: demo used for skunkworksdata used for training

working: home of translation engine

translate: scripts to generate test data and translations

This may be of help http://www.statmt.org/moses_steps.html
This also may be of help http://lintaka.wordpress.com/2014/01/17/installing-moses-decoder-on-ubuntu/

Step 1:
Follow instructions here: http://www.statmt.org/moses/?n=Development.GetStarted
Install all dependencies as described at the bottom of the document using apt-get if on Ubuntu
Make sure g++ and Boost are also installed as described in the document
Clone Moses from Github
To install it, ensure that Moses uses the correct Boost package

Step 2:
Install IRSTLM as explained here: http://lintaka.wordpress.com/2014/01/15/installing-irstlm-on-ubuntu/
In code, make sure that when you call “export IRSTLM=...” you direct it to the proper location
Install Moses again with IRSTLM
./bjam --with-irstlm=/usr/local/src/irstlm -j12

Step 3:
Install MGIZA as described here: http://www.statmt.org/moses/?n=Moses.ExternalTools#ntoc3
If not already installed, you may need to install cmake for this to work
Make a tools/ directory in mosesdecoder and put all of the files in the mgiza bin/ directory in it
also include merge_alignment.py abd sbt2cooc.pl rom the mgiza scripts/ directory
Finally if it doesn’t work, try to add a file called snt2cooc.out with the following in it:
${0%/*}/snt2cooc /dev/stdout $1
$2 $3

Step 4:
Scrape MongoDB docs for Spanish text
https://github.com/deafgoat/doctrans/blob/master/extract/pull_test.py
The above does so, though make sure to run extract_translated_entries() rather than extract_source()
Move the corpus folder from doctrans to ~/corpus
You will also need to move the output files from above, doc.en and doc.es, to ~/corpus/training

Step 5:
Whenever running build_model.sh, make sure directories ~/lm and ~/working do not already exist or build_model.sh will complain

Step 6:
Make sure when using the “--text” flag (as described in the directions) to NOT say “--text yes” and to only say “--text”

Step 7: 
When running, run with bash, not just sh








