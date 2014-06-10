#tokenisation
~/mosesdecoder/scripts/tokenizer/tokenizer.perl -l en < ~/corpus/training/skunkworks.es-en.en > ~/corpus/skunkworks.es-en.tok.en -threads 12

~/mosesdecoder/scripts/tokenizer/tokenizer.perl -l es < ~/corpus/training/skunkworks.es-en.es > ~/corpus/skunkworks.es-en.tok.es -threads 12

# truecasing
~/mosesdecoder/scripts/recaser/train-truecaser.perl --model ~/corpus/truecase-model.en --corpus ~/corpus/skunkworks.es-en.tok.en

~/mosesdecoder/scripts/recaser/train-truecaser.perl --model ~/corpus/truecase-model.es --corpus ~/corpus/skunkworks.es-en.tok.es

# recasing
~/mosesdecoder/scripts/recaser/truecase.perl --model ~/corpus/truecase-model.en < ~/corpus/skunkworks.es-en.tok.en > ~/corpus/skunkworks.es-en.true.en

~/mosesdecoder/scripts/recaser/truecase.perl --model ~/corpus/truecase-model.es < ~/corpus/skunkworks.es-en.tok.es > ~/corpus/skunkworks.es-en.true.es

# truncate sentence length to 80 chars
~/mosesdecoder/scripts/training/clean-corpus-n.perl ~/corpus/skunkworks.es-en.true es en ~/corpus/skunkworks.es-en.clean 1 80

# create lm
rm -rf ~/lm
mkdir ~/lm
cd ~/lm
~/irstlm/add-start-end.sh < ~/corpus/skunkworks.es-en.true.es > skunkworks.es-en.sb.es
export IRSTLM=/usr/local/lib/irstlm; ~/irstlm/build-lm.sh -i skunkworks.es-en.sb.es -t ./tmp -p -s improved-kneser-ney -o skunkworks.es-en.lm.es

# create arpa
~/irstlm/compile-lm --text  skunkworks.es-en.lm.es.gz skunkworks.es-en.arpa.es

# binarize arpa file
~/mosesdecoder/bin/build_binary skunkworks.es-en.arpa.es skunkworks.es-en.blm.es

echo "Is this a Spanish sentance?" | ~/mosesdecoder/bin/query /home/judah/lm/skunkworks.es-en.blm.es

#######################################
#  training the translation engine    #
#                           10:52     #
#######################################
rm -rf ~/working
mkdir ~/working
cd ~/working
nohup ~/mosesdecoder/scripts/training/train-model.perl -root-dir train -corpus ~/corpus/skunkworks.es-en.clean -f en -e es --score-options '--GoodTuring'  -alignment grow-diag-final-and -reordering msd-bidirectional-fe -lm 0:3:$HOME/lm/skunkworks.es-en.blm.es:8 -mgiza -external-bin-dir $HOME/mosesdecoder/tools  -cores 12 --parallel --parts 3  >& training.out &


######################################
#  tuning the engine                 #
######################################
cd ~/corpus
~/mosesdecoder/scripts/tokenizer/tokenizer.perl -l es < tuning/news-commentary-v8.es-en.es > news-commentary-v8.es-en.tok.es -threads 12
~/mosesdecoder/scripts/tokenizer/tokenizer.perl -l en < tuning/news-commentary-v8.es-en.en > news-commentary-v8.es-en.tok.en -threads 12

~/mosesdecoder/scripts/recaser/truecase.perl --model truecase-model.es < news-commentary-v8.es-en.tok.es > news-commentary-v8.es-en.true.es
~/mosesdecoder/scripts/recaser/truecase.perl --model truecase-model.en < news-commentary-v8.es-en.tok.en >news-commentary-v8.es-en.true.en

cd ~/working
nohup nice ~/mosesdecoder/scripts/training/mert-moses.pl ~/corpus/news-commentary-v8.es-en.true.en ~/corpus/news-commentary-v8.es-en.true.es ~/mosesdecoder/bin/moses --decoder-flags="-threads 12" train/model/moses.ini ~mertdir ~mosesdecoder/bin/ &> mert.out &

# binarising the model
mkdir ~/working/binarised-model
cd ~/working
~/mosesdecoder/bin/processPhraseTable  -ttable 0 0 train/model/phrase-table.gz -nscores 5 -out binarised-model/phrase-table
~/mosesdecoder/bin/processLexicalTable -in train/model/reordering-table.wbe-msd-bidirectional-fe.gz -out binarised-model/reordering-table
cp ~/working/train/model/moses.ini ~/working/binarised-model
sed -i 's/PhraseDictionaryMemory/PhraseDictionaryBinary/' ~/working/binarised-model/moses.ini
sed -i 's/train\/model/binarized-model/' ~/working/binarised-model/moses.ini

~/mosesdecoder/bin/moses  -f  ~/working/train/model/moses.ini 