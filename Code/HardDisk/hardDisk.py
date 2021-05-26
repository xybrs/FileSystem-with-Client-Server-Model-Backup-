import json
import math
from os import write
import threading

dirDataLock = threading.Lock()
fileDatalock = threading.Lock()
fileSegmentLock = threading.Lock()
freeSegmentLock = threading.Lock()
segmentLock = threading.Lock()
class disk:
    #CONSTRUCTOR
    def __init__(self, fileName):
        #Variables
        self.diskData = {}
        self.fileData = {}
        self.dirData = {}
        self.segmentLength = 0
        self.noOfSegments = 0
        self.segmentOffset = []
        self.freeSegments = []
        self.disk = open(fileName,"r+")

        if self.isEmpty():                  #Setting Up if Disk is empty
            print("Disk is not Setup!\n")
            print("Setting Up Disk\n")
            self.setupDisk()
        else:                               #Setting Up otherwise
            self.setup()

    def setup(self):
        self.disk.seek(0)
        diskData = self.disk.readline()
        fileData = ""

        ### DISK DATA SETTING UP!
        self.diskData = json.loads(diskData) #Converting to dict object
        self.noOfSegments = self.diskData["Segments"]       #Setting segments
        self.segmentLength = self.diskData["SegmentLength"]
        self.segmentOffset = [i for i in range(0, (self.noOfSegments)*self.segmentLength+1, self.segmentLength)]

        ### SETTING UP LOCKS
        global segmentSemas
        segmentSemas = [threading.Semaphore(1)]*self.noOfSegments

        ### FILE DATA SETTING UP!
        fileDataSegments = self.diskData[""]
        for segment in fileDataSegments:
            fileData += self.readSeg(segment)
        self.fileData = json.loads(fileData)
        
        self.dirData = json.loads(self.readFile("dirData"))
        self.freeSegments = [i for i in range(0,self.noOfSegments)]
        for file in self.fileData:
            for segment in self.fileData[file][1]:
                self.freeSegments.remove(segment)
    def setupDisk(self):
        self.noOfSegments = int(input("Enter number of segments: "))
        self.segmentLength = int(input("Enter segment size(Greater than 85): "))
        self.segmentOffset = [i for i in range(0, (self.noOfSegments)*self.segmentLength+1, self.segmentLength)]
        self.createSegments()
        self.createDicts()

        ###Setting up segmentSemas
        global segmentSemas
        segmentSemas = [threading.Semaphore(1)]*self.noOfSegments
        print(segmentSemas)
    def createDicts(self):
        print(self.segmentOffset)
        self.diskData = {"Segments":self.noOfSegments,"SegmentLength":self.segmentLength,"":[1]}
        self.fileData = {"diskData": ["Null",[0]], "fileData": ["Null",[1]], "dirData": ["Null",[2]]}
        self.dirData = {"Root": [None, []]}

        self.writeToFile("diskData", json.dumps(self.diskData),0)
        self.writeToFile("fileData", json.dumps(self.fileData),0)
        self.writeToFile("dirData", json.dumps(self.dirData),0)
        self.freeSegments = [i for i in range (0, self.noOfSegments)]
        for file in self.fileData:
            for segment in self.fileData[file][1]:
                self.freeSegments.remove(segment)
                print("Segment " , segment , "Occupied!")
    
    def updatefileData(self):
        for segment in self.fileData["fileData"][1]:
            self.clearSegment(segment)
        self.writeToFile("fileData",json.dumps(self.fileData),0)
    def updateDirData(self):
        for segment in self.fileData["dirData"][1]:
            self.clearSegment(segment)
        self.writeToFile("dirData",json.dumps(self.dirData),0)

    def createSegments(self):
        for segment in range(self.noOfSegments):
            for char in range(self.segmentLength-2):
                self.disk.write(" ")
            self.disk.write("\n")
        self.disk.flush()
    def clearSegment(self, segNo):
        self.writeToSeg(segNo, " " * int(self.segmentLength - 2),0)
    def writeToSeg(self, segNo, text, loc):
        if (len(text) + loc > self.segmentLength-2):
            print("Error! Input is bigger than Segment. Truncating to size!")
            text = text[0:self.segmentLength-2-loc]
        segmentLock.acquire()
        segStart = self.segmentOffset[segNo]
        self.disk.seek(segStart + loc)
        segmentLock.release()  
        self.disk.write(text)
        self.disk.flush()
    def readSeg(self, segNo):
        segStart = self.segmentOffset[segNo]
        segmentLock.acquire()
        self.disk.seek(segStart)
        segmentLock.release()
        seg = self.disk.readline(self.segmentLength-2)
        return seg
    def assignSeg(self, fileName):
        if (len(self.freeSegments) == 0):
            print("No free Segment Available! Error!")
            return -1
        freeSegmentLock.acquire()                     #####LOCK
        freeSegment = self.freeSegments.pop(0)
        freeSegmentLock.release()                     #####RELEASE
        fileDatalock.acquire()
        self.fileData[fileName][1].append(freeSegment)
        fileDatalock.release()

        if (fileName == "fileData"):
            self.diskData[""].append(freeSegment)
            self.writeToFile("diskData", json.dumps(self.diskData),0)

        print("Segment No:" ,freeSegment , " assigned to File:" ,fileName + "\n\n")
        self.updatefileData()
        self.updatefileData()
    def freeSeg(self, segment):
        self.freeSegments.append(segment)
        self.clearSegment(segment)
        print("Segment No: ", segment, " freed!")

    def writeToFile(self, fileName, text, loc):
        if (len(text) + loc > (self.segmentLength-2) * len(self.fileData[fileName][1])): #Finding out if we need to assign new segments
            newSegmentsNeeded = math.trunc((len(text)+loc - self.segmentLength*len(self.fileData[fileName][1]))/self.segmentLength) + 1
            for i in range (0, newSegmentsNeeded):
                self.assignSeg(fileName)
        segment = math.trunc(loc/(self.segmentLength-2)) #Going to the starting Segment
        toWrite = text[0:self.segmentLength-2-loc]
        text = text[self.segmentLength-2-loc:]
        self.writeToSeg(self.fileData[fileName][1][segment],toWrite, loc)
        loc = 0
        segment += 1

        while (len(text) > (self.segmentLength -2)):
            toWrite = text[0:self.segmentLength-2]
            text = text[self.segmentLength-2-loc:]
            self.writeToSeg(self.fileData[fileName][1][segment],toWrite,0)
            segment += 1
        if text != "":
            self.writeToSeg(self.fileData[fileName][1][segment],text, 0)  #Writing the last segment
    def readFile(self, fileName):
        segments = self.fileData[fileName][1]
        file = ""
        for segment in segments:
            file += self.readSeg(segment)
        return file
    def clearFile(self, fileName):
        for segment in self.fileData[fileName][1]:
            self.clearSegment(segment)

    # TASK 1 & 2
    def createFile(self,fileName, dirName):

        if (dirName not in self.dirData):
            print("-----------------------------------------------")
            print("Invalid Directory name. Saving in Root instead.")
            print("-----------------------------------------------")
            dirName = "Root"
        
        dirDataLock.acquire()
        if (fileName in self.dirData[dirName][1]):
            print("--------------------------------------")
            print("File Already Exists in this Directory.")
            print("-------------Terminating--------------")
            dirDataLock.release()
            return -1
        self.dirData[dirName][1].append(fileName)
        dirDataLock.release()               ## DEBUGGING
        self.updateDirData()
        
        
        fileSegmentLock.acquire()
        self.fileData[fileName] = [dirName,[]]    
        fileSegmentLock.release()           ## DEBUGGING
        self.updatefileData()
        self.updatefileData()               ## DEBUGGING

    def deleteFile(self,fileName, dirName):
        
        fileDatalock.acquire()
        for segment in self.fileData[fileName][1]:
            self.freeSeg(segment)

        del self.fileData[fileName]
        fileDatalock.release()

        self.updatefileData()
        self.updatefileData()
        
        dirDataLock.acquire()
        self.dirData[dirName][1].remove(fileName)
        dirDataLock.release()
        self.updateDirData()
        
    # TASK 3
    def createDir(self,dirName,parentDir):
        if (parentDir not in self.dirData):
            parentDir = 'Root'
            print("-----------------------------------------------")
            print("Invalid Directory name. Saving in Root instead.")
            print("-----------------------------------------------")
        dirDataLock.acquire()
        self.dirData[parentDir][1].append(dirName)
        self.dirData[dirName] = [parentDir, []]
        dirDataLock.release()
        self.updateDirData()
    def deleteDir(self, dirName, parentDir):
        return 0

    # TASK 12
    def memMap(self):
        print("-----------Mem Map------------")
        print("----------Disk Data-----------")
        print(self.diskData)
        print("------------------------------")
        print("----------File Data-----------")
        print(self.fileData)
        print("------------------------------")
        print("----------Dir Data------------")
        print(self.dirData)
        print("------------------------------")
        print("--------SegmentOffset---------")
        print(self.segmentOffset)
        print("------------------------------")
        print("--------Segment Length--------")
        print(self.segmentLength)
        print("------------------------------")
        print("--------No. of Segments-------")
        print(self.noOfSegments)
        print("------------------------------")
        print("--------Free Segments---------")
        print(self.freeSegments)
        print("------------------------------")
        print("")
        print("")

        output = "\n"
        output += ("\n-----------Mem Map------------")
        output += ("\n----------Disk Data-----------")
        output += ("\n" + str(self.diskData))
        output += ("\n------------------------------")
        output += ("\n----------File Data-----------")
        output += ("\n" + str(self.fileData))
        output += ("\n------------------------------")
        output += ("\n----------Dir Data------------")
        output += ("\n" + str(self.dirData))
        output += ("\n------------------------------")
        output += ("\n--------SegmentOffset---------")
        output += ("\n" + str(self.segmentOffset))
        output += ("\n------------------------------")
        output += ("\n--------Segment Length--------")
        output += ("\n" + str(self.segmentLength))
        output += ("\n------------------------------")
        output += ("\n--------No. of Segments-------")
        output += ("\n" + str(self.noOfSegments))
        output += ("\n------------------------------")
        output += ("\n--------Free Segments---------")
        output += ("\n" + str(self.freeSegments))
        output += ("\n------------------------------" + "\n")
        return output
    def isEmpty(self):
        self.disk.seek(0)
        if not self.disk.read(1):
            self.disk.seek(0)
            return True
        self.disk.seek(0)
        return False

########CREATING OBJECT
try:
    hardDisk = disk("Code\hardDisk\hardDisk.txt")
except:
    hardDisk = disk("hardDisk\hardDisk.txt")
#print(segmentSemas)
#hardDisk.memMap()
#hardDisk.writeToFile("dirData", "Wow", 50)
