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