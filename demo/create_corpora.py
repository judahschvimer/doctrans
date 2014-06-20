import sys
import os
import shutil
import math

def user():
    return sys.stdin.readline().strip()

def copy_and_open(src, dst):
    shutil.copy(src, dst)
    f=open("{0}/{1}".format(dst, os.path.basename(src)),"a")
    return f 

def file_length(f):
    i=0
    for line in f:
        i=i+1
    return i

def main():
    print("Source Language?")
    source=user()
    print("Target Language?")
    target=user()
    os.makedirs("train")
    os.makedirs("tune")
    os.makedirs("test")

    print("Input path to current source training file (N if none)")
    while True:
        line=user()
        if line=="N":
            train_src=open("train/train.{0}-{1}.{0}".format(source,target),"a")
            break
        elif os.path.isfile(line)==False:
            print("Please enter a valid file path")
        else:
            train_src=copy_and_open(line,"train")
            break

    while True:
        print("Input path to new source file (N if no more)")
        line=user()
        if line=="N":
            break
        elif os.path.isfile(line)==False:
            print("Please enter a valid file path")
        else:
            f=open(line,"r")
            len=file_length(f)
            f.close()
            f=open(line,"r")
            while True:
                print("Enter percent of file to be added to training")
                line=user()
                try:
                    train_perc = float(line)
                    if train_perc<0 or train_perc>100:
                        print("Percentage must be between 0 and 100")
                    else:
                        num_lines=math.floor(len*train_perc/100)
                        for i in range(0,num_lines):
                            train_src.write(f.readline())
                except ValueError:
                    print("Invalid number")
                
            close()

    train_src.close()
    
    
   

        
if __name__ == "__main__":
    main()