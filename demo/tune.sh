######################################
#tuning the engine                 #
######################################
cd ~/corpus
~/mosesdecoder/scripts/tokenizer/tokenizer.perl -l es < training/skunkworks.es-en.es > skunkworks.es-en.tok.es -threads 12
~/mosesdecoder/scripts/tokenizer/tokenizer.perl -l en < training/skunkworks.es-en.en > skunkworks.es-en.tok.en -threads 12

~/mosesdecoder/scripts/recaser/truecase.perl --model truecase-model.es < skunkworks.es-en.tok.es > skunkworks.es-en.true.es
~/mosesdecoder/scripts/recaser/truecase.perl --model truecase-model.en < skunkworks.es-en.tok.en > skunkworks.es-en.true.en

cd ~/working
nohup nice -n 15 time ~/mosesdecoder/scripts/training/mert-moses.pl ~/corpus/skunkworks.es-en.true.en ~/corpus/skunkworks.es-en.true.es ~/mosesdecoder/bin/moses  train/model/moses.ini --mertdir ~/mosesdecoder/bin/ 2>&1 > mert.out; mail -s "Tuning Done" judah.schvimer@mongodb.com <<< "Tuning the model is done" &
echo "Tuning in progress"