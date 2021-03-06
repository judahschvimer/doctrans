# Translation Pipeline

### Giza Commands


- build model
  - `giza translate build_translation_model --config <translate.yaml>`
  - `giza translate bm -c <translate.yaml>`
  - These commands create a translation model with the configuration taken from the translate.yaml config.
  - First create some some empty directory that the script should run in. Specify that as the "project_path" in the config.
  - Then create (or resuse) a directory that the auxilary corpus files (the tokenized fies , truecased files, etc.) should be written to. Specify that as the "aux_corpus_files" in the config.
  - Additionally, specify the paths to the top most mosesdecoder directory and the topmost irstlm directory
  - Next create your corpora. This should be one file in the source language and one in the target language for training, tuning, and testing. You can't use multiple corpora with Moses easily.
    - These could be individual corpora such as KDE4 or Europarl, or they could be hybrid ones
    - The create_corpora script can be used to create good hubrid corpora. See its documentation for how to use it.
    - Specify the paths to the training, tuning and testing directories. The source and target language files training should be together, the files for tuning should be together, and the files for testing should be together. The three sets can have different directories though. The source and target language files for each should have the same name except for the final extensions. For example: in testdir/ you'd have test.es-en.en and test.es-en.es. When specifying the name in the config, leave off the final language extension.
  - Specify your run settings.
    - Threads is the number of threads for multi-threaded moses/irstlm/mgiza commands in any given process. Pool_size is the number of processes that build_model will run at once.
    - phrase_table_name and reordering_name are a bit trickier. In general they are 'phrase_table' and 'reordering_table' in some cases- mainly when doing factorized or OSM models- this name changes to something like `phrase_table.0-0,1`. This would be found under `project/0/working/train/model`. As such you can't actually know exactly what the answer is before you run it. Usually this will just cause an error late in the script (around tuning or testing) and you'll have to fix the name at then rerun the whole script or those sections if you feel like editing the initial script. 
  - Specify your training_parameters. If you know what you want to run you can just make a simple yaml attribute. If you make a list, as shown in the example, it will run all combinations of the parameters in parallel using as many processes as the pool-size allows. 
  - Run the build model command in the background. Expect it to take a long time. It should email you if it succeeds, however make sure to monitor if the process is still running. `ps aux | grep 'moses'` usually does the trick. 
  - Look at `data.csv` in the project directory to get the results from the test. The highest BLEU score is the best result. 
  - To see a sample from the model, look at `project/0/working/test.en-es.translate.es` (note es will be your target language).
- create corpora
  - `giza translate create_corpora --config <corpora.yaml>`
  - `giza translate cc -c <corpora.yaml>`
  - These commands create training, tuning, and testing corpora from mutliple different input corpora
  - The first thing to do is create the config file.
    - The container_path is the path to the directory that the corpora will be placed in. If you provide just a name then a directory of that name will be placed in the current directory.
    - The source section specifies what percentage of a given file goes to each of training, testing, tuning. You provide the name and the path to the corpus and then the percentages that go into each. The percentages must add up to 100. 
    - The source contributions section specifices the percentage of each corpus that comes from each of the files. create_corpora finds the minimum total length of the corpus such that all of the lines are used at least once. If one corpus has sa higher percentage than it has lines, its lines get repeated, emphasizing them more. For example, say `f1` is 100 lines, and under sources we allocate 60% to training. Let's say create_corpora finds that the training corpus should be 200 lines and the source_contributions says `f1` should comprise 80% of that corpus. Thus 160 lines need to be taken from `f1`, so `f1`'s first 60 lines will be put in twice and then we still need to put in 40 more lines so we'll add the first 40 lines in one more time. 
    - Create corpora creates both languages at the same time, you must specify the paths to each and the script verifies that they are the same length.
  - After creating the config just run the command and move the container wherever you'd like if you didn't specify it correctly off the bat.
- merge translations
  - `giza translate merge_translations --output <output_file> --input <input_file1> <input_file2> ...`
  - `giza translate mt -o <output_file> -i <input_file1> <input_file2> ...`
  - These comamnds merge two files together line by line. This is useful for looking at different translations of the same file line by line next to each other.
  - It annotates each line so that the user can better line things up.
  - To use it just specify an output file and a list of input files.
    - The input files don't have to be the same length but it'll stop when it gets to the bottom of the shortest file.
    - Currently it only works with 14 files because of the number of default annotations. If you want to use more files than that, just go into the operations file and add more annotations manually.
  - If you want to compare multiple models, or compare a model to a "correct" translation, or compare a model to the source language, this is the easiest way to visualize it.
- po to corpus
  - `giza translate po_to_corpus --po <path_to_po_files> --source <path_for_source_lang_corpus> --target <path_for_target_lang_corpus>`
  - `giza translate p2c --po <path_to_po_files> -s <path_for_source_lang_corpus> -t <path_for_target_lang_corpus>`
  - These commands are used for creating corpora from po files
  - If you have po files that have been translated by a person and are reliable these will parse through them and write them out line by line to parallel files.
  - The source and target flags are used for specifying the output files. They are optional and if left off will use default files.
  - If you have po files that are translated I highly recommend using them as corpora since they are the best data you could possibly have and are the most similar to the sentences you'll be translating.
- dict to corpus
  - `giza translate dict_to_corpus --dict <path_to_dictionary> --source <path_for_source_lang_corpus> --target <path_for_target_lang_corpus>`
  - `giza translate d2c --dict <path_to_dictionary> -s <path_for_source_lang_corpus> -t <path_for_target_lang_corpus>`
  - These commands will turn a dictionary into a corpus
  - This can be good for trying to fill in words that don't get translated, though adding dictionaries is not so effective as there are no actual phrases
  - Dictionaries for this script can be gotten at http://www.dicts.info/uddl.php . 
  - This command works almost identically to po_to_corpus, though it doens't work for multiple input files.
- translate text doc 
  - `giza translate translate_text_doc --config <translate.yaml> --source <file_to_translate> --target <filename_after_translation> --protected <protected_regex_file>`
  - `giza translate tdoc -c <translate.yaml> -s <file_to_translate> -t <filename_after_translation> -p <protected_regex_file>`
  - These commands will translate any file according to the model specified by the provided (or default) config.
  - The file will be translated line by line, so it is primarily meant for text documents that are just text line after line, however obviously it could "translate" any other structured file
  - The source is the file to translate, the target is the name of the file after translation.
  - If there are regexes that you don't want to tokenize, --protected will handle them for you.
    - This is good for not translating file names or urls.
    - They will still be translated, but their tokens won't be separated off. Thus most likely if you have a special character in a word like a \` or a < it will probably not be translated as it will have no precedent.
- translate po
  - `giza translate translate_po --config <translate.yaml> --po <po_files_to_translate> --protected <protected_regex_file>`
  - `giza translate tpo -c <translate.yaml> --po <po_files_to_translate> -p <protected_regex_file>`
  - These commands work just like translate text doc, but rather than translating one text doc they can translate one or more po files
  - Just provide a link to a po file or a directory of them and it will traverse them all and translate them all. 
  - The po files will be translated in place so it's important to copy them beforehand. Moreover, the already translated entries will be emptied.
    - This is intentional as it makes it so every translation has a known source. It would be bad if we conflated human translations with machine translations. This way each set has a consistent source.



### Modules

- demo: bash scripts  used for training, tuning, and running the translator
  - `build_model.py`: builds a tranlsation model given a config file
  - `create_corpora.py`: creates train, tune, and test corpora given a config file
  - `datamine.py`: goes through log of experiemnts and creates a csv file with the config and results
  - `merge_trans.py`: merges as many files as you want into one file alternating lines from each, good for comparing translations
  - `translate_docs.py`: translates a document with the moses decoder. Supply a protected.re file to not tokenize some regular expressions.
  - `translate_po.py`: translates a po file or directory of po files
  - `protected.re`: This file lists a set of regex's that the tokenizer will not tokenize. URLs and paths are good things to put in here. The regex `<*.>` (and any that replace < with another character(s)) will protect anything that is found between two angle brackets. This doesn't need to be used when running tests on your model, just when actually translating documents.
  - `po_to_corpus.py`: pulls words from the po files in the mongo docs
  - `split_dict.py`: splits dictionaries from http://www.dicts.info/uddl.php into parallel corpora

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

Step 3:
Install MGIZA as described here: http://www.statmt.org/moses/?n=Moses.ExternalTools#ntoc3
If not already installed, you may need to install cmake for this to work
Make a tools/ directory in mosesdecoder and put all of the files in the mgiza `bin/` directory in it
also include `merge_alignment.py` and `sbt2cooc.pl` from the mgiza `scripts/` directory
Install Moses with IRSTLM, boost, 
`./bjam --with-boost=/home/judah/boost_1_55_0 --with-irstlm=/home/judah/irstlm-5.80.03 --with-giza=/home/judah/mgizapp-code/mgizapp/bin -j12 -a -q`

### Workflow

1. Setup Moses, Giza, and IRSTLM as described above
2. Setup your corpora
  1. Use more data for better results, preferably data similar to the documents you will be translating from
  2. Plan out the train, tune, and test corpora, with almost all data going to train. To do this first find as many parallel corpora as you want out of which you will create your train, tune, and test corpora
  3. If you have any translations in po files, use `po_to_corpus.py` to pull the data out to use as parallel corpora
  4. Use` create_corpora.py` to make your corpora. You will need to first create a `config_corpora.yaml` file similar to the sample one provided specifying how much of each file goes into train, tune, and test respectively and how much of the train, tune, and test copora will have lines from each file. Note that this second part means that the train, tune, or test corpora may have multiple copies of some input corpora.
  5. Put the same data in multiple times (or make it a higher percentage of the train, tune, or test corpus in `create_corpora.py`) to weight it higher. For example, if you have sentences in po files that you know are good and relevant to your domain, these may be the best data you have and should be correspondingly waited higher. Alternatively, unless you're creating a translater for parliamentary data, the europarl corpus should probably have a low weight so your translations do not sound like parliamentary proceedings
3. Build your model
  1. Decide what configurations to test and run `build_model.py` with an appropriate config file modeled off of the sample `config_train.yaml` which shows all of the possible settings. Perusing the Moses website will explain a bit more about every setting, but in general most settings either perform faster or perform better. Ones that seem to "do less"- such as by using fewer scoring options, considering only one direction, or considering smaller phrases or words- likely will finish faster but will perform worse. 
  2. Wait a while (and read a good book!) while the test runs
  3. At the end of the test look at the out.csv file for the data on how well each configuration did, the BLEU score is the metric you want to look at
4. Translate your docs
  1. Use `translate_po.py` to translate your po files.
  2. First copy the files so you have a parallel directory tree, and give `translate_po.py` one of them to translate
5. Put your docs in MongoDB
  1. Use `po_to_mongo.py` to move the data into MongoDB
  2. Run this once for every "type" of translation you have. (i.e. Moses, Person1, Person2....), this will make the status and the username correct
6. Run the verifier
  1. Run the verifier web app and have people contribute to it
7. Take the approved data from the verifier
  1. Copy doc directory tree to back it up
  2. Use `mongo_to_po.py` to copy approved translations into the new doc directory tree
  3. This will inject the approved translations into all of the untranslated sentences
  
Information about the different configuration options can best be found in the Moses documentation:
http://www.statmt.org/moses/?n=FactoredTraining.TrainingParameters
http://www.statmt.org/moses/?n=FactoredTraining.BuildReorderingModel
http://www.statmt.org/moses/?n=FactoredTraining.AlignWords
http://www.statmt.org/moses/?n=Moses.AdvancedFeatures
http://www.statmt.org/moses/?n=FactoredTraining.ScorePhrases

To use `build_model.py` do the following:
Make sure that the config variables in the config file  pointing to the corpora and files are all correct
Create an empty directory for the run files to go into and point to it as the archive_path at the top of the script
Put all of the flags you want to run with (to run once just make all lists only have 1 or 0 items) in the lists in the config

The `structures.py` and `bash_command.p`y files were written by Sam Kleinman and are useful for reading yaml files and wrapping bash commands in python respectively

### Notes

When running any moses .sh files, run with bash, not just sh

To test, go into the working/train/ folder and run:
`grep ' document ' model/lex.f2e | sort -nrk 3 | head`

Get KDE4 corpus from here, it's a mid-size corpus filled with technical sentences:
http://opus.lingfil.uu.se/KDE4.php

These scripts, especailly the tuning and training phases, can take a long time. Take proper measures to background your processes so that they do not get killed part way.
`nohup`- makes sure that training is not interrupted when done over SSH 
`nice`- makes sure the training doens't hold up the entire computer. run with `nice -n 15`
### Explanation of Moses scripts

- **Tokenizing**
  - Tokenizing is splitting every meaningful linguistic object into a new word. This primarily separates off punctuation as it's own "word" and escaping special characters
  - Running this with the `-protected` flag willmark certain tokens to not be split off.
  - After translation use the detokenizer to replace escaped characters with their original form. It does not get rid of the extra spacing added, so use `-protected` where this becomes an issue.
- **Truecasing**
  - Trucasing is the process of turning all words to a standard case. For most words this means making them lower case, but for others, like MongoDB, it keeps them capitalized but in a standard form. After translation you must go back through (recasing) and make sure the capitalization is correct for the language used. The truecaser first needs to be trained to create the truecase-model before it can be used. The trainer counts the number of times each word is in each form and chooses the most common one as the standard form.
- **Cleaning**
  - Cleaning removes long and empty sentances which can cause problems and mis-alignment. Numbers at the end of the commandare minimum line size and maximum line size: `clean-corpus-n.perl CORPUS L1 L2 OUT MIN MAX`
- **Language Model**
  - The Language model ensures fluent output, so it is built with the target language in mind. Perplexity is a measure of how probable the language model is. IRSTLM computes the perplexity of the test set. The language model counts n-gram frequencies and also estimates smoothing parameters.
    - `add-start-end.sh`: adds sentance boundary symbols to make it easier to parse. This creates the `.sb` file.
    - `build-lm.sh`: generates the language model. `-i` is the input `.sb` file, `-o` is the output LM file, `-t` is a directory for temp files, `-p` is to prune singleton n-grams, `-s` is the smoothing method, `-n` is the order of the language model (typically set to 3). The output theoretically is an iARPA file with a `.ilm.gz` extension, though moses says to use `.lm.es`. This step may be run in parallel with `build-lm-qsub.sh` 
    - `compile-lm`: turns the iARPA into an ARPA file. It appears you need the `--text` flag alone (as opposed to `--text yes`) to make it work properly. 
    - `build_binary`: binarizes the ARPA file so it's faster to use
    - More info on IRSTLM here: http://hermes.fbk.eu/people/bertoldi/teaching/lab_2010-2011/img/irstlm-manual.pdf
    - Make sure to export the irstlm environment variable either in your `.bash_profile` or in the code itself `export IRSTLM=/home/judah/irstlm-5.80.03`
- **Training**
  - Training teaches the model how to make good translations. This uses the MGIZA++ word alignment tool which can be run multi-threaded. A factored translation model taking into account parts of speech could improve training though it makes the process more complicated and makes it take longer.
    - `-f` is the "foreign language" which is the source language
    - `-e` is the "english language" which is the target language. This comes from the convention of translating INTO english, not out of as we are doing.
    - `--parts n` allows training on larger corpora, 3 is typical
    - `--lm factor:order:filename:type`
      - `factor` = factor that the model is modeling. There are separate models for word, lemma, pos, morph
      - `order` = n-gram size
      - `type` = the type of language model used. 1 is for IRSTLM, 8 is for KenLM.
    - `--score-options` used to score phrase translations with different metrics. `--GoodTuring` is good, the other options could make it run faster but make performance suffer
    - For informationa about the reordering model, see here: http://www.statmt.org/moses/?n=FactoredTraining.BuildReorderingModel
- **Tuning**
  - Tuning changes the weights of the difference scores in the moses.ini file. Tuning takes a long time and is best to do with small tuning corpora as a result. It is best to tune on sentences VERY similar to those you are actually trying to translate.  
- **Binarize the model**
  - This makes the decoder load the model faster and thus the decoder starts faster. It does not speed up the actual decoding process
    - `-ttable` refers to the size of the phrase table. For a standard configuration just use 0 0.
    - `-nscores` is number of scores used in translation table, to find this, open `phrase-table.gz` (first use gunzip to unzip it), and then count how many scores there are at the end.
    - `sed` searches and replaces
    - NOTE: The extensions are purposefully left off of the replacements done by sed. This is the way moses intends for it to be used.
- **Testing the model**
  - Running just uses the `moses` script and takes in the `moses.ini` file. If the model was filtered, binarised, or tuned, the "most recent" `moses.ini` file should be used.
  - `detruecase.perl`: recapitalizes the beginnings of words appropriately
  - `detokenizer.perl`: fixes up the tokenization by replacing escaped characters with the original character
  - Use `mail -s "{subject}" {email} <<< "{message}"`  to find out when long running processes are done running 
