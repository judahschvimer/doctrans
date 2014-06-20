import sys
import os
import shutil
import math

def copy_and_open(src):
    shutil.copyfile(src, "{0}-copy".format(src))
    f=open(src,"a")
    return f 

def file_length(f):
    i=0
    for line in f:
        i=i+1
    return i

def print_usage():
    print("Usage: python append_corpus.py [starting corpus or -n if none] [corpus to append] [percentage of corpus]")

def main():
    if len(sys.argv)!=4:
        print_usage()   
        exit(1)
    try:
        percentage = float(sys.argv[3])
        if percentage<0 or percentage>100:
            print("Percentage must be between 0 and 100")
            print_usage()   
            exit(1)
    except ValueError:
        print("Invalid percentage")
        print_usage()   
        exit(1)
    none=False
    if sys.argv[1]=="-n":
        none=True
    elif os.path.isfile(sys.argv[1])==False:
        print("Please enter a valid starting corpus file path")
        print_usage()   
        exit(1)
        
    if os.path.isfile(sys.argv[2])==False:
        print("Please enter a valid file path for the corpus to append")
        print_usage()   
        exit(1)
    if none:
        start=open("newcorpus.txt","w")   
    else:
        start=copy_and_open(sys.argv[1])
    additional=open(sys.argv[2], "r")
    length=file_length(additional)
    additional.close()
    additional=open(sys.argv[2],"r")
    num_lines=int(math.floor(length*percentage/100))
    for i in range(0,num_lines):
        start.write(additional.readline())
    additional.close()
    start.close()
        
if __name__ == "__main__":
    main()