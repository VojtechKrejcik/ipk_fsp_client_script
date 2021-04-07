#!/usr/bin/env python3
# autor: Vojtech Krejcik
# 1. projekt IPK 2021

"""TODO TODAY
"""
from socket import *
import re, getopt, sys


bufferSize = 4096


def NSP(ip,port, domain):
    """Function requesting Name Server Protocol on server given by ip and port in parametrs for domain"""
    bytesToSend = str.encode(f"WHEREIS {domain}")
    serverAddressPort = (ip, port)
    UDPClientSocket = socket(family=AF_INET, type=SOCK_DGRAM)
    UDPClientSocket.sendto(bytesToSend, serverAddressPort)
    msgFromServer = UDPClientSocket.recvfrom(bufferSize)

    # parsing answer
    splitted_msg = re.split(' ', msgFromServer[0].decode('utf-8'))

    # parse answer if 
    if splitted_msg[0] == 'OK':
        fsp_ip, fsp_port = re.split(':', splitted_msg[1])
        fsp_port = int(fsp_port)
        return fsp_ip, fsp_port
    else:
        print("NSP server error: ", splitted_msg[1:])
        raise Exception()


def fsp(host, port, file_path):
    """Function downloads file specified by filepath from FSP serever specified by host (ipv4 of server) and port"""
    file_path = file_path.replace('\n','')
    bytesToSend = str.encode(f"GET {file_path} FSP/1.0\r\nHostname:{host}\r\nAgent: xkrejc68\r\n\r\n")
    byte_answer = b"" 
    with socket(AF_INET, SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(bytesToSend)
        while True:
            data = s.recv(bufferSize)
            if not data:break
            byte_answer = b''.join([byte_answer, data])

    if byte_answer[0:15] == b'FSP/1.0 Success':
        i = 15
        while(True):
            i += 1
            if byte_answer[i:i+4] ==b'\r\n\r\n':
                with open(re.split('/',file_path)[-1], "wb") as bin_file:
                    bin_file.write(byte_answer[i+4:])
                break
    #Error
    else:
        error_message = byte_answer.decode("utf-8").split("\r\n\r\n")[-1]
        print(error_message)
        raise Exception()


if __name__ == "__main__":
    #processing command line arguments
    #====================================================================================================
    f_flag = False
    n_flag = False
    try:
        opts, args = getopt.getopt(sys.argv[1:], "n:f:h") 
    except:
        print('Wrong arguments, use python fileget.py -h to see help!')
        sys.exit(1)
    for opt, arg in opts:
        # -n NAMESERVER (ex. "127.0.0.1:3333" )
        if opt == '-n':
            n_flag = True
            try:
                ip, port = re.split(':', arg) # ip address and port      
                if not re.search(r'(^([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})$)',ip):
                    raise TypeError
                port = int(port) # port of name server as int
                if port not in range(1023,65353):
                    raise ValueError

            except TypeError:
                print('Invalid format of ip address')
                sys.exit(1)
            
            except ValueError:
                print("Number of port is not in range from 1023 to 65553")
                sys.exit(1)
        # -f SURL (ex. "fsp://foo.bar/file.txt"        
        if opt == '-f':
            f_flag = True
            try:
                surl_lsit = re.split('/', arg)
                if surl_lsit[0] == "fsp:" and surl_lsit[1] == '' and re.search(r'^(^[a-zA-Z0-9\.\-_]+$)', surl_lsit[2]):
                    file_path = '/'.join(surl_lsit[3:]) # file to download from fsp server
                    server_name = surl_lsit[2] # host name of server
                else:
                    raise Exception
            except:
                print("Invalid SURL")
                sys.exit(1)
        if opt == '-h':
            print("Usage:\nfileget -n NAMESERVER -f SURL")
            sys.exit(1)

    if not( n_flag and f_flag):
        print("Invalid arguments")
        sys.exit(1)
    #====================================================================================================

    # Gettin ip address and port of FSP server from NSP sever
    try:
        fsp_ip, fsp_port = NSP(ip, port, server_name)
    except TimeoutError:
        print("NSP server: Timeout error")
        sys.exit(1)
    except:
        sys.exit(1)
    
    # Downloadin all files from server
    if file_path == '*':
        fsp(fsp_ip, fsp_port, 'index')
        index = open('index', 'r')
        for line in index:
            fsp(fsp_ip, fsp_port, line)
    # Downloading specified filem from fsp server
    else:
        try:
            fsp(fsp_ip,fsp_port, file_path)  

        except TimeoutError:
            print("NSP server: Timeout error")
            sys.exit(1)
        except:
            sys.exit(1)

    sys.exit(0)
    
