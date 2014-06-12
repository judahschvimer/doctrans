#tokenisation
~/mosesdecoder/scripts/tokenizer/tokenizer.perl -l en < ~/corpus/training/skunkworks.es-en.en > ~/corpus/skunkworks.es-en.tok.en -threads 12

~/mosesdecoder/scripts/tokenizer/tokenizer.perl -l es < ~/corpus/training/skunkworks.es-en.es > ~/corpus/skunkworks.es-en.tok.es -threads 12

# train truecaser and make truecase model based on corpus
~/mosesdecoder/scripts/recaser/train-truecaser.perl --model ~/corpus/truecase-model.en --corpus ~/corpus/skunkworks.es-en.tok.en

~/mosesdecoder/scripts/recaser/train-truecaser.perl --model ~/corpus/truecase-model.es --corpus ~/corpus/skunkworks.es-en.tok.es

# truecase the corpus
~/mosesdecoder/scripts/recaser/truecase.perl --model ~/corpus/truecase-model.en < ~/corpus/skunkworks.es-en.tok.en > ~/corpus/skunkworks.es-en.true.en

~/mosesdecoder/scripts/recaser/truecase.perl --model ~/corpus/truecase-model.es < ~/corpus/skunkworks.es-en.tok.es > ~/corpus/skunkworks.es-en.true.es

# truncate sentence length to 80 chars
~/mosesdecoder/scripts/training/clean-corpus-n.perl ~/corpus/skunkworks.es-en.true es en ~/corpus/skunkworks.es-en.clean 1 80

# create lm
rm -rf ~/lm
mkdir ~/lm
cd ~/lm
#add sentance boundary symbols and create sb file
~/irstlm-5.80.03/bin/add-start-end.sh < ~/corpus/skunkworks.es-en.true.es > skunkworks.es-en.sb.es
export IRSTLM=/home/judah/irstlm-5.80.03;
#generate language model into an iARPA file
~/irstlm-5.80.03/bin/build-lm.sh -i skunkworks.es-en.sb.es -t ./tmp -p -s improved-kneser-ney -o skunkworks.es-en.lm.es

# create ARPA from iARPA
~/irstlm-5.80.03/bin/compile-lm --text  skunkworks.es-en.lm.es.gz skunkworks.es-en.arpa.es

# binarize ARPA file for faster use
~/mosesdecoder/bin/build_binary skunkworks.es-en.arpa.es skunkworks.es-en.blm.es

# test the language model
echo "Is this a Spanish sentance?" | ~/mosesdecoder/bin/query /home/judah/lm/skunkworks.es-en.blm.es

#######################################
#  training the translation engine    #
#                           10:52     #
#######################################
rm -rf ~/working
mkdir ~/working
cd ~/working
#
nohup nice -n 15 time ~/mosesdecoder/scripts/training/train-model.perl -root-dir train -corpus ~/corpus/skunkworks.es-en.clean -f en -e es --score-options '--GoodTuring'  -alignment grow-diag-final-and -reordering hier-mslr-bidirectional-fe -lm 0:3:$HOME/lm/skunkworks.es-en.blm.es:1 -mgiza -external-bin-dir $HOME/mosesdecoder/tools  -cores 12 --parallel --parts 3 2>&1 training.out


#binarising the model (if untuned)
rm -rf ~/working/binarised-model
mkdir ~/working/binarised-model
cd ~/working
~/mosesdecoder/bin/processPhraseTable  -ttable 0 0 train/model/phrase-table.gz -nscores 5 -out binarised-model/phrase-table
~/mosesdecoder/bin/processLexicalTable -in train/model/reordering-table.hier-mslr-bidirectional-fe.gz -out binarised-model/reordering-table
cp ~/working/train/model/moses.ini ~/working/binarised-model
sed -i 's/PhraseDictionaryMemory/PhraseDictionaryBinary/' ~/working/binarised-model/moses.ini
sed -i 's/train\/model/binarised-model/' ~/working/binarised-model/moses.ini

~/mosesdecoder/bin/moses  -f  ~/working/binarised-model/moses.ini | ~/mosesdecoder/scripts/recaser/detruecase.perl