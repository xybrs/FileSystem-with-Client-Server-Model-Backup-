#!/usr/bin/python

import sys
import glob, os
import threading

sys.path.append('./Code')
from fileSystem import multipleCLI

threads = []

def main():
    print("Welcome!")
    ####### First thread
    t1 = threading.Thread(target=multipleCLI,args = (r"Code\Scripts\firstScript.txt",))
    t2 = threading.Thread(target=multipleCLI,args = (r"Code\Scripts\secondScript.txt",))
    t3 = threading.Thread(target=multipleCLI,args = (r"Code\Scripts\thirdScript.txt",))
    t4 = threading.Thread(target=multipleCLI,args = (r"Code\Scripts\fourthScript.txt",))
    t5 = threading.Thread(target=multipleCLI,args = (r"Code\Scripts\experiment.txt",))

    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t5.start()

    t1.join()
    t2.join()
    t3.join()
    t4.join()
    t5.join()
    
def allFiles():
    import os
    for file in os.listdir(r"./Code/Scripts"):
        if file.endswith(".txt"):
            print(file)
            t = threading.Thread(target=multipleCLI, args = ("Code/Scripts/" + file,))
            threads.append(t)
    for fileThread in threads:
        fileThread.start()
    for fileThread in threads:
        fileThread.join()

if __name__ == "__main__":
    ####### First thread
    allFiles()