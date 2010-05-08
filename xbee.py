# By Amit Snyderman <amit@amitsnyderman.com>
# $Id: xbee.py,v 1.1 2009/01/20 18:23:01 cvs Exp $

import array

class xbee(object):
       
        START_IOPACKET   = '0x7e'
        SERIES1_IOPACKET = '0x83'
       
        def find_packet(serial):
                if hex(ord(serial.read())) == xbee.START_IOPACKET:
                        lengthMSB = ord(serial.read())
                        lengthLSB = ord(serial.read())
                        length = (lengthLSB + (lengthMSB << 8)) + 1
                        return serial.read(length)
                else:
                        return None
        find_packet = staticmethod(find_packet)
       
        def __init__(self, arg):
                self.digital_samples = []
                self.analog_samples = []
                self.init_with_packet(arg)
       
        def init_with_packet(self, p):
                p = [ord(c) for c in p]

                #print p
                #print len(p)
            
                self.app_id = hex(p[0])
               
                if self.app_id == xbee.SERIES1_IOPACKET:
                        addrMSB = p[1]
                        addrLSB = p[2]
                        self.address_16 = (addrMSB << 8) + addrLSB
                       
                        self.rssi = p[3]
                        self.address_broadcast = ((p[4] >> 1) & 0x01) == 1
                        self.pan_broadcast = ((p[4] >> 2) & 0x01) == 1
                       
                        self.total_samples = p[5]
                        self.channel_indicator_high = p[6]
                        self.channel_indicator_low = p[7]
                       
                        local_checksum = int(self.app_id, 16) + addrMSB + addrLSB + self.rssi + p[4] + self.total_samples + self.channel_indicator_high + self.channel_indicator_low
                       
                        for n in range(self.total_samples):
                                dataD = [-1] * 9
                                digital_channels = self.channel_indicator_low
                                digital = 0
                               
                                for i in range(len(dataD)):
                                        if (digital_channels & 1) == 1:
                                                dataD[i] = 0
                                                digital = 1
                                        digital_channels = digital_channels >> 1
                               
                                if (self.channel_indicator_high & 1) == 1:
                                        dataD[8] = 0
                                        digital = 1
                               
                                if digital:
                                        digMSB = p[8]
                                        digLSB = p[9]
                                        local_checksum += digMSB + digLSB
                                        dig = (digMSB << 8) + digLSB
                                        for i in range(len(dataD)):
                                                if dataD[i] == 0:
                                                        dataD[i] = dig & 1
                                                dig = dig >> 1
                               
                                self.digital_samples.append(dataD)
                               
                                analog_count = None
                                dataADC = [-1] * 6
                                analog_channels = self.channel_indicator_high >> 1
                                validanalog = 0
                                for i in range(len(dataADC)):
                                    if ((analog_channels>>i) & 1) == 1:
                                        validanalog += 1

                                for i in range(len(dataADC)):
                                        if (analog_channels & 1) == 1:
                                            analogchan = 0
                                            for j in range(i):
                                                if ((self.channel_indicator_high >> (j+1)) & 1) == 1:
                                                    analogchan += 1
                                            dataADCMSB = p[8 + validanalog * n * 2 + analogchan*2]
                                            dataADCLSB = p[8 + validanalog * n * 2 + analogchan*2 + 1]
                                            local_checksum += dataADCMSB + dataADCLSB
                                            dataADC[i] = ((dataADCMSB << 8) + dataADCLSB)# / 64
                                            #print "sample #"+str(n)+" for chan "+str(analogchan)+" = ["+str(dataADCMSB)+", "+str(dataADCLSB)+"] = "+str(dataADC[i])

                                            analog_count = i
                                        analog_channels = analog_channels >> 1
                               
                                self.analog_samples.append(dataADC)
                                #print dataADC
                               
                        #checksum = p[10 + analog_count * n]
                        #local_checksum = 0xff - local_checksum;
                       
                        # if (checksum - local_checksum != 0):
                        #       print "Checksum error! checksum: %s, local_checksum: %s" % (checksum, local_checksum)
       
        def __str__(self):
                return "<xbee {app_id: %s, address_16: %s, rssi: %s, address_broadcast: %s, pan_broadcast: %s, total_samples: %s, digital: %s, analog: %s}>" % (self.app_id, self.address_16, self.rssi, self.address_broadcast, self.pan_broadcast, self.total_samples, self.digital_samples, self.analog_samples)

