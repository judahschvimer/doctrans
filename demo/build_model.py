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
import shutil
from bash_command import command

'''
This module builds the translation model by training, tuning, and then testing
It also binarizes the model at the end so that it's faster to load the decoder later on
Using a config file as shown in the config_train.yaml, you can customize the build and what settings it uses to experiment
Best to run this with as many threads as possible
Recommended Usage: nohup nice -n 17 python build_model.py config_train.yaml 2>&1 > log.txt &
'''


class Timer():
    def __init__(self, d, name=None):
        self.d = d
        if name is None:
            self.name = 'task'
        else:
            self.name = name

    def __enter__(self):
        self.start = time.time()
        time_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        self.d[self.name+"_start_time"] = time_now 
        message = '[build] [timer]: {0} started at {1}'
        message = message.format(self.name, time_now)
        logger.info(message)

    def __exit__(self, *args):
        total_time = time.time()-self.start
        message = '[build] [timer]: time elapsed for {0} was: {1}'
        message = message.format(self.name, str(total_time))
        logger.info(message)
        self.d[self.name+"_time"] = total_time
        self.d[self.name+"_time_hms"] = str(datetime.timedelta(seconds=total_time))

class CGLogger(logging.Logger):
    '''This class is responsible for making sure logging works with multiprocessing
    Essentially it starts a stream handler and allows you to switch it out for other handlers
    By switching out the handler in different processes you can have each process handle the log in its own way
    '''
    def __init__(self,name):
        logging.Logger.__init__(self,name)
        self.f = logging.Formatter("%(levelname)s %(asctime)s %(funcName)s %(lineno)d %(processName)s: %(message)s")
        self.mainhandler = logging.StreamHandler(sys.stdout)
        self.mainhandler.setFormatter(self.f)
        self.addHandler(self.mainhandler)

    def stop_main_logging(self):
        self.removeHandler(self.mainhandler)

    def log_to_file(self, fn):
        self.filehandler = logging.FileHandler(fn)
        self.filehandler.setFormatter(self.f)
        self.addHandler(self.filehandler)

    def stop_logging_to_file(self):
        self.removeHandler(self.filehandler)

    def restart_main_logging(self):
        self.addHandler(self.mainhandler)

    def switch_to_file_logging(self, fn):
        self.stop_main_logging()
        self.log_to_file(fn)

    def switch_to_main_logging(self):
        self.stop_logging_to_file()
        self.restart_main_logging(fn)

logging.basicConfig(level=logging.INFO)
logging.setLoggerClass(CGLogger)
logger = logging.getLogger("build_model")

def pcommand(c):
    '''This function wraps the command module with logging functionality
    :Parameters:
        - 'c': command to run and log
        - 'log': log file to log all actions to
    :Returns:
        -  a command result object
    '''
    
    logger.info(c)
    o = command(c)
    if len(o.out) != 0: logger.info(o.out)
    if len(o.err) != 0: logger.info(o.err)
    return o

#def log(curr_file, message):
    '''This function logs a message to the logger, the global log file, and the local log file
    :Parameters:
        - 'curr_file': a local log file for each configuration
        - 'message': the message to log 
    '''
    #curr_file.write(message+"\n")

def tokenize_corpus(corpus_dir, corpus_name,y):
    '''This function tokenizes a corpus
    :Parameters:
        - 'corpus_dir': directory to the corpus
        - 'corpus_name': name of the corpus in the directory
        - 'y': yaml configuration dictionary
    '''
    
    cmd = "{0}/scripts/tokenizer/tokenizer.perl -l en < {1}/{3}.{4} > {2}/{3}.tok.{4} -threads {5}"
    pcommand(cmd.format(y.paths.moses, corpus_dir, y.paths.aux_corpus_files, corpus_name, "en", y.settings.threads))
    pcommand(cmd.format(y.paths.moses, corpus_dir, y.paths.aux_corpus_files, corpus_name, y.settings.foreign, y.settings.threads))

def train_truecaser(corpus_name,y):
    '''This function trains the truecaser on a corpus
    :Parameters:
        - 'corpus_name': name of the corpus in the directory
        - 'y': yaml configuration dictionary
    '''
    cmd = "{0}/scripts/recaser/train-truecaser.perl --model {1}/truecase-model.{3} --corpus {1}/{2}.tok.{3}"
    pcommand(cmd.format(y.paths.moses, y.paths.aux_corpus_files, corpus_name, "en"))
    pcommand(cmd.format(y.paths.moses, y.paths.aux_corpus_files, corpus_name, y.settings.foreign))

def truecase_corpus(corpus_name,y):
    '''This function truecases a corpus
    :Parameters:
        - 'corpus_name': name of the corpus in the directory
        - 'y': yaml configuration dictionary
    '''
    cmd = "{0}/scripts/recaser/truecase.perl --model {1}/truecase-model.{3} < {1}/{2}.tok.{3} > {1}/{2}.true.{3}"
    pcommand(cmd.format(y.paths.moses, y.paths.aux_corpus_files, corpus_name, "en"))
    pcommand(cmd.format(y.paths.moses, y.paths.aux_corpus_files, corpus_name, y.settings.foreign))

def clean_corpus(corpus_name,y):
    '''This function cleans a corpus to have proper length up to 80 words
    :Parameters:
        - 'corpus_name': name of the corpus in the directory
        - 'y': yaml configuration dictionary
    '''
    pcommand("{0}/scripts/training/clean-corpus-n.perl {1}/{2}.true {3} en {1}/{2}.clean 1 80".format(y.paths.moses, y.paths.aux_corpus_files, corpus_name, y.settings.foreign))

def setup_train(y):
    '''This function sets up the training corpus
    :Parameters:
        - 'y': yaml configuration dictionary
    '''
    tokenize_corpus(y.train.dir, y.train.name, y)
    train_truecaser(y.train.name,y)
    truecase_corpus(y.train.name,y)
    clean_corpus(y.train.name,y)

def setup_tune(y):
    '''This function sets up the tuning corpus
    :Parameters:
        - 'y': yaml configuration dictionary
    '''
    tokenize_corpus(y.tune.dir, y.tune.name,y)
    truecase_corpus(y.tune.name,y)

def setup_test(y):
    '''This function sets up the testing corpus
    :Parameters:
        - 'y': yaml configuration dictionary
    '''
    tokenize_corpus(y.test.dir, y.test.name,y)
    truecase_corpus(y.test.name,y)

def run_lm(lm_path,
           l_order, 
           l_smoothing, 
           y,
           d):
    '''This function builds the language model for the goven config 
    :Parameters:
        - 'lm_path': path to language model directory
        - 'l_order': n-gram order
        - 'l_smoothing': smoothing algorithm
        - 'y': yaml configuration dictionary
        - 'd': output dictionary
    ''' 

    # Create language model
    with Timer(d, 'lm'):
        os.makedirs(lm_path)
        pcommand("{0}/bin/add-start-end.sh < {1}/{2}.true.{3} > {4}/{2}.sb.{3}".format(y.paths.irstlm, y.paths.aux_corpus_files, y.train.name, y.settings.foreign, lm_path))
        pcommand("{0}/bin/build-lm.sh -i {5}/{1}.sb.{4} -t {5}/tmp -p -n {2} -s {3} -o {5}/{1}.ilm.{4}.gz".format(y.paths.irstlm, y.train.name, l_order, l_smoothing, y.settings.foreign, lm_path))
        pcommand("{0}/bin/compile-lm --text  {3}/{1}.ilm.{2}.gz {3}/{1}.arpa.{2}".format(y.paths.irstlm, y.train.name, y.settings.foreign, lm_path))
        pcommand("{0}/bin/build_binary -i {3}/{1}.arpa.es {3}/{1}.blm.{2}".format(y.paths.moses,y.train.name, y.settings.foreign, lm_path))
        pcommand("echo 'Is this a Spanish sentance?' | {0}/bin/query {1}/{2}.blm.{3}".format(y.paths.moses, lm_path, y.train.name, y.settings.foreign))
    
def run_train(working_path,
              lm_path,
              l_len,
              l_order,
              l_lang, 
              l_direct, 
              l_score, 
              l_align, 
              l_orient, 
              l_model,  
              y,
              d):
    '''This function does the training for the given configuration 
    :Parameters:
        - 'working_path': path to working directory
        - 'l_order': n-gram order
        - 'l_lang': reordering language setting, either f or fe
        - 'l_direct': reordering directionality setting, either forward, backward, or bidirectional
        - 'l_score': score options setting, any combination of --GoodTuring, --NoLex, --OnlyDirect
        - 'l_align': alignment algorithm
        - 'l_orient': reordering orientation setting, either mslr, msd, monotonicity, leftright
        - 'l_model': reordering modeltype setting, either wbe, phrase, or hier
        - 'y': yaml configuration dictionary
        - 'd': output dictionary
        
    ''' 
    
    with Timer(d, 'train'):
        os.makedirs(working_path)
        pcommand("{0}/scripts/training/train-model.perl -root-dir {13}/train -corpus {1}/{2}.clean -f en -e {3} --score-options \'{4}\' -alignment {5} -reordering {6}-{7}-{8}-{9} -lm 0:{10}:{11}/{2}.blm.{3}:1 -mgiza -mgiza-cpus {12} -external-bin-dir {0}/tools -cores {12} --parallel --parts 3 2>&1 > {13}/training.out".format(y.paths.moses, y.paths.aux_corpus_files, y.train.name, y.settings.foreign, l_score, l_align, l_model, l_orient, l_direct, l_lang, l_order, lm_path, y.settings.threads, working_path))

def run_binarise(working_path, 
                 l_lang, 
                 l_direct, 
                 l_orient, 
                 l_model,  
                 y,
                 d):
    '''This function binarises the phrase and reoridering tables.
    Binarising them speeds up loading the decoder, though doesn't actually speed up decoding sentences
    :Parameters:
        - 'working_path': the path to the working directory
        - 'l_lang': reordering language setting, either f or fe
        - 'l_direct': reordering directionality setting, either forward, backward, or bidirectional
        - 'l_orient': reordering orientation setting, either mslr, msd, monotonicity, leftright
        - 'l_model': reordering modeltype setting, either wbe, phrase, or hier
        - 'y': yaml configuration dictionary
        - 'd': output dictionary
        
    ''' 
    with Timer(d, 'binarise'):
        pcommand("mkdir -p {0}/binarised-model".format(working_path),c_log)
        pcommand("{0}/bin/processPhraseTable  -ttable 0 0 {1}/train/model/{2}.gz -nscores 5 -out {1}/binarised-model/phrase-table".format(y.paths.moses, working_path, y.settings.phrase_table_name))
        pcommand("{0}/bin/processLexicalTable -in {1}/train/model/{6}.{2}-{3}-{4}-{5}.gz -out {1}/binarised-model/reordering-table".format(y.paths.moses, working_path, l_model, l_orient, l_direct, l_lang, y.settings.reordering_name))
        pcommand("cp {0}/mert-work/moses.ini {0}/binarised-model".format(working_path))
        pcommand("sed -i 's/PhraseDictionaryMemory/PhraseDictionaryBinary/' {0}/binarised-model/moses.ini".format(working_path))
        pcommand("sed -i 's/train\/model\/{1}.gz/binarised-model\/phrase-table/' {0}/binarised-model/moses.ini".format(working_path, y.settings.phrase_table_name))


def run_test_filtered(working_path, 
                      y,
                      d):
    '''This function tests the model made so far.
    It first filters the data to only use those needed for the test file.
    This can speed it  up over the binarised version but has a history of failing on certain corpora
    :Parameters:
        - 'd': output dictionary
        - 'y': yaml configuration dictionary
        - 'd': output dictionary
        
    ''' 
    with Timer(d, 'test'):
        pcommand("{0}/scripts/training/filter-model-given-input.pl {3}/filtered {3}/mert-work/moses.ini {2}/{1}.true.en -Binarizer {0}/bin/processPhraseTable".format(y.paths.moses, y.test.name, y.paths.aux_corpus_files, working_path))
        pcommand("{0}/bin/moses -f {1}/filtered/moses.ini  < {2}/{3}.true.en > {1}/{3}.translated.{4} 2> {1}/{3}.out".format(y.paths.moses, working_path, y.paths.aux_corpus_files, y.test.name, y.settings.foreign))
        c = pcommand("{0}/scripts/generic/multi-bleu.perl -lc {1}/{2}.true.{4} < {3}/{2}.translated.{4}".format(y.paths.moses, y.paths.aux_corpus_files, y.test.name, working_path, y.settings.foreign))
        d["BLEU": c.out]
        logger.info(c.out)

def run_test_binarised(working_path, 
                       y,
                       d):
    '''This function tests the model so far with the binarised phrase table 
    :Parameters:
        - 'd': output dictionary
        - 'y': yaml configuration dictionary
        - 'd': output dictionary
        
    ''' 
    with Timer(d, 'test'):
        pcommand("{0}/bin/moses -f {1}/binarised-model/moses.ini  < {2}/{3}.true.en > {1}/{3}.translated.{4} 2> {1}/{3}.out".format(y.paths.moses, working_path, y.paths.aux_corpus_files, y.test.name, y.settings.foreign))
        c = pcommand("{0}/scripts/generic/multi-bleu.perl -lc {1}/{2}.true.{4} < {3}/{2}.translated.{4}".format(y.paths.moses, y.paths.aux_corpus_files, y.test.name, working_path, y.settings.foreign))
        d["BLEU": c.out]
        logger.info(c.out)

def run_config(l_len, 
               l_order, 
               l_lang, 
               l_direct, 
               l_score, 
               l_smoothing, 
               l_align, 
               l_orient, 
               l_model,  
               i, 
               y):
    '''This function runs one configuration of the training script. 
    This function can be called with different arguments to run multiple configurations in parallel
    :Parameters:
        - 'l_len': max phrase length
        - 'l_order': n-gram order
        - 'l_lang': reordering language setting, either f or fe
        - 'l_direct': reordering directionality setting, either forward, backward, or bidirectional
        - 'l_score': score options setting, any combination of --GoodTuring, --NoLex, --OnlyDirect
        - 'l_smoothing': smoothing algorithm
        - 'l_align': alignment algorithm
        - 'l_orient': reordering orientation setting, either mslr, msd, monotonicity, leftright
        - 'l_model': reordering modeltype setting, either wbe, phrase, or hier
        - 'i': configuration number, should be unique for each
        - 'y': yaml configuration dictionary
        
    ''' 

    run_start = time.time();
    lm_path = "{0}/{1}/lm".format(y.paths.project,i)
    working_path = "{0}/{1}/working".format(y.paths.project,i)
    
    os.makedirs("{0}/{1}".format(y.paths.project,i))
    logger.switch_to_file_logging('{0}/{1}/commands.log'.format(y.paths.project, i))
     
    # Logs information about the current configuation
    d = {"i": i, 
         "start_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
         "order": l_order,
         "smoothing": l_smoothing,
         "score_options": l_score,
         "alignment": l_align,
         "reordering_modeltype": l_model,
         "reordering_orientation": l_orient,
         "reordering_directionality": l_direct,
         "reordering_language": l_lang,
         "max_phrase_length": l_len}

    run_lm(lm_path, l_order, l_smoothing, y, d)
    run_train(working_path, lm_path, l_len, l_order, l_lang, l_direct, l_score, l_align, l_orient, l_model, y, d)
    run_binarise(working_path, l_lang, l_direct, l_orient, l_model, y, d)
    run_test_binarised(working_path, y, d)

    d["run_time_hms"] = str(datetime.timedelta(seconds=(time.time()-run_start)))
    d["end_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    with open("{0}/{1}/{1}.json".format(y.paths.project,i),"w",1) as ilog:
        ilog.write(d)    

def run_star(args):
    '''This function unpacks the list of parameters to run the configuration
    :Parameters:
        - 'args': a list of arguments 
    '''
    return run_config(*args)

def get_run_args(y): 
    '''This function creates a list of configuration lists
    :Parameters:
        - 'y': yaml configuration dictionary
    :Returns:
        - list of lists of configuration arguments
    '''
    config = itertools.product( y.parameters.max_phrase_length, 
                                y.parameters.order, 
                                y.parameters.reordering_language, 
                                y.parameters.reordering_directionality, 
                                y.parameters.score_options,
                                y.parameters.smoothing, 
                                y.parameters.alignment, 
                                y.parameters.reordering_orientation, 
                                y.parameters.reordering_modeltype)
    config = [list(e) for e in config]
    i = 0
    for c in config:
        c.append(i)
        c.append(y)
        i += 1
    return config

def main():
    if len(sys.argv) != 2:
        print "Usage: python", ' '.join(sys.argv), "config_train.yaml"
        return
 
    y = structures.BuildConfiguration(sys.argv[1]) 

    config = get_run_args(y)
    shutil.copy(sys.argv[1], y.paths.project)
    os.environ['IRSTLM'] = y.paths.irstlm
    
    #setup_train(y)
    #setup_tune(y)
    #setup_test(y)
    
    pool = multiprocessing.Pool(processes=y.settings.pool_size)
    pool_outputs = pool.map(run_star, config)
    pool.close()
    pool.join()

    datamine.write_data(y.paths.project)
    command('cat {0}/data.csv | mail -s "Output" {1}'.format(y.paths.project, y.settings.email))
    

if __name__ == "__main__":
    main()


