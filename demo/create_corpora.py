from __future__ import division
import sys
import os
import math
import yaml
import logging

''''
This module creates the appropriate train, tune, and test corpora
You must run it one language at a time in case the files don't match up exactly, 
however it would be easy to modify if you guarenteed they would match up
It takes a config file similar to config_corpora.yaml
Usage: python create_corpora.py config_corpora.yaml
'''

logger = logging.getLogger('create_corpora')
logging.basicConfig(level=logging.DEBUG)

def process_config(fn):
    '''This function takes a configuration file cand creates a dictionary of the useful information.
    It also sets defaults for certain arguments so they do not need to be specified by the user for it to work
    :Parameters:
        - 'fn': file name of the configuration file
    :Returns:
        - a dictionary of the configuration
    '''

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


def verify_percs(d):
    '''This function verifies that the percentages are valid and add up to 100
    :Parameters:
        - 'd': configuration dictionary
    :Returns:
        True if they're verified, false if there's a problem
    '''
    for fn,s in d['sources'].iteritems():
        if s['percent_train'] + s['percent_tune'] + s['percent_test'] != 100:
             logger.error("Percentages don't add up to 100")
             return False
        elif s['percent_train'] < 0 or s['percent_tune'] < 0 or s['percent_test'] < 0:
            logger.error("percentage is below 0")
            return False
        elif s['percent_train'] > 100 or s['percent_tune'] > 100 or s['percent_test'] > 100:
            logger.error("percentage is above 100")
            return False
        
    for t in ['train', 'tune', 'test']:
        tot = 0
        for fn,s in d['sources'].iteritems():
            tot += s['percent_of_'+t]
        if tot != 100:
            logger.error(t+" percentages don't add up to 100")
            return False
    
    return True

def append_corpus(percentage, num_copies, base_fn, new_fn, start, final=False):
    '''This function appends the correct amount of the corpus to the basefile, finishing up the file when necessary so no data goes to waste
    :Parameters:
        - 'percentage': percentage of the file going into the corpus
        - 'num_copies': number of copies of the file section going into the corpus
        - 'base_fn': file name of the base file to append the corpus to 
        - 'new_fn': file name of the new file to take the data from
        - 'start': the line to start copying from in the new file
        - 'final': if it's the final section of the file it makes sure to go to the end, assuming the length will be apporximately correct 
    :Returns:
        - The last line it copied until
    '''
    with open(new_fn, 'r') as f:
        new_content = f.readlines()
    
    with open(base_fn, 'a') as f:
        tot = int(len(new_content) * percentage / 100)
        i = 1
        while i <= num_copies:
            if final is False:
                f.writelines(new_content[start:start+tot])
            else:
                f.writelines(new_content[start:])
            i += 1   
        if i!=num_copies: 
            f.writelines(new_content[start:start+int(tot*(num_copies-i+1))])
            
    return start + tot

def get_file_lengths(d):
    '''This function adds the file lengths of the files to the configuration dictionary
    :Parameters:
        - 'd': configuration dictionary
    '''
    for fn,s in d['sources'].iteritems():
        with open(s['file_path'], 'r') as f:
            s['length'] = len(f.readlines())

def get_total_length(d, corpus_type):
    '''This function finds the ideal total length of the corpus
    It finds the minimum length where each corpus section is used in full 
    :Parameters:
        - 'd': configuration dictionary
        - 'corpus_type': either train, tune, or test
    :Returns:
        - total length of the corpus
    '''
    tot_length=0
    i=0
    for fn,s in d['sources'].iteritems():
        if s['percent_of_'+corpus_type] > 0 and s['length'] * 100 / s['percent_of_'+corpus_type] > tot_length:
            tot_length = s['length'] * 100 / s['percent_of_'+corpus_type]
        i += 1
    return tot_length
 

def create_corpora(config):
    '''This function takes the confiration file and runs through the files, appending them appropriately
    It first verifies that all of the percentages add up and then it figures out how much of each file should go into each corpus and appends them
    :Parameters:
        - 'config': configuration of the corpora
    '''
    
    d = process_config(config)
    get_file_lengths(d)
    if verify_percs(d) is False:
        return
    if os.path.exists(d['name']) is False:
        os.makedirs(d['name'])
    
 
    #append files appropriately
    for t in ['train', 'tune', 'test']:
        outfile = "{0}/{1}.en-{2}.{3}".format(d['name'], t ,d['foreign_language'] ,d['corpus_language'])
        open(outfile,'w').close()
        # finds the total length of the entire corpus
        tot_length = get_total_length(d, t)   
        i = 0
        for fn,s in d['sources'].iteritems():
            #finds how many copies of this file will make it the correct percentage of the full corpus
            s['num_copies'] = tot_length * s['percent_of_'+t] / 100 / s['length']
            final = False
            if t is 'test': 
                final = True
            #appends the section of the file to the corpus
            s['end'] = append_corpus(s['percent_'+t], s['num_copies'], outfile, s['file_path'], s['end'], final)
            i += 1
            

def main():
    if len(sys.argv) != 2:
        print("Usage: python", ' '.join(sys.argv), "config_corpora.yaml")
        return

    config = sys.argv[1]
    if not os.path.exists(config):
            print(config +" could not be opened")
            exit(1)

    create_corpora(config)
    
if __name__ == "__main__":
    main()