#tokenisation
~/mosesdecoder/scripts/tokenizer/tokenizer.perl -l en < ~/corpus/EnEsText/KDE4.en-es.en > ~/corpus/KDE4.es-en.tok.en -threads 12

~/mosesdecoder/scripts/tokenizer/tokenizer.perl -l es < ~/corpus/EnEsText/KDE4.en-es.es > ~/corpus/KDE4.es-en.tok.es -threads 12

# truecasing
~/mosesdecoder/scripts/recaser/train-truecaser.perl --model ~/corpus/truecase-model.en --corpus ~/corpus/KDE4.es-en.tok.en

~/mosesdecoder/scripts/recaser/train-truecaser.perl --model ~/corpus/truecase-model.es --corpus ~/corpus/KDE4.es-en.tok.es

# recasing
~/mosesdecoder/scripts/recaser/truecase.perl --model ~/corpus/truecase-model.en < ~/corpus/KDE4.es-en.tok.en > ~/corpus/KDE4.es-en.true.en

~/mosesdecoder/scripts/recaser/truecase.perl --model ~/corpus/truecase-model.es < ~/corpus/KDE4.es-en.tok.es > ~/corpus/KDE4.es-en.true.es

# truncate sentence length to 80 chars
~/mosesdecoder/scripts/training/clean-corpus-n.perl ~/corpus/KDE4.es-en.true es en ~/corpus/KDE4.es-en.clean 1 80

# create lm
rm -rf ~/lm
mkdir ~/lm
cd ~/lm
~/irstlm/add-start-end.sh < ~/corpus/KDE4.es-en.true.es > KDE4.es-en.sb.es
export IRSTLM=/usr/local/lib/irstlm; ~/irstlm/build-lm.sh -i KDE4.es-en.sb.es -t ./tmp -p -s improved-kneser-ney -o KDE4.es-en.lm.es

# create arpa
~/irstlm/compile-lm --text  KDE4.es-en.lm.es.gz KDE4.es-en.arpa.es

# binarize arpa file
~/mosesdecoder/bin/build_binary KDE4.es-en.arpa.es KDE4.es-en.blm.es

echo "Is this a Spanish sentance?" | ~/mosesdecoder/bin/query /home/judah/lm/KDE4.es-en.blm.es

#######################################
#  training the translation engine    #
#                           10:52     #
#######################################
rm -rf ~/working
mkdir ~/working
cd ~/working
nohup ~/mosesdecoder/scripts/training/train-model.perl -root-dir train -corpus ~/corpus/KDE4.es-en.clean -f en -e es  -alignment grow-diag-final-and -reordering msd-bidirectional-fe -lm 0:3:$HOME/lm/KDE4.es-en.blm.es:8 -mgiza -external-bin-dir $HOME/mosesdecoder/tools  -cores 12 --parallel --parts 3  >& training.out &


######################################
#  tuning the engine                 #
######################################
cd ~/corpus
~/mosesdecoder/scripts/tokenizer/tokenizer.perl -l es < training/skunkworks.es-en.es > skunkworks.es-en.tok.es -threads 12
~/mosesdecoder/scripts/tokenizer/tokenizer.perl -l en < training/skunkworks.es-en.en > skunkworks.es-en.tok.en -threads 12

~/mosesdecoder/scripts/recaser/truecase.perl --model truecase-model.es < skunkworks.es-en.tok.es > skunkworks.es-en.true.es
~/mosesdecoder/scripts/recaser/truecase.perl --model truecase-model.en < skunkworks.es-en.tok.en > skunkworks.es-en.true.en

cd ~/working
nohup nice ~/mosesdecoder/scripts/training/mert-moses.pl ~/corpus/skunkworks.es-en.true.en ~/corpus/skunkworks.es-en.true.es ~/mosesdecoder/bin/moses --decoder-flags="-threads 12" train/model/moses.ini ~mertdir ~mosesdeecoder/bin/ &> mert.out &

# binarising the model
mkdir ~/working/binarised-model
cd ~/working
~/mosesdecoder/bin/processPhraseTable  -ttable 0 0 train/model/phrase-table.gz -nscores 5 -out binarised-model/phrase-table
~/mosesdecoder/bin/processLexicalTable -in train/model/reordering-table.wbe-msd-bidirectional-fe.gz -out binarised-model/reordering-table
cp ~/working/train/model/moses.ini ~/working/binarised-model
sed -i 's/PhraseDictionaryMemory/PhraseDictionaryBinary/' ~/working/binarised-model/moses.ini
sed -i 's/train\/model/binarized-model/' ~/working/binarised-model/moses.ini

~/mosesdecoder/bin/moses  -f  ~/working/train/model/moses.ini 