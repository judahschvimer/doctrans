#tokenisation
~/mosesdecoder/scripts/tokenizer/tokenizer.perl -l en < ~/corpus/dictTrain/kde4.es-en.en > ~/corpus/kde4.es-en.tok.en -threads 12

~/mosesdecoder/scripts/tokenizer/tokenizer.perl -l es < ~/corpus/dictTrain/kde4.es-en.es > ~/corpus/kde4.es-en.tok.es -threads 12

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
~/irstlm-5.80.03/bin/add-start-end.sh < ~/corpus/kde4.es-en.true.es > kde4.es-en.sb.es
export IRSTLM=/home/judah/irstlm-5.80.03;
# generate language model into an iARPA file
~/irstlm-5.80.03/bin/build-lm.sh -i kde4.es-en.sb.es -t ./tmp -p -s improved-kneser-ney -o kde4.es-en.ilm.es.gz

# create ARPA from iARPA
~/irstlm-5.80.03/bin/compile-lm --text  kde4.es-en.ilm.es.gz kde4.es-en.arpa.es

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
nohup nice -n 15 time ~/mosesdecoder/scripts/training/train-model.perl -root-dir train -corpus ~/corpus/kde4.es-en.clean -f en -e es --score-options '--GoodTuring'  -alignment grow-diag-final-and -reordering hier-mslr-bidirectional-fe -lm 0:3:$HOME/lm/kde4.es-en.blm.es:1 -mgiza -external-bin-dir $HOME/mosesdecoder/tools  -cores 12 --parallel --parts 3 2>&1 > training.out; mail -s "Training Done" judah.schvimer@mongodb.com <<< "Training the model is Done"  &
echo "Training finishing up"
