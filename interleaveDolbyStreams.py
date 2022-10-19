#!/usr/bin/env python3
import argparse, os, sys

class getBitStreams(object):
	def __init__(self):
		self.parseArgument()
		self.checkFileExtensions()
		self.readAC3()
		self.readMLP()

	def parseArgument(self):
		parser=argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,description=helpDescription)
		parser.add_argument("AC3", help="the Dolby Digital .ac3 file")
		parser.add_argument("THD", help="the Dolby TrueHD (MLP) .thd file")
		parser.add_argument("-o", help="the name of the interleaved .thd+ac3 file", action="store", dest="output")
		args=parser.parse_args()
		self.fileName=[args.AC3,args.THD]
		self.out=args.output

	def checkFileExtensions(self):
		if not os.path.basename(self.fileName[0]).lower().endswith(".ac3"):
			sys.exit("Error: The AC3 file doesn't have a .ac3 extension.")
		if not os.path.basename(self.fileName[1]).lower().endswith(".thd"):
			sys.exit("Error: The MLP file doesn't have a .thd extension.")

	def readAC3(self):
		syncWordAC3=bytearray.fromhex('0b77')
		try:
			stream=open(self.fileName[0], 'rb')
			getBitStreams.bitStreamAC3=bytearray(stream.read())
			stream.close()
		except IOError as e:
			sys.exit("Error: %s: %s." % (e.strerror, e.filename))
		if getBitStreams.bitStreamAC3[0:2]!=syncWordAC3:
			sys.exit("Error: The .ac3 file doesn't start with the AC3 sync word.")

	def readMLP(self):
		formatSyncMLP=bytearray.fromhex('f8726fba')
		try:
			stream=open(self.fileName[1], 'rb')
			getBitStreams.bitStreamMLP=bytearray(stream.read())
			stream.close()
		except IOError as e:
			sys.exit("Error: %s: %s." % (e.strerror, e.filename))
		if getBitStreams.bitStreamMLP[4:8]!=formatSyncMLP:
			sys.exit("Error: The .thd file doesn't have the major format sync.")

class splitDolbyDigitalFrames(object):
	def __init__(self):
		self.checkSamplingFrequency()
		self.getFrameSize()
		self.splitFrames()

	def checkSamplingFrequency(self):
		twoMSBOperand=bytearray.fromhex('c0')
		self.codeByte=getBitStreams.bitStreamAC3[4:5]
		if self.codeByte[0]&twoMSBOperand[0]!=0:
			sys.exit("Error: The AC3 bit stream has an unsupported sampling frequency.")

	def getFrameSize(self):
		words=[64,80,96,112,128,160,192,224,256,320,384,448,512,640,768,896,1024,1152,1280]
		sixLSBOperand=bytearray.fromhex('3f')
		frameSizeCode=(self.codeByte[0]&sixLSBOperand[0])>>1
		self.frameSize=words[frameSizeCode]*2

	def splitFrames(self):
		if len(getBitStreams.bitStreamAC3)%self.frameSize!=0:
			sys.exit("Error: There's a problem with the AC3 frames.")
		numberOfFrames=int(len(getBitStreams.bitStreamAC3)/self.frameSize)
		splitDolbyDigitalFrames.frameList=[getBitStreams.bitStreamAC3[i:i+self.frameSize] for i in range(
			0, len(getBitStreams.bitStreamAC3), self.frameSize)]

class splitAccessHeaders(object):
	def __init__(self):
		splitAccessHeaders.formattedAccessHeaders=[]
		self.accessHeaderList=[]
		self.startByte=0
		self.fourLSBOperand=bytearray.fromhex('0f')
		self.splitAccessHeaderLoop()
		self.formatAccessHeaders()
		if len(self.accessHeaderList)%192!=0:
			self.formatLeftOverAccessHeaders()

	def getAccessUnitLength(self):
		accessUnitWordLength=getBitStreams.bitStreamMLP[self.startByte:self.startByte+2]
		accessUnitWordLength[0]=getBitStreams.bitStreamMLP[self.startByte]&self.fourLSBOperand[0]
		self.accessUnitLength=int.from_bytes(accessUnitWordLength, 'big')*2

	def splitAccessHeaderLoop(self):
		while self.startByte<len(getBitStreams.bitStreamMLP):
			self.getAccessUnitLength()
			self.accessHeaderList.append(getBitStreams.bitStreamMLP[self.startByte:self.startByte+self.accessUnitLength])
			self.startByte+=self.accessUnitLength

	def formatAccessHeaders(self):
		numberOfSegments=len(self.accessHeaderList)//192
		for i in range(0, numberOfSegments*192, 192):
			temp=self.accessHeaderList[i:i+192]
			splitAccessHeaders.formattedAccessHeaders.append(b''.join(temp[0:39]))
			splitAccessHeaders.formattedAccessHeaders.append(b''.join(temp[39:77]))
			splitAccessHeaders.formattedAccessHeaders.append(b''.join(temp[77:116]))
			splitAccessHeaders.formattedAccessHeaders.append(b''.join(temp[116:154]))
			splitAccessHeaders.formattedAccessHeaders.append(b''.join(temp[154:192]))

	def formatLeftOverAccessHeaders(self):
		fullLength=len(self.accessHeaderList)
		startIndex=(fullLength//192)*192
		temp=self.accessHeaderList[startIndex:fullLength]
		tempLength=len(temp)
		if tempLength<=39:
			splitAccessHeaders.formattedAccessHeaders.append(b''.join(temp[0:tempLength]))
		elif tempLength<=77:
			splitAccessHeaders.formattedAccessHeaders.append(b''.join(temp[0:39]))
			splitAccessHeaders.formattedAccessHeaders.append(b''.join(temp[39:tempLength]))
		elif tempLength<=116:
			splitAccessHeaders.formattedAccessHeaders.append(b''.join(temp[0:39]))
			splitAccessHeaders.formattedAccessHeaders.append(b''.join(temp[39:77]))
			splitAccessHeaders.formattedAccessHeaders.append(b''.join(temp[77:tempLength]))
		elif tempLength<=154:
			splitAccessHeaders.formattedAccessHeaders.append(b''.join(temp[0:39]))
			splitAccessHeaders.formattedAccessHeaders.append(b''.join(temp[39:77]))
			splitAccessHeaders.formattedAccessHeaders.append(b''.join(temp[77:116]))
			splitAccessHeaders.formattedAccessHeaders.append(b''.join(temp[116:tempLength]))
		else:
			splitAccessHeaders.formattedAccessHeaders.append(b''.join(temp[0:39]))
			splitAccessHeaders.formattedAccessHeaders.append(b''.join(temp[39:77]))
			splitAccessHeaders.formattedAccessHeaders.append(b''.join(temp[77:116]))
			splitAccessHeaders.formattedAccessHeaders.append(b''.join(temp[116:154]))
			splitAccessHeaders.formattedAccessHeaders.append(b''.join(temp[154:tempLength]))

class interleaveBitStreams(object):
	def __init__(self):
		self.findMinMaxLengths()
		self.createInterleavedList()
		self.interleavedBitStream=b''.join(self.interleavedList)

	def findMinMaxLengths(self):
		self.lenDD=len(splitDolbyDigitalFrames.frameList)
		self.lenMLP=len(splitAccessHeaders.formattedAccessHeaders)
		self.minimum=min(self.lenDD, self.lenMLP)
		self.maximum=max(self.lenDD, self.lenMLP)

	def createInterleavedList(self):
		self.interleavedList=[]
		for i in range(self.minimum):
			self.interleavedList.append(splitDolbyDigitalFrames.frameList[i])
			self.interleavedList.append(splitAccessHeaders.formattedAccessHeaders[i])
		if self.lenDD!=self.lenMLP:
			for i in range(self.minimum, self.maximum):
				if i<self.lenDD:
					self.interleavedList.append(splitDolbyDigitalFrames.frameList[i])
				if i<self.lenMLP:
					self.interleavedList.append(splitAccessHeaders.formattedAccessHeaders[i])

def getOutputFileName():
	if getStream.out==None:
		fileName='output.thd+ac3'
	else:
		if os.path.basename(getStream.out).lower().endswith('.thd+ac3'):
			fileName=getStream.out
		else:
			fileName=getStream.out+'.thd+ac3'
	return fileName

def writeBitStream(bitStream, fileName):
	outputFile=open(fileName, 'wb')
	outputFile.write(bitStream)
	outputFile.close()

helpDescription="""
Interleave the bitstreams of an AC3 (Dolby Digital) file and a THD (Dolby TrueHD
or MLP) file to create a THD+AC3 file compatible with tsMuxer and blu-ray.\n
If a name for the THD+AC3 file isn't provided with the -o argument, the file
name will automatically be output.thd+ac3\n
Only AC3 files with a sampling frequency of 48 kHz are supported.\n
"""

getStream=getBitStreams()
splitFrames=splitDolbyDigitalFrames()
splitMLP=splitAccessHeaders()
interleaveStreams=interleaveBitStreams()
writeBitStream(interleaveStreams.interleavedBitStream, getOutputFileName())
