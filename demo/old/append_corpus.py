import sys
import os
import shutil
import math

def copy_and_open(src):
    shutil.copy(src, "./{0}-1".format(os.path.basename(src)))
    f=open("./{0}-1".format(os.path.basename(src)),"a")
    return f 

def file_length(f):
    i=0
    for line in f:
        i=i+1
    return i

def print_usage():
    print("Usage: python append_corpus.py [base corpus] [new corpus] [percentage of new corpus]")

def append_corpus(percentage, base_fn, new_fn): 
    with open(new_fn, 'r') as f: 
        new_content = f.readlines()

    with open(base_fn, 'a') as f: 
         f.writelines(new_content[:int(len(new_content)*percentage/100)])

def main(): 
    base_fn = sys.argv[1]
    new_fn = sys.argv[2]
    
    try:
        percentage = float(sys.argv[3])
        if percentage<0 or percentage>100:
            print("Percentage must be between 0 and 100")
            print_usage()   
            exit(1)
    except ValueError:
        print("Invalid percentage")
        print_usage()   
    
    for fn in (new_fn, base_fn): 
        if not os.path.exists(fn):
            print(fn +" could not be opened")
            print_usage()
            exit(1)
    
    append_corpus(percentage, base_fn, new_fn)
        
if __name__ == "__main__":
    main()