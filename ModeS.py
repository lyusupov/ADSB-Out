from location import *
from conversions import *
class ModeS:
    """This class handles the ModeS ADSB manipulation
    """
    
    def df17_pos_rep_encode(self, ca, icao, tc, ss, nicsb, alt, time, lat, lon, surface):
        """
        This will take the parameters for an ADSB type 17 message and reutrn the even and odd bytes
        """

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
