from KNNLearn import *
import sys

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("usage:\n%s test_file_name(no .txt)\n" % (sys.argv[0]))
        exit(-1)
    filename = "./evaluate/" + sys.argv[1] + ".txt"
    if len(sys.argv) > 2:
        classify(filename, int(sys.argv[2]))
    else:
        classify(filename)
