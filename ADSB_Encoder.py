#!/usr/bin/env python
#

from HackRF import HackRF
from PPM import PPM
from ModeS import ModeS
from sys import argv, exit
from optparse import OptionParser
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

###############################################################
# Further work on fork
# Copyright (C) 2017 David Robinson
def optionParser():
    usage = 'usage: %prog [options]'
    parser = OptionParser(usage=usage)
    parser.add_option('-i', '--icao', action='store', type='int', dest='icao', default='0xABCDEF', help='The ICAO number for the plane in hex. Ensure the ICAO is prefixed with \'0x\' to ensure this is parsed as a hex number. Default: %default')
    parser.add_option('--lat', '--latitude', action='store', type='float', dest='latitude', default='12.34', help='Latitude for the plane in decminal degrees. Default: %default')
    parser.add_option('--lon', '--long', '--longitude', action='store', type='float', dest='longitude', default='56.78', help='Longitude for the place in decminal degrees. Default: %default')
    parser.add_option('-a', '--alt', '--altitude', action='store', type='float', dest='altitude', default='9876.5', help='Altitude in decminal feet. Default: %default')
    parser.add_option('--ca', '--capability', action='store', type='int', dest='capability', default=5, help='The capability. (Think this is always 5 from ADSB messages. More info would be appreciate).  Default: %default')
    parser.add_option('--tc', '--typecode', action='store', type='int', dest='typecode', default=11, help='The type for the ADSB messsage. See https://adsb-decode-guide.readthedocs.io/en/latest/content/introduction.html#ads-b-message-types for more information. Default: %default')
    parser.add_option('--ss', '--surveillancestatus', action='store', type='int', dest='surveillancestatus', default=0, help='The surveillance status. (Think this is always 0 from ADSB messages. More info would be appreciate).  Default: %default')
    parser.add_option('--nicsb', '--nicsupplementb', action='store', type='int', dest='nicsupplementb', default=0, help='The  NIC supplement-B.(Think this is always 0 from ADSB messages. More info would be appreciate).  Default: %default')
    parser.add_option('--time', action='store', type='int', dest='time', default=0, help='The  time. (Think this is always 0 from ADSB messages. More info would be appreciate).  Default: %default')
    parser.add_option('-s', '--surface', action='store', default=False, dest='surface', help='If the plane is on the ground or not. Default: %default')
    parser.add_option('-o', '--out', '--output', action='store', type='string', default='Samples_256K.iq8s', dest='outputfilename', help='The iq8s output filename. This is the file which you will feed into the hackRF. Default: %default')
    return parser.parse_args()
    
if __name__ == "__main__":
    
    options, arguments = optionParser()
    print options    

    modes = ModeS()
    (df17_even, df17_odd) = modes.df17_pos_rep_encode(options.capability, options.icao, options.typecode, options.surveillancestatus, options.nicsupplementb, options.altitude, options.time, options.latitude, options.longitude, options.surface)

    ppm = PPM()
    df17_array = ppm.frame_1090es_ppm_modulate(df17_even, df17_odd)

    hackrf = HackRF()
    samples_array = hackrf.hackrf_raw_IQ_format(df17_array)

    SamplesFile = open('tmp.iq8s', 'wb')
    SamplesFile.write(samples_array)
    os.system("dd if=tmp.iq8s of=%s bs=4k seek=63" % (options.outputfilename)) 
    os.system('rm tmp.iq8s')
