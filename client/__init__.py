###########################################################
#  Imports
###########################################################
from libclient import *
from random import randint
import csv
import time
###########################################################
#  Main functions
###########################################################
def write_csv(filename, titles, rows):
	#file = open('id_user_url.csv', mode='w+')
	file = open(name, mode='w+')
	writer = csv.writer(file, delimiter=',', quotechar="'", quoting=csv.QUOTE_MINIMAL)
	writer.writerow(titles)
	for row in rows:
		writer.writerow(row)

def make_tests(output_file):
	secrets = [256, 512, 1024, 2048, 4096]
	coverts = [256, 512, 1024, 2048, 4096, 10240]
	results = []
	covert = open('test_files/16K', "rb").read()
	for secret_size in secrets:
		#secret = open('test_files/' + str(secret_size), "rb").read()
		secret = open('test_files/' + str(secret_size), "rb").read()
		print('[+] Acting on covert size %d and secret size %d' %(len(secret), len(covert)))
		tic = time.time()
		send_file(secret, covert)
		toc = time.time()
		results.append((covert_size, secret_size, tic - toc))
		return
	write_csv(output_file, ['Covert Size', 'Secret Size', 'Time to Send (sec)'], results)
def get_pokemon():
    return "pokemon/"+str(randint(0,5757))+".png"

def main():
    data = open("test.txt", "rb").read()
    covert = open(get_pokemon(), "rb").read()

    print ("[+] Got file, sending")

    send_file(data, None) # TODO: add covert

if __name__ == '__main__':
	make_tests('localhost_results.csv')
	#main()
	#
    #
