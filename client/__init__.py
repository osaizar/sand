from libclient import *

def get_pokemon():
    pass

def main():
    data = open("test.txt", "rb").read()
    covert = get_pokemon()

    print ("[+] Got file, sending")
    
    file_in_bits = BitArray(data).bin
    send_file(file_in_bits, covert)


if __name__ == '__main__':
    main()
