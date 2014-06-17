import sys
import os
import time
import itertools
import datetime
import multiprocessing
from bash_command import command

foreign = "es"
threads = "2"
pool_size = 30
corpora_path =  "/home/judah/corpus"
train_name = "kde4.{0}-en".format(foreign) 
training_path ="{0}/training/{1}".format(corpora_path,train_name) 
tune_name = "mongo-docs-tune.{0}-en".format(foreign) 
tuning_path ="{0}/tuning/{1}".format(corpora_path,tune_name)
test_name = "mongo-docs-test.{0}-en".format(foreign) 
testing_path ="{0}/testing/{1}".format(corpora_path,test_name)
moses_path = "/home/judah/mosesdecoder"
irstlm_path = "/home/judah/irstlm-5.80.03" 
archive_path = "/home/judah/archive"

order = ["3"]
smoothing = ["improved-kneser-ney"]
score_options = ["--GoodTuring"]
alignment = [ "grow-diag-final-and"]
reordering_modeltype = [ "wbe", "phrase", "hier"]
reordering_orientation = [ "mslr", "msd", "monotonicity", "leftright"]
reordering_directionality = ["bidirectional", "backward", "forward"] 
reordering_language = ["fe", "f"]
max_phrase_length = ["7"]
log_file=open("{0}/LOG.txt".format(archive_path), "w", 1)

def pcommand(c, log):  
    log.write(c+"\n")
    o=command(c)
    log.write(o.out+"\n")
    log.write(o.err+"\n")
    return o

def log(curr_file, message):
    curr_file.write(message+"\n")
    log_file.write(message+"\n")

def tokenize_corpus(corpus_path, token_path):
    pcommand("{0}/scripts/tokenizer/tokenizer.perl -l en < {1}.en > {2}.tok.en -threads {3}".format(moses_path, corpus_path, token_path, threads), log_file)
    pcommand("{0}/scripts/tokenizer/tokenizer.perl -l en < {1}.{3} > {2}.tok.{3} -threads {4}".format(moses_path, corpus_path,token_path, foreign, threads), log_file)    


def train_truecaser(token_path):
    pcommand("{0}/scripts/recaser/train-truecaser.perl --model {1}/truecase-model.en --corpus {2}.tok.en".format(moses_path, corpora_path, token_path), log_file)
    pcommand("{0}/scripts/recaser/train-truecaser.perl --model {1}/truecase-model.{3} --corpus {2}.tok.{3}".format(moses_path, corpora_path, token_path, foreign), log_file)
     
def truecase_corpus(token_path):
    pcommand("{0}/scripts/recaser/truecase.perl --model {1}/truecase-model.en < {2}.tok.en > {2}.true.en".format(moses_path, corpora_path, token_path), log_file)
    pcommand("{0}/scripts/recaser/truecase.perl --model {1}/truecase-model.{3} < {2}.tok.{3} > {2}.true.{3}".format(moses_path, corpora_path, token_path, foreign), log_file)

def clean_corpus(token_path):
    pcommand("{0}/scripts/training/clean-corpus-n.perl {1}.true {2} en {1}.clean 1 80".format(moses_path, token_path, foreign), log_file)

def setup_train():
    tokenize_corpus(training_path, "{0}/{1}".format(corpora_path, train_name))
    train_truecaser("{0}/{1}".format(corpora_path, train_name))
    truecase_corpus("{0}/{1}".format(corpora_path, train_name))   
    clean_corpus("{0}/{1}".format(corpora_path, train_name))

def setup_tune():
    tokenize_corpus(tuning_path,  "{0}/{1}".format(corpora_path, tune_name))
    truecase_corpus("{0}/{1}".format(corpora_path, tune_name))

def setup_test():
    tokenize_corpus(testing_path, "{0}/{1}".format(corpora_path, test_name))
    truecase_corpus("{0}/{1}".format(corpora_path, test_name)) 

def run_config(l_len, l_order, l_lang, l_direct, l_score, l_smoothing, l_align, l_orient, l_model,  i):
  
    i=str(i)
    run_start=time.time();
    
    c=command("mkdir {0}/{1}".format(archive_path,i))
    print(c.out)
    print(c.err)

    
    i_log = open("{0}/{1}/{1}.ilog.txt".format(archive_path,i),"w",1)
    c_log = open("{0}/{1}/{1}.clog.txt".format(archive_path,i),"w",1)
    
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
    lm_path = "{0}/{1}/lm".format(archive_path,i)
    pcommand("mkdir {0}".format(lm_path), c_log)
    pcommand("{0}/bin/add-start-end.sh < {1}/{2}.true.{3} > {4}/{2}.sb.{3}".format(irstlm_path, corpora_path, train_name, foreign, lm_path), c_log)
    pcommand("{0}/bin/build-lm.sh -i {5}/{1}.sb.{4} -t {5}/tmp -p -n {2} -s {3} -o {5}/{1}.ilm.{4}.gz".format(irstlm_path,train_name, l_order, l_smoothing, foreign, lm_path), c_log)
    pcommand("{0}/bin/compile-lm --text  {3}/{1}.ilm.{2}.gz {3}/{1}.arpa.{2}".format(irstlm_path,train_name, foreign, lm_path), c_log)
    pcommand("{0}/bin/build_binary {3}/{1}.arpa.es {3}/{1}.blm.{2}".format(moses_path,train_name, foreign, lm_path), c_log)
    o=pcommand("echo 'Is this a Spanish sentance?' | {0}/bin/query {1}/{2}.blm.{3}".format(moses_path, lm_path, train_name, foreign), c_log)
    log(i_log,"")
    log(i_log, o.out)
    log(i_log, o.err)
    log(i_log, "LM_Time = {0}".format(str(time.time()-lm_start)))
    log(i_log, "LM_Time_HMS = {0}".format(str(datetime.timedelta(seconds=(time.time()-lm_start)))))

    
    #Train the model
    train_start=time.time()
    
    working_path = "{0}/{1}/working".format(archive_path,i)
    
    pcommand("mkdir {0}".format(working_path), c_log)
    pcommand("{0}/scripts/training/train-model.perl -root-dir {15}/train -corpus {1}/{2}.clean -f en -e {3} --score-options \'{4}\' -alignment {5} -reordering {6}-{7}-{8}-{9} -lm 0:{10}:{11}/{12}.blm.{13}:1 -mgiza -mgiza-cpus {14} -external-bin-dir {0}/tools -cores {14} --parallel --parts 3 2>&1 > {15}/training.out".format(moses_path, corpora_path, train_name, foreign, l_score, l_align, l_model, l_orient, l_direct, l_lang, l_order, lm_path, train_name, foreign, threads, working_path), c_log)
    log(i_log, "Train_Time = {0}".format(str(time.time()-lm_start)))
    log(i_log, "Train_Time_HMS = {0}".format(str(datetime.timedelta(seconds=(time.time()-lm_start)))))
    print("trained")
    
    #Tune the model
    tune_start=time.time()
    pcommand("{0}/scripts/training/mert-moses.pl {1}/{2}.true.en {1}/{2}.true.{3} {0}/bin/moses  {4}/train/model/moses.ini --working-dir {4}/mert-work --mertdir {0}/bin/ 2>&1 > {4}/mert.out".format(moses_path, corpora_path, tune_name, foreign, working_path), c_log) 
    log(i_log, "Tune_Time = {0}".format(str(time.time()-tune_start)))
    log(i_log, "Tune_Time_HMS = {0}".format(str(datetime.timedelta(seconds=(time.time()-tune_start)))))
    print("tuned")
    
    #Test the model
    test_start=time.time()
    pcommand("{0}/scripts/training/filter-model-given-input.pl {3}/filtered-{1} {3}/mert-work/moses.ini {2}/{1}.true.en -Binarizer {0}/bin/processPhraseTable".format(moses_path, test_name, corpora_path, working_path), c_log)
    pcommand("{0}/bin/moses -f {1}/filtered-{3}/moses.ini  < {2}/{3}.true.en > {1}/{3}.translated.{4} 2> {1}/{3}.out".format(moses_path, working_path, corpora_path, test_name, foreign), c_log)
    c=pcommand("{0}/scripts/generic/multi-bleu.perl -lc {1}/{2}.true.{4} < {3}/{2}.translated.{4}".format(moses_path, corpora_path, test_name, working_path, foreign), c_log)
    log(i_log, c.out)
    print("tested")
    log(i_log, "Test_Time = {0}".format(str(time.time()-test_start)))
    log(i_log, "Test_Time_HMS = {0}".format(str(datetime.timedelta(seconds=(time.time()-test_start)))))
    log(i_log, "Run_Time_HMS = {0}".format(str(datetime.timedelta(seconds=(time.time()-run_start)))))
    log(i_log, "Done = {0}".format(i))
    i_log.close()
    c_log.close()

# this method unpacks the list of parameters
def run_star(args):
    return run_config(*args)

def main():
    global log_file
    os.environ['IRSTLM'] = irstlm_path
    #setup_train()
    #setup_tune()
    #setup_test()
    
    config=itertools.product(max_phrase_length, order, reordering_language, reordering_directionality, score_options, smoothing, alignment, reordering_orientation, reordering_modeltype)
    config=[list(e) for e in config]
    i=0
    for c in config:
        c.append(i)
        i=i+1
   

    pool=multiprocessing.Pool(processes=pool_size)
    pool_outputs = pool.map(run_star, config)
    pool.close()
    pool.join()
    # run_config(c[0], c[1], c[2], c[3], c[4], c[5], c[6], c[7], c[8],i)
    
    log_file.close()

    

if __name__ == "__main__":
    main()