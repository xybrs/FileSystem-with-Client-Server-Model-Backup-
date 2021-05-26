#!/usr/bin/python
from fileSystem import multipleCLI
import threading

def main():
    ####### First thread
    t1 = threading.Thread(target=multipleCLI,args = (r"Scripts\firstScript.txt",))
    t2 = threading.Thread(target=multipleCLI,args = (r"Scripts\secondScript.txt",))
    t3 = threading.Thread(target=multipleCLI,args = (r"Scripts\thirdScript.txt",))
    t4 = threading.Thread(target=multipleCLI,args = (r"Scripts\fourthScript.txt",))
    t5 = threading.Thread(target=multipleCLI,args = (r"Scripts\experiment.txt",))

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
    

if __name__ == "__main__":
    ####### First thread
    main()