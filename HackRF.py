import numpy
###############################################################
# Further work on fork
# Copyright (C) 2017 David Robinson
class HackRF:
    """The HackRF class has functions from converting data into a format into which the hackrf can process
    """
    

    def hackrf_raw_IQ_format(self, ppm):
        """
        Args:
            ppm: this is some data in ppm (pulse position modulation) which you want to convert into raw IQ format
            
        Returns:
            bytearray: containing the IQ data
        """

        signal = []
        bits = numpy.unpackbits(numpy.asarray(ppm, dtype=numpy.uint8))
        for bit in bits:
            if bit == 1:
                I = 127
                Q = 127
            else:
                I = 0
                Q = 0
            signal.append(I)
            signal.append(Q)

        return bytearray(signal)
