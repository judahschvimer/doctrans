import sys
import re

def split_dict(in_f, from_f, to_f):
    for line in in_f:
        if line[0]=='#':
            continue
        halves = re.split(r'\t+', line)
        if len(halves) < 2:
            continue          
        from_words = re.split(r';', halves[0])       
        to_words = re.split(r';', halves[1])
        for to_word in to_words:
            to_word=to_word.strip()
            for from_word in from_words:
                from_word = from_word.strip()
                from_f.write(from_word)
                from_f.write("\n")
                to_f.write(to_word)
                to_f.write("\n")
    

def main():
    if len(sys.argv) !=  4:
        print("Usage: python split_dict.py <inFile> <fromFile> <toFile>")
        sys.exit();
    in_file_name = sys.argv[1]
    fpi = open(in_file_name)
    from_file_name = sys.argv[2]
    fpf = open(from_file_name,'w')
    to_file_name = sys.argv[3]
    fpt = open(to_file_name,'w')
    split_dict(fpi,fpf,fpt)

if __name__ == "__main__":
    main()