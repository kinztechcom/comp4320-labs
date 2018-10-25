import socket
import sys
import struct


class Buffer:

    def __init__(self, data=[]):
        self.position = 0
        self.buffer = bytearray(data)

    def readWord(self):
        x1 = (self.buffer[self.position] & 255) << 24
        self.movePos()
        x2 = (self.buffer[self.position] & 255) << 16
        self.position = self.position + 1
        x3 = (self.buffer[self.position] & 255) << 8
        self.movePos()
        x4 = (self.buffer[self.position] & 255)
        self.movePos()
        return x1 + x2 + x3 + x4

    def readByte(self):
        x = self.buffer[self.position] & 255
        self.movePos()
        return x

    def putWord(self, data):
        x1 = data >> 24
        self.buffer.append(x1)
        self.movePos()
        x2 = (data >> 16) & 0x000000ff
        self.buffer.append(x2)
        self.movePos()
        x3 = (data >> 8) & 0x000000ff
        self.buffer.append(x3)
        self.movePos()
        x4 = data & 0x000000ff
        self.buffer.append(x4)
        self.movePos()

    def putByte(self, data):
        x = data & 0x000000ff
        self.buffer.append(x)
        self.movePos()

    def movePos(self, amount=1):
        self.position = self.position + amount


class Response:
    def __init__(self, response):
        self.response = response
        self.buffer = Buffer(self.response)
        self.readResponse()

    def readResponse(self):
        self.gid = self.buffer.readByte()
        self.magic = self.buffer.readWord()
        self.rid = self.buffer.readByte()
        self.nextSlaveIP = self.buffer.readWord()
        self.dottedIP = socket.inet_ntoa(struct.pack('>L', self.nextSlaveIP))

    def printResponse(self):
        print "Group ID of master: ", self.gid
        print "My ring ID: ", self.rid
        print "IP Address:  ", self.dottedIP


if (len(sys.argv) != 3):
    print "Error: Incorrect arguments. Use format: Slave MasterHostname MasterPort#"
    sys.exit()

hostname = sys.argv[1]
port = int(sys.argv[2])
groupID = 12
magicNumber = '0x4a6f7921'

buffer = Buffer()

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect((hostname, port))

buffer.putByte(groupID)
buffer.putWord(int(magicNumber, 16))

# send request to server
client.send(buffer.buffer)

# Receive response from server
response = client.recv(4096)
resp = Response(response)
resp.printResponse()