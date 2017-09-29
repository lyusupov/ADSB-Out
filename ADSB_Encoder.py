#!/usr/bin/env python3
#

from HackRF import HackRF
from PPM import PPM
from ModeS import ModeS
from sys import argv, exit
import argparse
import configparser
import logging
import logging.config
import os
import csv

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

def auto_int(x):
    """Parses HEX into for argParser"""
    return int(x, 0)
    
def auto_bool(x):
    if x.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif x.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def argParser():
    description = 'This tool will generate ADS-B data in a form that a hackRF can broadcast. In addition to providing the information at the command the defaults can be changed in the config.cfg file and the the loggin config changed in logging.cfg.'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-i', '--icao', action='store', type=auto_int, dest='icao', default=cfg.get('plane', 'icao'), help='The ICAO number for the plane in hex. Ensure the ICAO is prefixed with \'0x\' to ensure this is parsed as a hex number. Default: %(default)s')
    parser.add_argument('--lat', '--latitude', action='store', type=float, dest='latitude', default=cfg.getfloat('plane', 'latitude'), help='Latitude for the plane in decminal degrees. Default: %(default)s')
    parser.add_argument('--lon', '--long', '--longitude', action='store', type=float, dest='longitude', default=cfg.getfloat('plane', 'longitude'), help='Longitude for the place in decminal degrees. Default: %(default)s')
    parser.add_argument('-a', '--alt', '--altitude', action='store', type=float, dest='altitude', default=cfg.getfloat('plane', 'altitude'), help='Altitude in decminal feet. Default: %(default)s')
    parser.add_argument('--ca', '--capability', action='store', type=int, dest='capability', default=cfg.getint('plane', 'capability'), help='The capability. (Think this is always 5 from ADSB messages. More info would be appreciate).  Default: %(default)s')
    parser.add_argument('--tc', '--typecode', action='store', type=int, dest='typecode', default=cfg.getint('plane', 'typecode'), help='The type for the ADSB messsage. See https://adsb-decode-guide.readthedocs.io/en/latest/content/introduction.html#ads-b-message-types for more information. Default: %(default)s')
    parser.add_argument('--ss', '--surveillancestatus', action='store', type=int, dest='surveillancestatus', default=cfg.getint('plane', 'surveillancestatus'), help='The surveillance status. (Think this is always 0 from ADSB messages. More info would be appreciate).  Default: %(default)s')
    parser.add_argument('--nicsb', '--nicsupplementb', action='store', type=int, dest='nicsupplementb', default=cfg.getint('plane', 'nicsupplementb'), help='The  NIC supplement-B.(Think this is always 0 from ADSB messages. More info would be appreciate).  Default: %(default)s')
    parser.add_argument('--time', action='store', type=int, dest='time', default=cfg.getint('plane', 'time'), help='The  time. (Think this is always 0 from ADSB messages. More info would be appreciate).  Default: %(default)s')
    parser.add_argument('-s', '--surface', action='store', default=cfg.getboolean('plane', 'surface'), type=auto_bool, dest='surface', help='If the plane is on the ground or not. Default: %(default)s')
    parser.add_argument('-o', '--out', '--output', action='store', type=str, default=cfg.get('general', 'outputfilename'), dest='outputfilename', help='The iq8s output filename. This is the file which you will feed into the hackRF. Default: %(default)s')
    parser.add_argument('-r', '--repeats', action='store', dest='repeats', type=int, default=cfg.getint('general', 'repeats'), help='How many repeats of the data to perform. Default: %(default)s')
    parser.add_argument('--csv', '--csvfile', '--in', '--input', action='store', type=str, default=cfg.get('general', 'csvfile'), dest='csvfile', help='Import a CSV file with the plane data in it. Default: %(default)s')    
    # TODO Make it so it can do a static checksum
    # TODO Get pause between messages
    # TODO Get pause between repeats
    # TODO Do a pause function
    return parser.parse_args()

def singlePlane(arguments):
    logger.info('Processing default and command line options for a single plane')
    logger.info('Repeating the message %s times' % (arguments.repeats))
    samples = bytearray()
    for i in range(0, arguments.repeats):
        modes = ModeS()
        (df17_even, df17_odd) = modes.df17_pos_rep_encode(arguments.capability, arguments.icao, arguments.typecode, arguments.surveillancestatus, arguments.nicsupplementb, arguments.altitude, arguments.time, arguments.latitude, arguments.longitude, arguments.surface)

        ppm = PPM()
        df17_array = ppm.frame_1090es_ppm_modulate(df17_even, df17_odd)

        hackrf = HackRF()
        samples_array = hackrf.hackrf_raw_IQ_format(df17_array)
        samples = samples+samples_array
    return samples

def manyPlanes(arguments):
    logger.info('Processing CSV file')    
    samples = bytearray()
    logger.info('Repeating the message %s times' % (arguments.repeats))
    for i in range(0, arguments.repeats):
        with open(arguments.csvfile, newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',')
            for row in reader:                
                if not 'icao' in row.keys():
                    row['icao'] = arguments.icao
                else:
                    row['icao'] = int(row['icao'], 0)
                if not 'latitude' in row.keys():
                    row['latitude'] = arguments.latitude
                if not 'longitude' in row.keys():
                    row['longitude'] = arguments.longitude
                if not 'altitude' in row.keys():
                    row['altitude'] = arguments.altitude
                if not 'capability' in row.keys():
                    row['capability'] = arguments.capability
                if not 'typecode' in row.keys():
                    row['typecode'] = arguments.typecode
                if not 'surveillancestatus' in row.keys():
                    row['surveillancestatus'] = arguments.surveillancestatus
                if not 'nicsupplementb' in row.keys():
                    row['nicsupplementb'] = arguments.nicsupplementb
                if not 'time' in row.keys():
                    row['time'] = arguments.time
                if not 'surface' in row.keys():
                    row['surface'] = arguments.surface
                logger.debug('Row from CSV: %s' % (row))
                modes = ModeS()
                (df17_even, df17_odd) = modes.df17_pos_rep_encode(row['capability'], row['icao'], row['typecode'], row['surveillancestatus'], row['nicsupplementb'], row['altitude'], row['time'], row['latitude'], row['longitude'], row['surface'])

                ppm = PPM()
                df17_array = ppm.frame_1090es_ppm_modulate(df17_even, df17_odd)

                hackrf = HackRF()
                samples_array = hackrf.hackrf_raw_IQ_format(df17_array)
                samples = samples+samples_array
    return samples

def writeOutputFile(filename, data):
    tmpfile = '%s.tmp'%(filename)
    logger.info('Writing %s file'%(tmpfile))
    SamplesFile = open(tmpfile, 'wb')
    SamplesFile.write(data)
    SamplesFile.close()
    os.system('sync')
    os.system('rm %s' % (filename)) 
    logger.info('dd for file: %s' % (filename))
    os.system("dd if=%s of=%s bs=4k seek=63 > /dev/null 2>&1" % (tmpfile, filename)) 
    os.system('sync')
    os.system('rm %s'%(tmpfile))   

def main():
    global cfg
    cfg = configparser.ConfigParser()
    cfg.read('config.cfg')
    
    arguments = argParser()
    
    global logger
    logging.config.fileConfig('logging.cfg')
    logger = logging.getLogger(__name__)
    logger.info('Starting ADSB Encoder')
    logger.debug('The arguments: %s' % (arguments))
    data = None
    if arguments.csvfile == '':
        data = singlePlane(arguments)
    else:
        data = manyPlanes(arguments)
    writeOutputFile(arguments.outputfilename, data)
    logger.info('Complete')

def threadingCSV(csv):
    global cfg
    cfg = configparser.ConfigParser()
    cfg.read('config.cfg')
    
    arguments = argParser()
    arguments.csvfile = csv[0]
    arguments.outputfilename = csv[1]
    global logger
    logging.config.fileConfig('logging.cfg')
    logger = logging.getLogger(__name__)
    logger.info('Starting ADSB Encoder')
    logger.debug('The arguments: %s' % (arguments))
    data = None
    if arguments.csvfile == '':
        data = singlePlane(arguments)
    else:
        data = manyPlanes(arguments)
    writeOutputFile(arguments.outputfilename, data)
    logger.info('Complete')
    
if __name__ == "__main__":
    main()
    



