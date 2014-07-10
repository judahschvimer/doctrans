import sys
import os
import time
import itertools
import datetime
import multiprocessing
import yaml
import structures
import datamine
import logging
from bash_command import command

######################
# This module builds the translation model by training, tuning, and then testing
# It also binarizes the model at the end so that it's faster to load the decoder later on
# Using a config file as shown in the config_train.yaml, you can customize the build and what settings it uses to experiment
# Usage: nohup nice -n 17 python build_model.py config_train.yaml 2>&1 > log.txt &
######################



logging.basicConfig(level=logging.INFO)
logg = logging.getLogger("mylog")
fh = logging.FileHandler('build_model.log')
f = logging.Formatter("%(levelname)s %(asctime)s %(funcName)s %(lineno)d %(message)s")
fh.setFormatter(f)
logg.addHandler(fh)

def pcommand(c, log):
    logg = logging.getLogger("mylog")
    logg.info(c)
    
    log.write(c+"\n")
    o=command(c)
    log.write(o.out+"\n")
    log.write(o.err+"\n")
    logg.info(o.out)
    logg.info(o.err)
    return o

def log(curr_file, message):
    curr_file.write(message+"\n")
    log_file.write(message+"\n")

def tokenize_corpus(corpus_dir, corpus_name,y):
    pcommand("{0}/scripts/tokenizer/tokenizer.perl -l en < {1}/{3}.en > {2}/{3}.tok.en -threads {4}".format(y.moses_path, corpus_dir, y.helper_dir, corpus_name, y.threads), log_file)
    pcommand("{0}/scripts/tokenizer/tokenizer.perl -l en < {1}/{3}.{4} > {2}/{3}.tok.{4} -threads {5}".format(y.moses_path, corpus_dir, y.helper_dir, corpus_name, y.foreign, y.threads), log_file)

def train_truecaser(corpus_name,y):
    pcommand("{0}/scripts/recaser/train-truecaser.perl --model {1}/truecase-model.en --corpus {1}/{2}.tok.en".format(y.moses_path, y.helper_dir, corpus_name), log_file)
    pcommand("{0}/scripts/recaser/train-truecaser.perl --model {1}/truecase-model.{3} --corpus {1}/{2}.tok.{3}".format(y.moses_path, y.helper_dir, corpus_name, y.foreign), log_file)

def truecase_corpus(corpus_name,y):
    pcommand("{0}/scripts/recaser/truecase.perl --model {1}/truecase-model.en < {1}/{2}.tok.en > {1}/{2}.true.en".format(y.moses_path, y.helper_dir, corpus_name), log_file)
    pcommand("{0}/scripts/recaser/truecase.perl --model {1}/truecase-model.{3} < {1}/{2}.tok.{3} > {1}/{2}.true.{3}".format(y.moses_path, y.helper_dir, corpus_name, y.foreign), log_file)

def clean_corpus(corpus_name,y):
    pcommand("{0}/scripts/training/clean-corpus-n.perl {1}/{2}.true {3} en {1}/{2}.clean 1 80".format(y.moses_path, y.helper_dir, corpus_name, y.foreign), log_file)

def setup_train(y):
    tokenize_corpus(y.train_dir, y.train_name, y)
    train_truecaser(y.train_name,y)
    truecase_corpus(y.train_name,y)
    clean_corpus(y.train_name,y)

def setup_tune(y):
    tokenize_corpus(y.tune_dir, y.tune_name,y)
    truecase_corpus(y.tune_name,y)

def setup_test(y):
    tokenize_corpus(y.test_dir, y.test_name,y)
    truecase_corpus(y.test_name,y)

def run_config(l_len, l_order, l_lang, l_direct, l_score, l_smoothing, l_align, l_orient, l_model,  i, y):
    
    model_path=y.model_path
    irstlm_path=y.irstlm_path
    helper_dir=y.helper_dir
    train_name=y.train_name
    foreign=y.foreign
    moses_path=y.moses_path
    threads=y.threads
    tune_name=y.tune_name
    test_name=y.test_name

    i=str(i)
    run_start=time.time();
    lm_path = "{0}/{1}/lm".format(model_path,i)
    working_path = "{0}/{1}/working".format(model_path,i)

    c=command("mkdir {0}/{1}".format(model_path,i))
    print(c.out)
    print(c.err)

    i_log = open("{0}/{1}/{1}.ilog.txt".format(model_path,i),"w",1)
    c_log = open("{0}/{1}/{1}.clog.txt".format(model_path,i),"w",1)

    log(i_log, "i = {0}".format(i));
    log(i_log, "Start_Time = {0}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
    log(i_log, "Order = {0}".format(l_order))
    log(i_log, "Smoothing = {0}".format(l_smoothing))
    log(i_log, "ScoreOptions = {0}".format(l_score))
    log(i_log, "Alignment = {0}".format(l_align))
    log(i_log, "ReorderingModeltype = {0}".format(l_model))
    log(i_log, "ReorderingOrientation = {0}".format(l_orient))
    log(i_log, "ReorderingDirectionality = {0}".format(l_direct))
    log(i_log, "ReorderingLanguage = {0}".format(l_lang))
    log(i_log, "MaxPhraseLength = {0}".format(l_len))
    log(i_log, "")

    #Create language model
    lm_start = time.time()
    pcommand("mkdir {0}".format(lm_path), c_log)
    pcommand("{0}/bin/add-start-end.sh < {1}/{2}.true.{3} > {4}/{2}.sb.{3}".format(irstlm_path, helper_dir, train_name, foreign, lm_path), c_log)
    pcommand("{0}/bin/build-lm.sh -i {5}/{1}.sb.{4} -t {5}/tmp -p -n {2} -s {3} -o {5}/{1}.ilm.{4}.gz".format(irstlm_path,train_name, l_order, l_smoothing, foreign, lm_path), c_log)
    pcommand("{0}/bin/compile-lm --text  {3}/{1}.ilm.{2}.gz {3}/{1}.arpa.{2}".format(irstlm_path,train_name, foreign, lm_path), c_log)
    pcommand("{0}/bin/build_binary -i {3}/{1}.arpa.es {3}/{1}.blm.{2}".format(moses_path,train_name, foreign, lm_path), c_log)
    o=pcommand("echo 'Is this a Spanish sentance?' | {0}/bin/query {1}/{2}.blm.{3}".format(moses_path, lm_path, train_name, foreign), c_log)
    log(i_log,"")
    log(i_log, o.out)
    log(i_log, o.err)
    log(i_log, "LM_Time = {0}".format(str(time.time()-lm_start)))
    log(i_log, "LM_Time_HMS = {0}".format(str(datetime.timedelta(seconds=(time.time()-lm_start)))))


    #Train the model
    train_start=time.time()

    log(i_log, "Train_Start_Time = {0}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))

    pcommand("mkdir {0}".format(working_path), c_log)
    pcommand("{0}/scripts/training/train-model.perl -root-dir {13}/train -corpus {1}/{2}.clean -f en -e {3} --score-options \'{4}\' -alignment {5} -reordering {6}-{7}-{8}-{9} -lm 0:{10}:{11}/{2}.blm.{3}:1 -mgiza -mgiza-cpus {12} -external-bin-dir {0}/tools -cores {12} --parallel --parts 3 2>&1 > {13}/training.out".format(moses_path, helper_dir, train_name, foreign, l_score, l_align, l_model, l_orient, l_direct, l_lang, l_order, lm_path, threads, working_path), c_log)
    log(i_log, "Train_Time = {0}".format(str(time.time()-lm_start)))
    log(i_log, "Train_Time_HMS = {0}".format(str(datetime.timedelta(seconds=(time.time()-lm_start)))))
    print("trained")

    #Tune the model
    tune_start=time.time()
    log(i_log, "Tune_Start_Time = {0}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
    pcommand("{0}/scripts/training/mert-moses.pl {1}/{2}.true.en {1}/{2}.true.{3} {0}/bin/moses  {4}/train/model/moses.ini --working-dir {4}/mert-work --mertdir {0}/bin/ 2>&1 > {4}/mert.out".format(moses_path, helper_dir, tune_name, foreign, working_path), c_log)
    log(i_log, "Tune_Time = {0}".format(str(time.time()-tune_start)))
    log(i_log, "Tune_Time_HMS = {0}".format(str(datetime.timedelta(seconds=(time.time()-tune_start)))))
    print("tuned")

    #Test the model
    test_start=time.time()
    log(i_log, "Test_Start_Time = {0}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
    pcommand("{0}/scripts/training/filter-model-given-input.pl {3}/filtered {3}/mert-work/moses.ini {2}/{1}.true.en -Binarizer {0}/bin/processPhraseTable".format(moses_path, test_name, helper_dir, working_path), c_log)
    pcommand("{0}/bin/moses -f {1}/filtered/moses.ini  < {2}/{3}.true.en > {1}/{3}.translated.{4} 2> {1}/{3}.out".format(moses_path, working_path, helper_dir, test_name, foreign), c_log)
    c=pcommand("{0}/scripts/generic/multi-bleu.perl -lc {1}/{2}.true.{4} < {3}/{2}.translated.{4}".format(moses_path, helper_dir, test_name, working_path, foreign), c_log)
    log(i_log, c.out)
    print("tested")
    log(i_log, "Test_Time = {0}".format(str(time.time()-test_start)))
    log(i_log, "Test_Time_HMS = {0}".format(str(datetime.timedelta(seconds=(time.time()-test_start)))))

    pcommand("mkdir -p {0}/binarised-model".format(working_path),c_log)
    pcommand("{0}/bin/processPhraseTable  -ttable 0 0 {1}/train/model/{2}.gz -nscores 5 -out {1}/binarised-model/phrase-table".format(moses_path,working_path,y.phrase_table_name), c_log)
    pcommand("{0}/bin/processLexicalTable -in {1}/train/model/{6}.{2}-{3}-{4}-{5}.gz -out {1}/binarised-model/reordering-table".format(moses_path,working_path,l_model, l_orient,l_direct,l_lang, y.reordering_name), c_log)
    pcommand("cp {0}/mert-work/moses.ini {0}/binarised-model".format(working_path), c_log)
    pcommand("sed -i 's/PhraseDictionaryMemory/PhraseDictionaryBinary/' {0}/binarised-model/moses.ini".format(working_path), c_log)
    pcommand("sed -i 's/train\/model\/{1}.gz/binarised-model\/phrase-table/' {0}/binarised-model/moses.ini".format(working_path, y.phrase_table_name), c_log)
    pcommand("sed -i 's/train\/model\/reordering-table.{0}-{1}-{2}-{3}.gz/binarised-model\/reordering-table/' {4}/binarised-model/moses.ini".format(l_model, l_orient,l_direct,l_lang, working_path), c_log)

    log(i_log, "Run_Time_HMS = {0}".format(str(datetime.timedelta(seconds=(time.time()-run_start)))))
    log(i_log, "End_Time = {0}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
    log(i_log, "Done = {0}".format(i))
    i_log.close()
    c_log.close()

# this method unpacks the list of parameters
def run_star(args):
    return run_config(*args)

def get_run_args(y): 
    config=itertools.product(y.max_phrase_length, y.order, y.reordering_language, y.reordering_directionality, y.score_options, y.smoothing, y.alignment, y.reordering_orientation, y.reordering_modeltype)
    config=[list(e) for e in config]
    i=0
    for c in config:
        c.append(i)
        c.append(y)
        i=i+1
    return config

def main():
    y=structures.BuildConfiguration(sys.argv[1])
    config=get_run_args(y)
    
    global log_file
    log_file=open("{0}/LOG.txt".format(y.model_path), "w", 1)
    
    os.environ['IRSTLM'] = y.irstlm_path
    
    setup_train(y)
    setup_tune(y)
    setup_test(y)
    
    pool=multiprocessing.Pool(processes=y.pool_size)
    pool_outputs = pool.map(run_star, config)
    pool.close()
    pool.join()

    log_file.close()
    datamine.write_data(y.model_path)
    command('cat {0}/out.csv | mail -s "Output" {1}'.format(y.model_path, y.email))
    

if __name__ == "__main__":
    main()