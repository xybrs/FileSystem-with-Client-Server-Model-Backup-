import socket
import sys
import threading
import time

sys.path.append('./Code/HardDisk')
from hardDisk import hardDisk
from fileObject import fileInDisk

#### CONSTANTS
USER_WINDOWS_LIMIT = 6
FILE_READ_LIMIT = 2
USER_FILE_LIMIT = 3

readerCount = {}

host = socket.gethostname()
port = 95  
server_socket = socket.socket()
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((host, port))
#server_socket.bind(("0.0.0.0", port))
threads = []

users = {}

usersFiles = {}         #Semaphore dictionary
readRequests = {}       #Semaphore dictionary
writeRequests = {}      #Semaphore dictionary

writeQuery = {}        #Write Query
writeQueryLock = {}
readerCountLock = {}

# configure how many client the server can listen simultaneously
server_socket.listen(1)

def clientServerCommunication(connection):
    data = connection.recv(1024).decode()
    #print(str(data))
    return str(data)
def serverClientCommuncation(connection, message):
    data = message.encode()
    #print(message)
    connection.send(data)

def userName(connection):
    inputUsername = clientServerCommunication(connection)
    #print(inputUsername)
    if inputUsername not in users:
        #Adding to the users dictionary and creating an item in the usersFiles
        users[inputUsername] = 1
        serverClientCommuncation(connection, "1")

    elif (users[inputUsername] < USER_WINDOWS_LIMIT):
        users[inputUsername]+=1
        print("Username: " ,inputUsername, " Session No.", users[inputUsername], " Started")
        serverClientCommuncation(connection, str(users[inputUsername]))
    else:
        print("Already 5 sessions are active. Terminating!")
        serverClientCommuncation(connection, "-1")
        connection.close()
    return inputUsername

############################# READER WRITER
def reader(conn, userName, fileName, mode):

    readerCountLock.setdefault(fileName, threading.Lock())

    #Updating the readerCount in a lock
    readerCountLock[fileName].acquire()
    readerCount.setdefault(fileName,0)
    readerCount[fileName]+=1
    readerCountLock[fileName].release()

    #Checking if this is the first file being read. And blocking the writer if that is the case
    if (readerCount[fileName] == 1):
        writeRequests.setdefault(fileName, threading.Semaphore(1))          ###Blocking write if read is active
        writeRequests[fileName].acquire()

    ##################Performing the READ operation
    #Acquiring a semaphore of the user
    usersFiles.setdefault(userName, threading.Semaphore(USER_FILE_LIMIT))    
    usersFiles[userName].acquire()

    #Acquiring a semaphore of a fileRead
    readRequests.setdefault(fileName, threading.Semaphore(FILE_READ_LIMIT))
    readRequests[fileName].acquire()

    fileOpened = fileInDisk(fileName)
    serverClientCommuncation(conn, "1")

    check = clientServerCommunication(conn)
    if (check == 'a'):
        serverClientCommuncation(conn, fileOpened.readFrom())
    else:
        start,size = clientServerCommunication(conn),clientServerCommunication(conn)
        serverClientCommuncation(conn, fileOpened.readFromSeg(int(start),int(size)))
    
    #Releasing semaphores
    readRequests[fileName].release()
    usersFiles[userName].release()
    
    #################Read operation Ended

    #Decreasing the reader count as we've read the file and closed it
    readerCountLock[fileName].acquire()
    readerCount[fileName]-=1
    readerCountLock[fileName].release()

    #Checking if no more reader is active and unblocking the writer if that is the case
    if(readerCount[fileName] == 0):
        writeRequests[fileName].release() # If this is the last reader, it will release the writer


def writer(conn, userName, fileName, mode):

    #Setting the default lock
    writeQueryLock.setdefault(fileName, threading.Lock())
    writeQuery.setdefault(fileName, [])
    
    # Finding the thread number of this write!
    threadNum =  threading.current_thread().ident        

    # Adding this number to the write Query
    writeQueryLock[fileName].acquire()
    writeQuery[fileName].append(threadNum)       
    writeQueryLock[fileName].release()

    # Locking until the writeQuery reaches this number
    while (True):
        time.sleep(1)          
        if (writeQuery[fileName][0] == threadNum):
            break

    #Acquiring a usersFile semaphore
    usersFiles.setdefault(userName, threading.Semaphore(USER_FILE_LIMIT))
    usersFiles[userName].acquire()

    ##################WRITE
    #Acquiring a writeRequest semaphore
    writeRequests.setdefault(fileName, threading.Semaphore(1))
    writeRequests[fileName].acquire()

    fileOpened = fileInDisk(fileName)
    serverClientCommuncation(conn, "1")

    if (mode == 'w'):
        try:
            toWrite, loc, mode = clientServerCommunication(conn), clientServerCommunication(conn), clientServerCommunication(conn)
            fileOpened.write(toWrite,int(loc),mode)
            serverClientCommuncation(conn, "1")
        except:
            serverClientCommuncation(conn, "-1")
    elif (mode == 't'):

        try:
            size = clientServerCommunication(conn)
            fileOpened.truncateFile(int(size))
            serverClientCommuncation(conn, "1")
        except:
            serverClientCommuncation(conn, "-1")

    #Releasing writes
    writeRequests[fileName].release()
    usersFiles[userName].release()
    #################FINISH WRITE

    #Removing thread from writeQuery
    writeQueryLock[fileName].acquire()      #Making sure writeQuery is safe
    print("Thread that was popped: " ,writeQuery[fileName].pop(0))                            # Removing the writeQuery element!
    writeQueryLock[fileName].release()

    print("Remaining thread: ", writeQuery[fileName])
############################# READER WRITER

def serverCli(conn, userName):
    print("Welcome to the UI for the file management  system.")
    while (clientServerCommunication(conn) == 'p'):
        #print("Welcome to the UI for the file management system.")
        diskOrFile = clientServerCommunication(conn)
        if (diskOrFile == 'd'):
            #serverClientCommuncation("d")
            choice = clientServerCommunication(conn)
            if (choice == 'c'):
                #serverClientCommuncation("c")
                try:
                    hardDisk.createFile(clientServerCommunication(conn), clientServerCommunication(conn))
                    serverClientCommuncation(conn, "1")
                except:
                    serverClientCommuncation(conn,"-1")
            elif (choice == 'd'):
                try:
                    hardDisk.deleteFile(clientServerCommunication(conn), clientServerCommunication(conn))
                    serverClientCommuncation(conn,"1")
                except:
                    serverClientCommuncation(conn, "-1")
            elif (choice == 'm'):
                serverClientCommuncation(conn, hardDisk.memMap())
            else:
                try:
                    hardDisk.createDir(clientServerCommunication(conn), clientServerCommunication(conn))
                    serverClientCommuncation(conn, "1")
                except:
                    serverClientCommuncation(conn, "-1")
        elif (diskOrFile == 'f'):
            fileName = clientServerCommunication(conn)
            serverClientCommuncation(conn,"1")
            mode = clientServerCommunication(conn)
            #serverClientCommuncation(conn,"1")
            
            if (mode == 'r'):
                reader(conn, userName, fileName, mode)
            else:
                writer(conn, userName, fileName, mode)

def threaded_client(connection):
    
    username = userName(connection)
    serverCli(connection, username)
    users[username]-=1
    connection.close()

if __name__ == '__main__':

    while(True):
        conn, address = server_socket.accept()
        print('Connected to: ' + address[0] + ':' + str(address[1]))
        threads.append(threading.Thread(target = threaded_client, args = (conn, )))
        threads[-1].start()
        print("New client added!")