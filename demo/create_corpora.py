from __future__ import division
import sys
import os
import math
import yaml

def process_config(fn):
    with open(fn, 'r') as c:
        y=yaml.load(c)
    
    #create dictionary of file info for easy reference    
    d=dict()
    d['name']=y['name']
    d['foreign_language']=y['foreign_language']
    d['corpus_language']=y['corpus_language']
    d['sources']=dict()
    for f in y['sources']:
        d['sources'][f['file_name']]=dict([('file_path',f['file_path']),('percent_train',f['percent_train']),('percent_tune',f['percent_tune']),('percent_test',f['percent_test']), ('end',0) ])
        d['sources'][f['file_name']].setdefault('percent_of_train',0)
        d['sources'][f['file_name']].setdefault('percent_of_tune',0)
        d['sources'][f['file_name']].setdefault('percent_of_test',0)
    for t in ['train','tune','test']:
        for f in y['source_contributions'][t]:
            d['sources'][f['file_name']]['percent_of_'+t]=f['percent_of_corpus'] 
    return d


#verify that percentages add up to 100 and are valid
def verify_percs(d):
    for fn,s in d['sources'].iteritems():
        if s['percent_train']+s['percent_tune']+s['percent_test'] != 100:
             print("Percentages don't add up to 100")
             return 1
        elif s['percent_train']<0 or s['percent_tune']<0 or s['percent_test'] < 0:
            print("percentage is below 0")
            return 1
        elif s['percent_train']>100 or s['percent_tune']>100 or s['percent_test'] >100:
            print("percentage is above 100")
            return 1
        
    for t in ['train', 'tune', 'test']:
        tot=0
        for fn,s in d['sources'].iteritems():
            tot=tot+s['percent_of_'+t]
        if(tot!=100):
            print(t+" percentages don't add up to 100")
            return 1
    
    return 0

#appends the correct amount of the corpus to the basefile, finishing up the file when necessary
def append_corpus(percentage, num_copies, base_fn, new_fn, start, final=False):
    with open(new_fn, 'r') as f:
        new_content = f.readlines()
    
    with open(base_fn, 'a') as f:
        tot=int(len(new_content)*percentage/100)
        i=1
        while i<=num_copies:
            if final==False:
                f.writelines(new_content[start:start+tot])
            else:
                f.writelines(new_content[start:])
            i=i+1   
        if(i!=num_copies): f.writelines(new_content[start:start+int(tot*(num_copies-i+1))])
            
    return start+tot

def get_file_lengths(d):
    for fn,s in d['sources'].iteritems():
        with open(s['file_path'], 'r') as f:
            s['length']=len(f.readlines())

# returns the ideal total length of the corpus, the minimum length where each corpus section is used in full but the least is added
def get_total_length(d,t):
    tot_length=0
    i=0
    for fn,s in d['sources'].iteritems():
        if s['percent_of_'+t]>0 and s['length']*100/s['percent_of_'+t]>tot_length:
            tot_length=s['length']*100/s['percent_of_'+t]
        i=i+1
    return tot_length
 

#creates the corpus from the config
def create_corpora(config):
    d=process_config(config)
    get_file_lengths(d)
    verify_percs(d)
    if not os.path.exists(d['name']):
        os.makedirs(d['name'])
    
 
    #append files appropriately
    for t in ['train', 'tune', 'test']:
        outfile="{0}/{1}.en-{2}.{3}".format(d['name'],t,d['foreign_language'],d['corpus_language'])
        open(outfile,'w').close()
        tot_length=get_total_length(d,t)   
        i=0
        for fn,s in d['sources'].iteritems():
            s['num_copies']=tot_length*s['percent_of_'+t]/100/s['length']
            final=False
            if(t=='test'): final=True
            s['end']=append_corpus(s['percent_'+t],s['num_copies'],outfile,s['file_path'],s['end'],final)
            i=i+1
            

def main():
    config=sys.argv[1]
    if not os.path.exists(config):
            print(config +" could not be opened")
            print_usage()
            exit(1)
    create_corpora(config)
    
if __name__ == "__main__":
    main()