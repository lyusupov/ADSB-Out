import numpy
from Encoder import Encoder
###############################################################
# Further work on fork
# Copyright (C) 2017 David Robinson
class PPM:
    """The PPM class contains functions about PPM manipulation
    """
 
    def frame_1090es_ppm_modulate(self, even, odd):
        """
        Args:
            even and odd: The bits you would converted to PPM
        Returns:
            The bytearray of the PPM data
        """
        ppm = [ ]
        encoder = Encoder()

        for i in range(48):    # pause
            ppm.append( 0 )

        ppm.append( 0xA1 )   # preamble
        ppm.append( 0x40 )
        
        for i in range(len(even)):
            word16 = numpy.packbits(encoder.manchester_encode(~even[i]))
            ppm.append(word16[0])
            ppm.append(word16[1])


        for i in range(100):    # pause
            ppm.append( 0 )

        ppm.append( 0xA1 )   # preamble
        ppm.append( 0x40 )

        for i in range(len(odd)):
            word16 = numpy.packbits(encoder.manchester_encode(~odd[i]))
            ppm.append(word16[0])
            ppm.append(word16[1])

        for i in range(48):    # pause
            ppm.append( 0 )

        #print '[{}]'.format(', '.join(hex(x) for x in ppm))
        
        return bytearray(ppm)
