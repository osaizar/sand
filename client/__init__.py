###########################################################
#  Imports
###########################################################
from libclient import *
from random import randint
import csv
import time
import sys

HELP = """-i <input file> [-h] [-c <covert file>] [-t]
-h print help
-i input file
-c covert file
-t run tests
"""

###########################################################
#  Main functions
###########################################################
def get_pokemon():
    return "pokemon/"+str(randint(0,5757))+".png"

def write_csv(filename, titles, rows):
	file = open(filename, mode='w+')
	writer = csv.writer(file, delimiter=',', quotechar="'", quoting=csv.QUOTE_MINIMAL)
	writer.writerow(titles)
	for row in rows:
		writer.writerow(row)

def make_tests(output_file):
	secrets = [2, 4, 8, 16, 32, 64, 128, 256]
	results = []
	covert = open('test_files/16K', "rb").read()
	covert_size = len(covert)
	for secret_size in secrets:
		secret = open('test_files/' + str(secret_size), "rb").read()
		print('[+] Acting on covert size %d and secret size %d' %(len(secret), len(covert)))
		tic = time.time()
		send_file(secret, covert)
		toc = time.time()
		results.append((covert_size, secret_size, tic - toc))
	write_csv(output_file, ['Covert Size', 'Secret Size', 'Time to Send (sec)'], results)

def main(in_file, covert, test):
    if test:
	       make_tests('localhost_results.csv')
    else:
        if covert:
            covert = open(covert,"rb").read()
        else:
            covert = open(get_pokemon(), "rb").read()

        in_file = open(in_file, "rb").read()
        send_file(in_file, covert)

def parse_args():
    in_file = None
    covert = None
    test = False
    try:
        for i, arg in enumerate(sys.argv):
            if arg == "-h":
                print(HELP)
                sys.exit()
            elif arg == "-i":
                in_file = sys.argv[i+1]
            elif arg == "-c":
                covert = sys.argv[i+1]
            elif arg == "-t":
                test = True
    except Exception as e:
        print("Error: "+str(e)+"\n"+HELP)
        sys.exit()

    if not in_file:
        print("No in file provided\n"+HELP)
        sys.exit()

    return in_file, covert, test

if __name__ == '__main__':
    in_file, covert, test = parse_args()
    main(in_file, covert, test)
