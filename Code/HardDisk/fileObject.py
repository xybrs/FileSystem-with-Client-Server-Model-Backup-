from hardDisk import hardDisk

class fileInDisk:

    #TASK 6
    def __init__(self, fileName):
        self.fileName = fileName
        self.fileInfo = hardDisk.fileData[fileName]
        self.fileData = hardDisk.readFile(fileName)

    def updatefileData(self):
        self.fileData = hardDisk.readFile(self.fileName)
    #TASK 8
    def appendToFile(self, text):
        hardDisk.writeToFile(self.fileName, text, len(self.fileData.rstrip()))
        self.fileData = self.fileData[0:len(self.fileData.rstrip())] +  text + self.fileData[len(self.fileData.rstrip()) + len(text): ]
    def writeToFile(self, text):
        hardDisk.writeToFile(self.fileName, text, 0) ### Overwriting at File
        self.fileData = text + self.fileData[len(text):] 
    def writeToFileAtLoc(self,text,loc):
        hardDisk.writeToFile(self.fileName, text, loc)
        self.fileData = self.fileData[0:loc] + text + self.fileData[loc+len(text):]
    def write(self, text, loc, mode):
        if mode == 'a':
            self.appendToFile(text)
        elif mode == 'w':
            self.writeToFile(text)
        elif mode == 'W':
            self.writeToFileAtLoc(text,loc)

    #TASK 9
    def readFrom(self):
        self.updatefileData()
        return self.fileData
    def readFromSeg(self,start,size):
        self.updatefileData()
        return self.fileData[start:start+size]

    #TASK 10
    def truncateFile(self, size):
        hardDisk.clearFile(self.fileName)
        #space = " " * int(size - len(self.fileData))
        self.fileData = self.fileData[0:size] #+ space
        print(self.fileData)
        self.writeToFile(self.fileData)

    #TASK 7
    def saveFile(self):
        hardDisk.writeToFile(self.fileName, self.fileData, 0)