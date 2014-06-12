cd ~/corpus
 ~/mosesdecoder/scripts/tokenizer/tokenizer.perl -l en < eval/newstest2009.en > newstest2009.tok.en -threads 12
 ~/mosesdecoder/scripts/tokenizer/tokenizer.perl -l es < eval/newstest2009.es > newstest2009.tok.es -threads 12
 ~/mosesdecoder/scripts/recaser/truecase.perl --model truecase-model.en < newstest2009.tok.en > newstest2009.true.en
 ~/mosesdecoder/scripts/recaser/truecase.perl --model truecase-model.es < newstest2009.tok.es > newstest2009.true.es

cd ~/working
~/mosesdecoder/scripts/training/filter-model-given-input.pl filtered-newstest2009 mert-work/moses.ini ~/corpus/newstest2009.true.en -Binarizer ~/mosesdecoder/bin/processPhraseTable

nohup nice -n 15 ~/mosesdecoder/bin/moses -f ~/working/filtered-newstest2009/moses.ini  < ~/corpus/newstest2009.true.en > ~/working/newstest2009.translated.es 2> ~/working/newstest2009.out 

#-lc means lower case
 ~/mosesdecoder/scripts/generic/multi-bleu.perl -lc ~/corpus/newstest2009.true.es < ~/working/newstest2009.translated.es
