from libclient import *
from random import randint

def get_pokemon():
    return "pokemon/"+str(randint(0,5757))+".png"

def main():
    data = open("test.txt", "rb").read()
    covert = open(get_pokemon(), "rb").read()

    print ("[+] Got file, sending")

    send_file(data, None) # TODO: add covert


if __name__ == '__main__':
    main()
