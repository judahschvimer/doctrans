import sys
import polib 
import shutil
import structures
import os
from  bash_command import command

def pcommand(c):
    print(c)
    o=command(c)
    print(o.out)
    print(o.err)

def decode(q, y):
    print("decoding: " + q)
    c=command("{0}/bin/moses -f {1}/0/working/binarised-model/moses.ini | {0}/scripts/recaser/detruecase.perl <<< \"{2}\"".format(y.moses_path,y.model_path, q))
    print("translation: " + c.out)
    return c.out 

def translate_doc(po_fn, y):
    binarise_model(y)
    shutil.copy(po_fn, "/home/judah")
    po=polib.pofile("/home/judah/{0}".format(os.path.basename(po_fn)))
    for e in po:
        e.msgstr=decode(e.msgid, y)
    po.save()

def binarise_model(y):
    pcommand("mkdir -p {0}/0/working/binarised-model".format(y.model_path))
    pcommand("{0}/bin/processPhraseTable  -ttable 0 0 {1}/0/working/train/model/{2}.gz -nscores 5 -out {1}/0/working/binarised-model/phrase-table".format(y.moses_path,y.model_path,y.phrase_table_name))
    pcommand("{0}/bin/processLexicalTable -in {1}/0/working/train/model/{6}.{2}-{3}-{4}-{5}.gz -out {1}/0/working/binarised-model/reordering-table".format(y.moses_path,y.model_path,y.reordering_modeltype[0], y.reordering_orientation[0],y.reordering_directionality[0],y.reordering_language[0], y.reordering_name))
    pcommand("cp {0}/0/working/mert-work/moses.ini {0}/0/working/binarised-model".format(y.model_path))
    pcommand("sed -i 's/PhraseDictionaryMemory/PhraseDictionaryBinary/' {0}/0/working/binarised-model/moses.ini".format(y.model_path))
    pcommand("sed -i 's/train\/model\/{1}.gz/binarised-model\/phrase-table/' {0}/0/working/binarised-model/moses.ini".format(y.model_path, y.phrase_table_name))
    pcommand("sed -i 's/train\/model\/reordering-table.{0}-{1}-{2}-{3}.gz/binarised-model\/reordering-table/' {4}/0/working/binarised-model/moses.ini".format(y.reordering_modeltype[0], y.reordering_orientation[0],y.reordering_directionality[0],y.reordering_language[0], y.model_path))
 
def main():
    y=structures.BuildConfiguration(sys.argv[1])
    translate_doc("/home/judah/adocs/locale/pot/about.pot", y)

if __name__ == "__main__":
    main()       