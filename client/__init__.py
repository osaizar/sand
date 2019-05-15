from libclient import *

def main():
    in_file = open("test.txt", "rb")
    data = in_file.read()
    in_file.close()

    print ("[+] Got file, sending")
    file_in_bits = BitArray(data).bin
    send_file(file_in_bits)


if __name__ == '__main__':
    main()
