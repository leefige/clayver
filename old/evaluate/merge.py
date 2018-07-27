import sys

def mergeFile(rootName):
    cnt = 0
    with open(rootName+".txt", 'w') as fout:
        for i in range(8):
            with open(rootName+'_'+str(i+1)+".txt", 'r') as fin:
                for line in fin:
                    if line[-1] != '\n':
                        line.append('\n')
                    fout.write(line)
                    cnt += 1
    print("finished: %d lines" % cnt)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        exit(-1)
    filename = sys.argv[1]
    mergeFile(filename)
