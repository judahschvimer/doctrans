import sys
from itertools import izip

#prints out all files line by line to compare lines
#just give it as many files as you want at the start, it'll finish when the first file is empty
def main():
    out= open("merged.txt", "w",1)
    files=[]
    for i in range(1,len(sys.argv)):
        files.append(open(sys.argv[i],"r")) 
    t=True
    while t:
        for f in files:
            l=f.readline()
            if l=="":
                t=False
                break
            out.write(l)    
        out.write("\n")
    for f in files:
        f.close()
    out.close()
    
if __name__ == "__main__":
    main()