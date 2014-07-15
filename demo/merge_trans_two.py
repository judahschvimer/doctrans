import sys
from itertools import izip

'''
This module prints each file line by line to compare lines and annotates them for easy viewing
Unlike merge_trans.py, this one only works for 2 files but adds annotations
It saves the output to merged.txt
Usage: python merge_trans_two.py file1 file2
'''

def main():
    if len(sys.argv) != 3:
        print "Usage: python", ' '.join(sys.argv), "file1 file2"
        return
    
    with open("merged.txt", "w",1) as out:
        with open(sys.argv[1],"r") as f1:
            with open(sys.argv[2],"r") as f2:
                t = True
                while t:
                    l1 = f1.readline()
                    l2 = f2.readline()
                    if l1 == "" or l2 == "":
                        t = False
                        break
                    out.write("- "+l1)
                    out.write("+ "+l2)    
                    out.write("\n")
    
if __name__ == "__main__":
    main()