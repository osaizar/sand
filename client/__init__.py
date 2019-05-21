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
		#secret = open('test_files/' + str(secret_size), "rb").read()
		secret = open('test_files/' + str(secret_size), "rb").read()
		print('[+] Acting on covert size %d and secret size %d' %(len(secret), len(covert)))
		tic = time.time()
		send_file(secret, covert)
		toc = time.time()
		results.append((covert_size, secret_size, tic - toc))
	write_csv(output_file, ['Covert Size', 'Secret Size', 'Time to Send (sec)'], results)

def main():
	make_tests('localhost_results.csv')

if __name__ == '__main__':
	main()	

