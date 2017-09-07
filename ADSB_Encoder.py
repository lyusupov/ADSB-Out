#!/usr/bin/env python
#

from HackRF import HackRF
from PPM import PPM
from ModeS import ModeS
from sys import argv, exit
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


    
if __name__ == "__main__":
    
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

    modes = ModeS()
    (df17_even, df17_odd) = modes.df17_pos_rep_encode(ca, icao, tc, ss, nicsb, alt, time, lat, lon, surface)

    #print ''.join(format(x, '02x') for x in df17_even)
    #print ''.join(format(x, '02x') for x in df17_odd)
    ppm = PPM()
    df17_array = ppm.frame_1090es_ppm_modulate(df17_even, df17_odd)

    #OutFile = open("filename.bin", "wb")
    #OutFile.write(df17_array)

    hackrf = HackRF()
    samples_array = hackrf.hackrf_raw_IQ_format(df17_array)

    SamplesFile = open("Samples.iq8s", "wb") # TODO make this a function and take the file name. Also have the option to run dd on it.
    # TODO make it empty the file first.
    SamplesFile.write(samples_array)
    os.system("dd if=Samples.iq8s of=Samples_256K.iq8s bs=4k seek=63") # TODO make this a flag, also make it take the file name
