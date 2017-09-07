#!/usr/bin/env python
#

from encoder import *
from location import *
from conversions import *
from parity import *
from HackRF import HackRF
import os

###############################################################

# Copyright (C) 2017 Linar Yusupov

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import numpy
#from scipy.signal import hilbert

def df17_pos_rep_encode(ca, icao, tc, ss, nicsb, alt, time, lat, lon, surface):

    format = 17 #The format type of an ADSB message

    enc_alt =	encode_alt_modes(alt, surface)
    #print "Alt(%r): %X " % (surface, enc_alt)

    #encode that position
    (evenenclat, evenenclon) = cpr_encode(lat, lon, False, surface)
    (oddenclat, oddenclon)   = cpr_encode(lat, lon, True, surface)

    #print "Even Lat/Lon: %X/%X " % (evenenclat, evenenclon)
    #print "Odd  Lat/Lon: %X/%X " % (oddenclat, oddenclon)

    ff = 0
    df17_even_bytes = []
    df17_even_bytes.append((format<<3) | ca)
    df17_even_bytes.append((icao>>16) & 0xff)
    df17_even_bytes.append((icao>> 8) & 0xff)
    df17_even_bytes.append((icao    ) & 0xff)
    # data
    df17_even_bytes.append((tc<<3) | (ss<<1) | nicsb)
    df17_even_bytes.append((enc_alt>>4) & 0xff)
    df17_even_bytes.append((enc_alt & 0xf) << 4 | (time<<3) | (ff<<2) | (evenenclat>>15))
    df17_even_bytes.append((evenenclat>>7) & 0xff)    
    df17_even_bytes.append(((evenenclat & 0x7f) << 1) | (evenenclon>>16))  
    df17_even_bytes.append((evenenclon>>8) & 0xff)   
    df17_even_bytes.append((evenenclon   ) & 0xff)

    df17_str = "{0:02x}{1:02x}{2:02x}{3:02x}{4:02x}{5:02x}{6:02x}{7:02x}{8:02x}{9:02x}{10:02x}".format(*df17_even_bytes[0:11])
    #print df17_str , "%X" % bin2int(crc(df17_str+"000000", encode=True)) , "%X" % get_parity(hex2bin(df17_str+"000000"), extended=True)
    df17_crc = bin2int(crc(df17_str+"000000", encode=True))

    df17_even_bytes.append((df17_crc>>16) & 0xff)
    df17_even_bytes.append((df17_crc>> 8) & 0xff)
    df17_even_bytes.append((df17_crc    ) & 0xff)
 
    ff = 1
    df17_odd_bytes = []
    df17_odd_bytes.append((format<<3) | ca)
    df17_odd_bytes.append((icao>>16) & 0xff)
    df17_odd_bytes.append((icao>> 8) & 0xff)
    df17_odd_bytes.append((icao    ) & 0xff)
    # data
    df17_odd_bytes.append((tc<<3) | (ss<<1) | nicsb)
    df17_odd_bytes.append((enc_alt>>4) & 0xff)
    df17_odd_bytes.append((enc_alt & 0xf) << 4 | (time<<3) | (ff<<2) | (oddenclat>>15))
    df17_odd_bytes.append((oddenclat>>7) & 0xff)    
    df17_odd_bytes.append(((oddenclat & 0x7f) << 1) | (oddenclon>>16))  
    df17_odd_bytes.append((oddenclon>>8) & 0xff)   
    df17_odd_bytes.append((oddenclon   ) & 0xff)

    df17_str = "{0:02x}{1:02x}{2:02x}{3:02x}{4:02x}{5:02x}{6:02x}{7:02x}{8:02x}{9:02x}{10:02x}".format(*df17_odd_bytes[0:11])
    df17_crc = bin2int(crc(df17_str+"000000", encode=True))

    df17_odd_bytes.append((df17_crc>>16) & 0xff)
    df17_odd_bytes.append((df17_crc>> 8) & 0xff)
    df17_odd_bytes.append((df17_crc    ) & 0xff)    
    
    return (df17_even_bytes, df17_odd_bytes)

def frame_1090es_ppm_modulate(even, odd):
    ppm = [ ]

    for i in range(48):    # pause
        ppm.append( 0 )

    ppm.append( 0xA1 )   # preamble
    ppm.append( 0x40 )
    
    for i in range(len(even)):
        word16 = numpy.packbits(manchester_encode(~even[i]))
        ppm.append(word16[0])
        ppm.append(word16[1])


    for i in range(100):    # pause
        ppm.append( 0 )

    ppm.append( 0xA1 )   # preamble
    ppm.append( 0x40 )

    for i in range(len(odd)):
        word16 = numpy.packbits(manchester_encode(~odd[i]))
        ppm.append(word16[0])
        ppm.append(word16[1])

    for i in range(48):    # pause
        ppm.append( 0 )

    #print '[{}]'.format(', '.join(hex(x) for x in ppm))
    
    return bytearray(ppm)


    
if __name__ == "__main__":

    from sys import argv, exit
    
    argc = len(argv)
    if argc != 5:
      print
      print 'Usage: '+ argv[0] +'  <ICAO> <Latitude> <Longtitude> <Altitude>'
      print
      print '    Example: '+ argv[0] +'  0xABCDEF 12.34 56.78 9999.0'
      print
      exit(2)

    icao = int(argv[1], 16)
    lat = float(argv[2])
    lon = float(argv[3])
    alt = float(argv[4])

    ca = 5 # Capability 
    tc = 11 # Type Code see: https://adsb-decode-guide.readthedocs.io/en/latest/content/introduction.html#ads-b-message-types
    ss = 0 # Surveillance status
    nicsb = 0 # NIC supplement-B
    time = 0       
    surface = False

    (df17_even, df17_odd) = df17_pos_rep_encode(ca, icao, tc, ss, nicsb, alt, time, lat, lon, surface)

    #print ''.join(format(x, '02x') for x in df17_even)
    #print ''.join(format(x, '02x') for x in df17_odd)

    df17_array = frame_1090es_ppm_modulate(df17_even, df17_odd)

    #OutFile = open("filename.bin", "wb")
    #OutFile.write(df17_array)

    hackrf = HackRF()
    samples_array = hackrf.hackrf_raw_IQ_format(df17_array)

    SamplesFile = open("Samples.iq8s", "wb") # TODO make this a function and take the file name. Also have the option to run dd on it.
    SamplesFile.write(samples_array)
    os.system("dd if=Samples.iq8s of=Samples_256K.iq8s bs=4k seek=63") # TODO make this a flag, also make it take the file name
