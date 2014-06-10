# tokenisation
~/mosesdecoder/scripts/tokenizer/tokenizer.perl -l en < ~/corpus/kde4/kde4.es-en.en > ~/corpus/kde4.es-en.tok.en -threads 12

~/mosesdecoder/scripts/tokenizer/tokenizer.perl -l es < ~/corpus/kde4/kde4.es-en.es > ~/corpus/kde4.es-en.tok.es -threads 12

# train truecaser and make truecase model based on corpus
~/mosesdecoder/scripts/recaser/train-truecaser.perl --model ~/corpus/truecase-model.en --corpus ~/corpus/kde4.es-en.tok.en

~/mosesdecoder/scripts/recaser/train-truecaser.perl --model ~/corpus/truecase-model.es --corpus ~/corpus/kde4.es-en.tok.es

# truecase the corpus
~/mosesdecoder/scripts/recaser/truecase.perl --model ~/corpus/truecase-model.en < ~/corpus/kde4.es-en.tok.en > ~/corpus/kde4.es-en.true.en

~/mosesdecoder/scripts/recaser/truecase.perl --model ~/corpus/truecase-model.es < ~/corpus/kde4.es-en.tok.es > ~/corpus/kde4.es-en.true.es

# truncate sentence length to 80 chars
~/mosesdecoder/scripts/training/clean-corpus-n.perl ~/corpus/kde4.es-en.true es en ~/corpus/kde4.es-en.clean 1 80

# create lm
rm -rf ~/lm
mkdir ~/lm
cd ~/lm
# add sentance boundary symbols and create sb file
~/irstlm/add-start-end.sh < ~/corpus/kde4.es-en.true.es > kde4.es-en.sb.es
export IRSTLM=/usr/local/lib/irstlm;
# generate language model into an iARPA file
~/irstlm/build-lm.sh -i kde4.es-en.sb.es -t ./tmp -p -s improved-kneser-ney -o kde4.es-en.ilm.es.gz

# create ARPA from iARPA
~/irstlm/compile-lm --text  kde4.es-en.ilm.es.gz kde4.es-en.arpa.es

# binarize ARPA file for faster use
~/mosesdecoder/bin/build_binary kde4.es-en.arpa.es kde4.es-en.blm.es

# test the language model
echo "Is this a Spanish sentance?" | ~/mosesdecoder/bin/query /home/judah/lm/kde4.es-en.blm.es

#######################################
#  training the translation engine    #
#                           10:52     #
#######################################
rm -rf ~/working
mkdir ~/working
cd ~/working
#trains the model with the parameters as explained in the readme in parallel
nohup nice -n 15 time ~/mosesdecoder/scripts/training/train-model.perl -root-dir train -corpus ~/corpus/kde4.es-en.clean -f en -e es --score-options '--GoodTuring'  -alignment grow-diag-final-and -reordering hier-mslr-bidirectional-fe -lm 0:3:$HOME/lm/kde4.es-en.blm.es:8 -mgiza -external-bin-dir $HOME/mosesdecoder/tools  -cores 12 --parallel --parts 3 2>&1 > training.out; mail -s "Training Done" judah.schvimer@mongodb.com <<< "Training the model is Done"  &


######################################
#  tuning the engine                 #
######################################
cd ~/corpus
~/mosesdecoder/scripts/tokenizer/tokenizer.perl -l es < training/skunkworks.es-en.es > skunkworks.es-en.tok.es -threads 12
~/mosesdecoder/scripts/tokenizer/tokenizer.perl -l en < training/skunkworks.es-en.en > skunkworks.es-en.tok.en -threads 12

~/mosesdecoder/scripts/recaser/truecase.perl --model truecase-model.es < skunkworks.es-en.tok.es > skunkworks.es-en.true.es
~/mosesdecoder/scripts/recaser/truecase.perl --model truecase-model.en < skunkworks.es-en.tok.en > skunkworks.es-en.true.en

cd ~/working
nohup nice -n 15 time ~/mosesdecoder/scripts/training/mert-moses.pl ~/corpus/skunkworks.es-en.true.en ~/corpus/skunkworks.es-en.true.es ~/mosesdecoder/bin/moses --decoder-flags="-threads 12" train/model/moses.ini --mertdir ~/mosesdecoder/bin/ 2>&1 > mert.out; mail -s "Tuning Done" judah.schvimer@mongodb.com <<< "Tuning the model is done" &

<<COMMENT1
# binarising the model (if untuned)
mkdir ~/working/binarised-model
cd ~/working
~/mosesdecoder/bin/processPhraseTable  -ttable 0 0 train/model/phrase-table.gz -nscores 5 -out binarised-model/phrase-table
~/mosesdecoder/bin/processLexicalTable -in train/model/reordering-table.wbe-msd-bidirectional-fe.gz -out binarised-model/reordering-table
cp ~/working/train/model/moses.ini ~/working/binarised-model
sed -i 's/PhraseDictionaryMemory/PhraseDictionaryBinary/' ~/working/binarised-model/moses.ini
sed -i 's/train\/model/binarized-model/' ~/working/binarised-model/moses.ini
COMMENT1

# binarise the model (if tuned)
mkdir ~/working/binarised-model
cd ~/working
~/mosesdecoder/bin/processPhraseTable  -ttable 0 0 train/model/phrase-table.gz -nscores 5 -out binarised-model/phrase-table
~/mosesdecoder/bin/processLexicalTable -in train/model/reordering-table.wbe-msd-bidirectional-fe.gz -out binarised-model/reordering-table
cp ~/working/mert-work/moses.ini ~/working/binarised-model
sed -i 's/PhraseDictionaryMemory/PhraseDictionaryBinary/' ~/working/binarised-model/moses.ini
sed -i 's/mert-work/binarized-model/' ~/working/binarised-model/moses.ini

~/mosesdecoder/bin/moses  -f  ~/working/train/model/moses.ini