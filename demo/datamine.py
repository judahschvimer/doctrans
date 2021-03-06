import re
import os.path
import sys
import structures
import logging
import json

'''
This module is used for extracting the data received from experiments created with build_model.py
It requires a directory structure similar to that created by build_model.py
It saves the data in a data.csv file that can easily be viewed in any spreadsheet program
It should be automatically called by build_model.py but can also be used on it's own
Usage: python datamine.py config_train.yaml
'''
logger = logging.getLogger('datamine')
logging.basicConfig(level=logging.DEBUG)

def grab_data(json_file, out):
    '''This function grabs data from the log and prints it to the outfile
    :Parameters:
        - 'log': log from the build_model experiment to copy from  
        - 'out': data file to write to
    '''
    
    with open(json_file, "r") as f:
        d = json.load(f)
    score_list = re.split(", |/| \(|=|\)", d['BLEU'])    
    BLEU_score = score_list[0]
    gram1 = score_list[1]
    gram2 = score_list[2]
    gram3 = score_list[3]
    gram4 = score_list[4]
    BP = score_list[6]
    ratio = score_list[8]
    hyp_len = score_list[10]
    ref_len = score_list[12]
    
    out.write("{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13},{14},{15},{16},{17},{18}\n".format(d['i'], d['max_phrase_length'], d['order'], d['reordering_language'], d['reordering_directionality'], d['score_options'], d['smoothing'], d['alignment'], d['reordering_orientation'], d['reordering_modeltype'], BLEU_score, gram1, gram2, gram3, gram4, BP, ratio, hyp_len, ref_len))

def write_data(project_path):
    '''This function goes through the different log files and writes the data to the outfile
    :Parameters:
        - 'project_path': path to the model as specified in the config file 
    '''
    with open("{0}/data.csv".format(project_path), "w", 1) as out:
        out.write("i,max phrase length,order,reordering language,reordering directionality,score options,smoothing,alignment,reordering orientation,reordering modeltype,BLEU Score,1-gram precision,2-gram precision,3-gram precision,4-gram precision,BP,ratio,hyp len,ref len\n") 
        g=0
        while True:
            json_path = "{1}/{0}/{0}.json".format(g, project_path)
            if os.path.isfile(json_path) == False:
                break
            grab_data(json_path,out)
            g += 1
             
def main():
    if len(sys.argv) != 2:
        print "Usage: python", ' '.join(sys.argv), "config_train.yaml"
        return

    y = structures.BuildConfiguration(sys.argv[1])
    write_data(y.paths.project)

if __name__ == "__main__":
    main()