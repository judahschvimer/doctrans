
# tokenisation
~/mosesdecoder/scripts/tokenizer/tokenizer.perl -l en < ~/corpus/demo.es-en.en > ~/corpus/demo.es-en.tok.en -threads 16

# truecasing
~/mosesdecoder/scripts/recaser/train-truecaser.perl --model ~/corpus/truecase-model.en --corpus ~/corpus/demo.es-en.tok.en

# recasing
~/mosesdecoder/scripts/recaser/truecase.perl --model ~/corpus/truecase-model.en < ~/corpus/demo.es-en.tok.en > ~/corpus/demo.es-en.true.en

# run decoder
nohup nice ~/mosesdecoder/bin/moses -f ~/working/train/model/moses.ini < ~/corpus/demo.es-en.true.en > ~/working/translated.en 2>&1 > ~/working/translation.out &
~/mosesdecoder/scripts/generic/multi-bleu.perl -lc ~/corpus/demo.es-en.true.en < ~/working/translation.out