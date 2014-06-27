#binarise the model (if tuned)
rm -rf ~/working/binarised-model
mkdir ~/working/binarised-model
cd ~/working
~/mosesdecoder/bin/processPhraseTable  -ttable 0 0 train/model/phrase-table.gz -nscores 5 -out binarised-model/phrase-table
~/mosesdecoder/bin/processLexicalTable -in train/model/reordering-table.hier-mslr-bidirectional-fe.gz -out binarised-model/reordering-table
cp ~/working/mert-work/moses.ini ~/working/binarised-model
sed -i 's/PhraseDictionaryMemory/PhraseDictionaryBinary/' ~/working/binarised-model/moses.ini
sed -i 's/train\/model\/phrase-table.gz/binarised-model\/phrase-table/' ~/working/binarised-model/moses.ini
sed -i 's/train\/model\/reordering-table.hier-mslr-bidirectional-fe.gz/binarised-model\/reordering-table/' ~/working/binarised-model/moses.ini

~/mosesdecoder/bin/moses  -f  ~/working/binarised-model/moses.ini | ~/mosesdecoder/scripts/recaser/detruecase.perl