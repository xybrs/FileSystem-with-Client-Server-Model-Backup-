import socket
import sys

def clientServerCommunication(message):
    #print(message)
    client_socket.send(message.encode())  # send message
def serverClientCommuncation():
    try:
        data = client_socket.recv(2048).decode()  # receive response
        return str(data)
    except:
        print("Error! Data from Server not received!")
        sys.exit()
    #print(data)
    return str(data)

def clientCLI():
    print("Welcome to the UI for the file management  system.")
    while(True):
        choice = input("Enter p to proceed. e to exit the UI: ")
        clientServerCommunication(choice)
        if (choice == 'p'):
            diskOrFile = input("Enter d to operate on Disk. f to operate on File: ")
            clientServerCommunication(diskOrFile)

            if (diskOrFile == 'd'):
                choice = input("Enter c to create file, d to delete file, m for mem map and anykey for directory creation: ")
                clientServerCommunication(choice)
                if (choice == 'c'):
                    clientServerCommunication(input("Enter file name: "))
                    clientServerCommunication(input("Enter dir name: "))
                    if (int(serverClientCommuncation()) == 1):
                        print("File Created Successfully")
                    else:
                        print("File Not created!")
                elif (choice == 'd'):
                    clientServerCommunication(input("Enter file name: "))
                    clientServerCommunication(input("Enter Directory name: "))
                    if (int(serverClientCommuncation())==1):
                        print("File deleted successfully!")
                    else:
                        print("File not deleted!")
                elif (choice == 'm'):
                    print(serverClientCommuncation())
                else:
                    clientServerCommunication(input("Enter Dir name: "))
                    clientServerCommunication(input("Enter Parent Directory: "))
                    if (int(serverClientCommuncation()) == 1):
                        print("Dir Created Succesfully!")
                    else:
                        print("Directory not created!")
            elif (diskOrFile == 'f'):

                clientServerCommunication(input ("Enter file Name: "))
                confirmation = int(serverClientCommuncation())
                if (confirmation == 1):
                    print("Delivered!")
                else:
                    print("Invalid fileName!")
                    continue
                #while (True):
                mode = input ("w to write, r to read,t to trunc: ")
                clientServerCommunication(mode)
                if (mode == 'w'):
                    if int(serverClientCommuncation()) == 1:
                        print("File Opened with Write Priveleges")
                        clientServerCommunication(input("Enter String: "))
                        clientServerCommunication(input("Enter loc: "))
                        clientServerCommunication(input("Enter mode (a for append, w for write, W for write at loc):"))
                        if int(serverClientCommuncation()) == 1:
                            print("Written to File succesfully")
                        else:
                            print("Failed to Write to File!")

                elif (mode == 't'):
                    if int(serverClientCommuncation()) == 1:
                        print("File Opened with Write Priveleges")
                        clientServerCommunication(input("Enter size to truncate to: "))
                        if int(serverClientCommuncation()) == 1:
                            print("Truncation Succesful!")
                        else:
                            print("Failed to truncate File!")
                            
                elif (mode == 'r'):
                    if int(serverClientCommuncation()) == 1:
                        print("File Opened with Read Priveleges")
                        check = input("Enter a for for all. s for specific: ")
                        clientServerCommunication(check)
                        if (check == 'a'):
                            print(serverClientCommuncation())
                        else:
                            start,size = clientServerCommunication(input("Enter start: ")),clientServerCommunication(input("Enter size: "))
                            print(serverClientCommuncation())
        if (choice == 'e'):
            break

def userName():
    ####Enter username
    clientServerCommunication(input("Enter username: "))
    sessionNumber = int(serverClientCommuncation())
    #print(sessionNumber)
    if (int(sessionNumber) == -1):
        print("User sessions Overflow. User not logged in!\n")
        exit
    else:
        print("User Session Established! Session No: ", int(sessionNumber) , "\n")

if __name__ == '__main__':
    ip = input("Enter IP Address: ")
    #host = socket.gethostbyaddr("192.168.1.2")[0][:-5]  # as both code is running on same pc
    try:
        host = socket.gethostbyaddr(ip)[0]
        print(host)
    except:
        print("Invalid IP Address!\n")
        sys.exit()
    port = 95  # socket server port number
    client_socket = socket.socket()  # instantiate
    try:
        client_socket.connect((host, port))  # connect to the server
        print("Succesfully connected to the server!\n")
    except:
        print("Unable to connect to the Server!\n")
        sys.exit()
    userName()
    clientCLI()
