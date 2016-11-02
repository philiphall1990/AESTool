__author__ = 'admin'
import io as io
import numpy as np
import binascii
import re
import os as os

class Encrypt():
    INPUT_BLOCK_SIZE = 128
    KEY_SIZE = 256
    Nb = INPUT_BLOCK_SIZE / 32
    Nk = KEY_SIZE / 32
    RCON = (0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80,0x1b,0x36)

    SBOX= (
            0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5, 0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76,
            0xCA, 0x82, 0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0, 0xAD, 0xD4, 0xA2, 0xAF, 0x9C, 0xA4, 0x72, 0xC0,
            0xB7, 0xFD, 0x93, 0x26, 0x36, 0x3F, 0xF7, 0xCC, 0x34, 0xA5, 0xE5, 0xF1, 0x71, 0xD8, 0x31, 0x15,
            0x04, 0xC7, 0x23, 0xC3, 0x18, 0x96, 0x05, 0x9A, 0x07, 0x12, 0x80, 0xE2, 0xEB, 0x27, 0xB2, 0x75,
            0x09, 0x83, 0x2C, 0x1A, 0x1B, 0x6E, 0x5A, 0xA0, 0x52, 0x3B, 0xD6, 0xB3, 0x29, 0xE3, 0x2F, 0x84,
            0x53, 0xD1, 0x00, 0xED, 0x20, 0xFC, 0xB1, 0x5B, 0x6A, 0xCB, 0xBE, 0x39, 0x4A, 0x4C, 0x58, 0xCF,
            0xD0, 0xEF, 0xAA, 0xFB, 0x43, 0x4D, 0x33, 0x85, 0x45, 0xF9, 0x02, 0x7F, 0x50, 0x3C, 0x9F, 0xA8,
            0x51, 0xA3, 0x40, 0x8F, 0x92, 0x9D, 0x38, 0xF5, 0xBC, 0xB6, 0xDA, 0x21, 0x10, 0xFF, 0xF3, 0xD2,
            0xCD, 0x0C, 0x13, 0xEC, 0x5F, 0x97, 0x44, 0x17, 0xC4, 0xA7, 0x7E, 0x3D, 0x64, 0x5D, 0x19, 0x73,
            0x60, 0x81, 0x4F, 0xDC, 0x22, 0x2A, 0x90, 0x88, 0x46, 0xEE, 0xB8, 0x14, 0xDE, 0x5E, 0x0B, 0xDB,
            0xE0, 0x32, 0x3A, 0x0A, 0x49, 0x06, 0x24, 0x5C, 0xC2, 0xD3, 0xAC, 0x62, 0x91, 0x95, 0xE4, 0x79,
            0xE7, 0xC8, 0x37, 0x6D, 0x8D, 0xD5, 0x4E, 0xA9, 0x6C, 0x56, 0xF4, 0xEA, 0x65, 0x7A, 0xAE, 0x08,
            0xBA, 0x78, 0x25, 0x2E, 0x1C, 0xA6, 0xB4, 0xC6, 0xE8, 0xDD, 0x74, 0x1F, 0x4B, 0xBD, 0x8B, 0x8A,
            0x70, 0x3E, 0xB5, 0x66, 0x48, 0x03, 0xF6, 0x0E, 0x61, 0x35, 0x57, 0xB9, 0x86, 0xC1, 0x1D, 0x9E,
            0xE1, 0xF8, 0x98, 0x11, 0x69, 0xD9, 0x8E, 0x94, 0x9B, 0x1E, 0x87, 0xE9, 0xCE, 0x55, 0x28, 0xDF,
            0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68, 0x41, 0x99, 0x2D, 0x0F, 0xB0, 0x54, 0xBB, 0x16
            )
    SBOX_INV = (
            0x52, 0x09, 0x6A, 0xD5, 0x30, 0x36, 0xA5, 0x38, 0xBF, 0x40, 0xA3, 0x9E, 0x81, 0xF3, 0xD7, 0xFB,
            0x7C, 0xE3, 0x39, 0x82, 0x9B, 0x2F, 0xFF, 0x87, 0x34, 0x8E, 0x43, 0x44, 0xC4, 0xDE, 0xE9, 0xCB,
            0x54, 0x7B, 0x94, 0x32, 0xA6, 0xC2, 0x23, 0x3D, 0xEE, 0x4C, 0x95, 0x0B, 0x42, 0xFA, 0xC3, 0x4E,
            0x08, 0x2E, 0xA1, 0x66, 0x28, 0xD9, 0x24, 0xB2, 0x76, 0x5B, 0xA2, 0x49, 0x6D, 0x8B, 0xD1, 0x25,
            0x72, 0xF8, 0xF6, 0x64, 0x86, 0x68, 0x98, 0x16, 0xD4, 0xA4, 0x5C, 0xCC, 0x5D, 0x65, 0xB6, 0x92,
            0x6C, 0x70, 0x48, 0x50, 0xFD, 0xED, 0xB9, 0xDA, 0x5E, 0x15, 0x46, 0x57, 0xA7, 0x8D, 0x9D, 0x84,
            0x90, 0xD8, 0xAB, 0x00, 0x8C, 0xBC, 0xD3, 0x0A, 0xF7, 0xE4, 0x58, 0x05, 0xB8, 0xB3, 0x45, 0x06,
            0xD0, 0x2C, 0x1E, 0x8F, 0xCA, 0x3F, 0x0F, 0x02, 0xC1, 0xAF, 0xBD, 0x03, 0x01, 0x13, 0x8A, 0x6B,
            0x3A, 0x91, 0x11, 0x41, 0x4F, 0x67, 0xDC, 0xEA, 0x97, 0xF2, 0xCF, 0xCE, 0xF0, 0xB4, 0xE6, 0x73,
            0x96, 0xAC, 0x74, 0x22, 0xE7, 0xAD, 0x35, 0x85, 0xE2, 0xF9, 0x37, 0xE8, 0x1C, 0x75, 0xDF, 0x6E,
            0x47, 0xF1, 0x1A, 0x71, 0x1D, 0x29, 0xC5, 0x89, 0x6F, 0xB7, 0x62, 0x0E, 0xAA, 0x18, 0xBE, 0x1B,
            0xFC, 0x56, 0x3E, 0x4B, 0xC6, 0xD2, 0x79, 0x20, 0x9A, 0xDB, 0xC0, 0xFE, 0x78, 0xCD, 0x5A, 0xF4,
            0x1F, 0xDD, 0xA8, 0x33, 0x88, 0x07, 0xC7, 0x31, 0xB1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xEC, 0x5F,
            0x60, 0x51, 0x7F, 0xA9, 0x19, 0xB5, 0x4A, 0x0D, 0x2D, 0xE5, 0x7A, 0x9F, 0x93, 0xC9, 0x9C, 0xEF,
            0xA0, 0xE0, 0x3B, 0x4D, 0xAE, 0x2A, 0xF5, 0xB0, 0xC8, 0xEB, 0xBB, 0x3C, 0x83, 0x53, 0x99, 0x61,
            0x17, 0x2B, 0x04, 0x7E, 0xBA, 0x77, 0xD6, 0x26, 0xE1, 0x69, 0x14, 0x63, 0x55, 0x21, 0x0C, 0x7D
            )
    THREEXTABLE = ( 0x00,0x03,0x06,0x05,0x0c,0x0f,0x0a,0x09,0x18,0x1b,0x1e,0x1d,0x14,0x17,0x12,0x11,
            0x30,0x33,0x36,0x35,0x3c,0x3f,0x3a,0x39,0x28,0x2b,0x2e,0x2d,0x24,0x27,0x22,0x21,
            0x60,0x63,0x66,0x65,0x6c,0x6f,0x6a,0x69,0x78,0x7b,0x7e,0x7d,0x74,0x77,0x72,0x71,
            0x50,0x53,0x56,0x55,0x5c,0x5f,0x5a,0x59,0x48,0x4b,0x4e,0x4d,0x44,0x47,0x42,0x41,
            0xc0,0xc3,0xc6,0xc5,0xcc,0xcf,0xca,0xc9,0xd8,0xdb,0xde,0xdd,0xd4,0xd7,0xd2,0xd1,
            0xf0,0xf3,0xf6,0xf5,0xfc,0xff,0xfa,0xf9,0xe8,0xeb,0xee,0xed,0xe4,0xe7,0xe2,0xe1,
            0xa0,0xa3,0xa6,0xa5,0xac,0xaf,0xaa,0xa9,0xb8,0xbb,0xbe,0xbd,0xb4,0xb7,0xb2,0xb1,
            0x90,0x93,0x96,0x95,0x9c,0x9f,0x9a,0x99,0x88,0x8b,0x8e,0x8d,0x84,0x87,0x82,0x81,
            0x9b,0x98,0x9d,0x9e,0x97,0x94,0x91,0x92,0x83,0x80,0x85,0x86,0x8f,0x8c,0x89,0x8a,
            0xab,0xa8,0xad,0xae,0xa7,0xa4,0xa1,0xa2,0xb3,0xb0,0xb5,0xb6,0xbf,0xbc,0xb9,0xba,
            0xfb,0xf8,0xfd,0xfe,0xf7,0xf4,0xf1,0xf2,0xe3,0xe0,0xe5,0xe6,0xef,0xec,0xe9,0xea,
            0xcb,0xc8,0xcd,0xce,0xc7,0xc4,0xc1,0xc2,0xd3,0xd0,0xd5,0xd6,0xdf,0xdc,0xd9,0xda,
            0x5b,0x58,0x5d,0x5e,0x57,0x54,0x51,0x52,0x43,0x40,0x45,0x46,0x4f,0x4c,0x49,0x4a,
            0x6b,0x68,0x6d,0x6e,0x67,0x64,0x61,0x62,0x73,0x70,0x75,0x76,0x7f,0x7c,0x79,0x7a,
            0x3b,0x38,0x3d,0x3e,0x37,0x34,0x31,0x32,0x23,0x20,0x25,0x26,0x2f,0x2c,0x29,0x2a,
            0x0b,0x08,0x0d,0x0e,0x07,0x04,0x01,0x02,0x13,0x10,0x15,0x16,0x1f,0x1c,0x19,0x1a
            )

    def encrypt(self, inputfile, key):
        output = []
        keyschedule = self.keyExpansion(key)
        iv = np.array(np.random.random_integers(0, 1, self.INPUT_BLOCK_SIZE)).reshape(16,8)  # randomly generate bits of equal size to block size
        priorstate = iv
        with io.open(inputfile,mode='rb') as f:
                byte = []
                try:
                    for i in range(0,16):
                        byte.append(f.read(1))
                    while byte[15]:
                        state = self.decodeandBlockChain(byte,priorstate)
                        output.append(self.round(state,keyschedule))
                        try:
                            byte = []
                            for i in range(0,16):
                                byte.append(f.read(1))

                            priorstate = np.asarray(state).reshape(16,8)
                        except Exception as e:
                            print("Error: {1}".format(e))
                        finally:
                            f.close()
                except Exception as e:
                    print("Error: {1}".format(e))
                finally:
                    f.close()

        path = input("Please select file path for encrypted file:\n")
        while os.path.exists(path):
            path = input("Sorry, this file already exists, please choose a unique file path:\n")
        with io.open(path,mode='ab') as f:
           for i in iv:
                   f.write(bytearray(int(self.bitArrayToBytes(i),16)))
           for i in output:
               for x in i:
                   f.write(bytearray(int(x,16)))



    def decodeandBlockChain(self, byteArray, priorstate):
        block = []
        state = []
        for i in range(0,16):
            block.append(binascii.hexlify(byteArray[i]).decode())
            block[i] = self.bitArrayToBytes(self.byteXOR(self.bytesToBits(block[i]),priorstate[i]))
            if (i+1) % 4 == 0:
                state.append([block[i-3],block[i-2],block[i-1],block[i]])
        return state

    def round(self,state, keyschedule):
            for i in range(0,len(state)):
                for x in range(len(state[i])):
                    newthing = hex(self.SBOX[int(state[i][x],16)])
                    state[i][x] = newthing
            state = self.shiftRows(state)
            state = self.mixColumns(state)
            state = np.asarray(state).reshape(16,8)
            finalstate = []
            for i in range(0, len(state)):
                    temp = self.byteXOR(state[i],self.bytesToBits(keyschedule[i]))
                    finalstate.append(self.bitArrayToBytes(temp))
            return finalstate



    def byteXOR(self, byte1, byte2):
        output = []
        if len(byte1) < 8:
            byte1 = ['0' + byte1]
        if len(byte2) < 8:
            byte2 = '0' + byte2
        for i in range(0, len(byte1), 1):
            output.append(byte1[i] ^ byte2[i])
        return output

    def bitArrayToBytes(self, bits):
        string = ''
        for x in bits:
            string += str(int(x))
        return hex(int(string, 2))

    def bitStringtoBytes(self,bits):
        return hex(int(bits.replace('0b',''),2))

    def bytesToBits(self, bytes):
        intarray = []
        string = bin(int(str(bytes), 16)).replace('0b','')
        for i in string:
            intarray.append(int(i))
        while len(intarray) < 8:
            intarray.insert(0,0)
        while len(intarray) > 8:
            intarray.pop()
        return intarray

    def shiftRows(self, state):

        def invShiftRows(self, state):
            for i in range(0, 4):
                tempstate = []
                othertempstate = []
                if i > 0:
                    x = 0
                    n = 0
                    y = 0
                    for x in range(0, i):
                        tempstate.append(state[i][x])
                    for x in range(i, 4):
                        othertempstate.append(state[i][x])
                    for n in range(0, len(othertempstate)):
                        state[i][n] = othertempstate[n]
                    for y in range(n + 1, 4):
                        state[i][y] = tempstate[y - len(othertempstate)]

            return state

    def mixColumns(self, state):
        for i in range(0, 4):
            for n in range(0, 4):
                tempbits = self.bytesToBits(state[n][i])
                if i == 0:
                    if n == 0:
                        tempbits = self.timesTwo(tempbits)
                    elif n == 1:
                        tempbits = self.timesThree(tempbits)
                if i == 1:
                    if n == 1:
                        tempbits = self.timesTwo(tempbits)
                    elif n == 2:
                        tempbits = self.timesThree(tempbits)
                if i == 2:
                    if n == 2:
                        tempbits = self.timesTwo(tempbits)
                    if n == 3:
                        tempbits = self.timesThree(tempbits)
                if i == 3:
                    if n == 0:
                        tempbits = self.timesThree(tempbits)
                    if n == 3:
                        tempbits = self.timesTwo(tempbits)
                state[n][i] = tempbits

        return state


    def timesThree(self, byte):
        return self.bytesToBits(self.THREEXTABLE[int(str(byte).replace('[', '').replace(']','').replace(',', '').replace(' ', ''),2)])


    def timesTwo(self, bits):
        for i in range(0,7):
            if bits[0] == 1:
                bits[i] = bits[i + 1]
                bits[7] = 0
                bits = self.byteXOR(bits, [0,0,0,1,1,0,1,1])
            else:
                bits[i] = bits[i + 1]
                bits[7] = 0

        return bits


    def keyExpansion(self, key):
        word = []
        bytes = bytearray(key, encoding='ascii')
        key = []
        for i in bytes:
            key.append(bin(int(i)))
        for i in key:
            word.append('0x00')
        rconCounter = 0
        for x in range(12,44,4):
            holder = word[x:x+4]
            if (x+4) % 16 == 0:
                holder = []
                for i in self.subWord(self.rotWord([word[x],word[x+1],word[x+2],word[x+3]])):
                    holder.append(i)
                holder[0] = self.bitArrayToBytes(self.byteXOR(self.bytesToBits(holder[0]),self.bytesToBits(self.RCON[rconCounter])))
                rconCounter +=1
            for i in range(0,4):
                word.append(self.bitArrayToBytes(self.byteXOR(self.bytesToBits(holder[i]),self.bytesToBits(word[i + (x-12)]))))


        return word



    def rotWord(self, word):
        temp = word[0]
        for i in range(1,4):
            word[i - 1] = word[i]
        word[3] = temp
        return word

    def subWord(self,word):
        array = []
        for byte in word:
            index = int(byte.replace('0x',''),16)
            array.append(hex(self.SBOX[index]))
        return array