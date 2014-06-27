import sys
from itertools import izip

#prints each file line by line to compare lines
#this one only works for 2 files
def main():
    out= open("merged.txt", "w",1)
    with open(sys.argv[1],"r") as f1:
        with open(sys.argv[2],"r") as f2:
            t=True
            while t:
                l1=f1.readline()
                l2=f2.readline()
                if l1=="" or l2=="":
                    t=False
                    break
                out.write("- "+l1)
                out.write("+ "+l2)    
                out.write("\n")
    
if __name__ == "__main__":
    main()