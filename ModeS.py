from ModeSLocation import ModeSLocation
import math

class ModeS:
    """This class handles the ModeS ADSB manipulation
    """
    
    def df17_pos_rep_encode(self, ca, icao, tc, ss, nicsb, alt, time, lat, lon, surface):
        """
        This will take the parameters for an ADSB type 17 message and reutrn the even and odd bytes
        """

        format = 17 #The format type of an ADSB message

        location = ModeSLocation()
        enc_alt =	location.encode_alt_modes(alt, surface)
        #print "Alt(%r): %X " % (surface, enc_alt)

        #encode that position
        (evenenclat, evenenclon) = location.cpr_encode(lat, lon, False, surface)
        (oddenclat, oddenclon)   = location.cpr_encode(lat, lon, True, surface)

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
        df17_crc = self.bin2int(self.modes_crc(df17_str+"000000", encode=True))

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
        df17_crc = self.bin2int(self.modes_crc(df17_str+"000000", encode=True))

        df17_odd_bytes.append((df17_crc>>16) & 0xff)
        df17_odd_bytes.append((df17_crc>> 8) & 0xff)
        df17_odd_bytes.append((df17_crc    ) & 0xff)    
        
        return (df17_even_bytes, df17_odd_bytes)

###############################################################

# Copyright (C) 2015 Junzi Sun (TU Delft)

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

# the polynominal generattor code for CRC

        
    def modes_crc(self, msg, encode=False):
        """Mode-S Cyclic Redundancy Check
        Detect if bit error occurs in the Mode-S message
        Args:
            msg (string): 28 bytes hexadecimal message string
            encode (bool): True to encode the date only and return the checksum
        Returns:
            string: message checksum, or partity bits (encoder)
        """

        GENERATOR = "1111111111111010000001001" # Currently don't know what is magic about this number

        msgbin = list(self.hex2bin(msg))

        if encode:
            msgbin[-24:] = ['0'] * 24

        # loop all bits, except last 24 piraty bits
        for i in range(len(msgbin)-24):
            # if 1, perform modulo 2 multiplication,
            if msgbin[i] == '1':
                for j in range(len(GENERATOR)):
                    # modulo 2 multiplication = XOR
                    msgbin[i+j] = str((int(msgbin[i+j]) ^ int(GENERATOR[j])))

        # last 24 bits
        reminder = ''.join(msgbin[-24:])
        return reminder
    
            
        
    def hex2bin(self, hexstr):
        """Convert a hexdecimal string to binary string, with zero fillings. """
        scale = 16
        num_of_bits = len(hexstr) * math.log(scale, 2)
        binstr = bin(int(hexstr, scale))[2:].zfill(int(num_of_bits))
        return binstr

    def bin2int(self, binstr):
        """Convert a binary string to integer. """
        return int(binstr, 2)
