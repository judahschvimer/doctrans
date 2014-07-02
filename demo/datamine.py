import re
import os.path
import sys
import structures

#####################################
# This module is used for extracting the data received from experiments created with build_model.py
# It requires a directory structure similar to that created by build_model.py
# It saves the data in an out.csv file that can easily be viewed in any spreadsheet program
# It should be automatically called by build_model.py but can also be used on it's own
# Usage: python datamine.py config_train.yaml
################################################

def grab_data(log, out):
    for line in log:
        words=re.split(" = ",line)
        if len(words)>1:
            words[1]=words[1].strip()
        if words[0]=="Order":
            order=words[1]
        elif words[0]=="Smoothing":
            smoothing=words[1]
        elif words[0]=="ScoreOptions":
            score_options=words[1]
        elif words[0]=="Alignment":
            alignment=words[1]
        elif words[0]=="ReorderingModeltype":
            reordering_modeltype=words[1]
        elif words[0]=="ReorderingOrientation":
            reordering_orientation=words[1]
        elif words[0]=="ReorderingDirectionality":
            reordering_directionality=words[1]
        elif words[0]=="ReorderingLanguage":
            reordering_language=words[1]
        elif words[0]=="MaxPhraseLength":
            max_phrase_length=words[1]
        elif words[0]=="i":
            i=words[1]
        elif words[0]=="BLEU":
            score_list=re.split(", |/| \(|=|\)",words[1])    
            BLEU_score=score_list[0]
            gram1=score_list[1]
            gram2=score_list[2]
            gram3=score_list[3]
            gram4=score_list[4]
            BP=score_list[6]
            ratio=score_list[8]
            hyp_len=score_list[10]
            ref_len=score_list[12]
        
 
    out.write("{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13},{14},{15},{16},{17},{18}\n".format(i,max_phrase_length, order, reordering_language, reordering_directionality, score_options, smoothing, alignment, reordering_orientation, reordering_modeltype, BLEU_score, gram1, gram2, gram3, gram4, BP, ratio, hyp_len, ref_len))

def write_data(model_path):
    with open("{0}/out.csv".format(model_path), "w", 1) as out:
        out.write("i,max phrase length,order,reordering language,reordering directionality,score options,smoothing,alignment,reordering orientation,reordering modeltype,BLEU Score,1-gram precision,2-gram precision,3-gram precision,4-gram precision,BP,ratio,hyp len,ref len\n") 
        g=0
        while True:
            curr_log_path="{1}/{0}/{0}.ilog.txt".format(g, model_path)
            if os.path.isfile(curr_log_path)==False:
                break
            curr_log = open(curr_log_path, "r")
            grab_data(curr_log,out)
            curr_log.close()
            g=g+1
             
def main():
    y=structures.BuildConfiguration(sys.argv[1])
    write_data(y.model_path)
    
if __name__ == "__main__":
    main()