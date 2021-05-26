import sys
import os
sys.path.insert(0, '.\HardDisk')
sys.path.insert(0, '.\Code\HardDisk')

from fileObject import fileInDisk
from hardDisk import hardDisk

def cli():
    while (input("Enter p to proceed. e to exit: ") == 'p'):
        print("Welcome to the UI for the file management system.")
        diskOrFile = input("Enter d to operate on Disk. f to operate on File: ")
        if (diskOrFile == 'd'):
            choice = input("Enter c to create file, d to delete file, m for mem map and anykey for directory creation: ")
            if (choice == 'c'):
                hardDisk.createFile(input("Enter file name: "), input("Enter dir name: "))
            elif (choice == 'd'):
                hardDisk.deleteFile(input("Enter file name: "), input("Enter Directory Name: "))
            elif (choice == 'm'):
                hardDisk.memMap()
            else:
                hardDisk.createDir(input("Enter Dir name: "), input("Enter Parent Directory: "))
        elif (diskOrFile == 'f'):
            fileOpened = fileInDisk(input ("Enter file Name: "))
            while (True):
                mode = input ("w to write, r to read,t to trunc, and e to Exit: ")
                if (mode == 'w'):
                    toWrite, loc, mode = input("Enter String: "), input("Enter loc: "), input("Enter mode (a for append, w for write, W for write at loc):")
                    fileOpened.write(toWrite,int(loc),mode)
                elif (mode == 't'):
                    size = input("Enter size to truncate to: ")
                    fileOpened.truncateFile(int(size))
                elif (mode == 'r'):
                    check = input("Enter a for for all. s for specific: ")
                    if (check == 'a'):
                        print(fileOpened.readFrom())
                    else:
                        start,size = input("Enter start: "),input("Enter size: ")
                        print(fileOpened.readFromSeg(int(start),int(size)))
                elif (mode == 'e'):
                    del fileOpened
                    break

def multipleCLI(fileName):
    file = open(fileName, "r")

    while (file.readline()[:-1] == 'p'):
        diskOrFile = file.readline()[:-1]
        if (diskOrFile == 'd'):
            choice = file.readline()[:-1]
            if (choice == 'c'):
                hardDisk.createFile(file.readline()[:-1], file.readline()[:-1])
            elif (choice == 'd'):
                hardDisk.deleteFile(file.readline()[:-1], file.readline()[:-1])
            elif (choice == 'm'):
                hardDisk.memMap()
            else:
                hardDisk.createDir(file.readline()[:-1], file.readline()[:-1])
        elif (diskOrFile == 'f'):
            fileOpened = fileInDisk(file.readline()[:-1])
            while (True):
                mode = file.readline()[:-1]
                if (mode == 'w'):
                    toWrite = file.readline()[:-1]
                    loc = file.readline()[:-1]
                    mode = file.readline()[:-1]
                    fileOpened.write(toWrite,int(loc),mode)
                elif (mode == 't'):
                    size = file.readline()[:-1]
                    fileOpened.truncateFile(int(size))
                elif (mode == 'r'):
                    check = file.readline()[:-1]
                    if (check == 'a'):
                        print(fileOpened.readFrom()[:-1])
                    else:
                        start,size = file.readline()[:-1],file.readline()[:-1]
                        print(fileOpened.readFromSeg(int(start),int(size)))
                elif (mode == 'e'):
                    del fileOpened
                    break

if __name__ == "__main__":
    cli()





