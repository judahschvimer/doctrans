import sys
import logging

'''
This module prints out all files line by line to compare lines
Just give it as many files as you want at the start, it'll finish when the first file is empty if they are not the same amount of lines
It saves the output to merged.txt
Usage: python merge_trans.py output_file infile1 infile2 infile3....
'''
logger = logging.getLogger('merge_trans')
logging.basicConfig(level=logging.DEBUG)

def merge_files(output, file_list, annotation_list):
    '''This function merges all of the files in the file_list into the output file
    annotations are made in order to help differentiate which line is from which file
    :Parameters:
        - 'output': The file to output the lines to
        - 'file_list': The list of file names to merge
        - 'annotation_list': The list of annotations to use
    '''
    with open(output, "w",1) as out:
        open_files = []
        for file in file_list:
            open_files.append(open(file,"r"))
        t = True
        while t:
            for index, file in enumerate(open_files):
                line = file.readline()
                print line
                if not line:
                    t = False
                    break
                if line[-1] == '\n': out.write(annotation_list[index]+line)    
                else: out.write(annotation_list[index]+line+'\n')    
            out.write("\n")
        for file in open_files:
            file.close()


def main():
    if len(sys.argv) < 3:
        print "Usage: python", ' '.join(sys.argv), "output_file infile1 infile2 ..."
        return    
    if len(sys.argv) > 14:
        print "Too many files, add more annotations and retry"
        return
    #This list is meant to be longer than any number of files anyone would use
    annotation_list = ['- ', '+ ', '~ ', '> ', '= ','* ', '# ', '$ ', '^ ', '% ', '& ', '@ ']
    merge_files(sys.argv[1], sys.argv[2:], annotation_list)    

if __name__ == "__main__":
    main()