import sys
sys.path.append('/home/judah/mosesdecoder/contrib/python/')
from moses.dictree import load # load abstracts away the choice of implementation by checking the available files
import polib 
import shutil
import structures
import os


def query(q, table): 

    result = table.query(q)
    # you could simply print the matches
    # print '\n'.join([' ||| '.join((q, str(e))) for e in matches])
    # or you can use their attributes
    print result.source
    for e in result:
        if e.lhs:
            print "1"
            print '\t%s -> %s ||| %s ||| %s' % (e.lhs, 
                    ' '.join(e.rhs), 
                    e.scores, 
                    e.alignment)
        else:
            print "2"
            print '\t%s ||| %s ||| %s' % (' '.join(e.rhs), 
                    e.scores, 
                    e.alignment)
    return result

def translate_doc(po_fn, phrase_table_name, nscores):
    shutil.copy(po_fn, "/home/judah")
    po=polib.pofile("/home/judah/{0}".format(os.path.basename(po_fn)))
    table = load(phrase_table_name, nscores, 1)
    for e in po:
        #r=query(e.msgid, table)
        #print(len(r))
        # e.msgstr=r[0].lhs
    po.save()
     
def main():
    y=structures.BuildConfiguration(sys.argv[1])
    translate_doc("/home/judah/adocs/locale/pot/about.pot", "{0}/0/working/filtered-mongo-docs-test.es-en/{1}".format(y.model_path,y.phrase_table_name), 5)

if __name__ == "__main__":
    main()       