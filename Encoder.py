class Encoder:
    """
    Hamming and Manchester Encoding example

    Author: Joel Addison
    Date: March 2013

    Functions to do (7,4) hamming encoding and decoding, including error detection
    and correction.
    Manchester encoding and decoding is also included, and by default will use
    least bit ordering for the byte that is to be included in the array.
    """
###############################################################
# Further work on fork
# Copyright (C) 2017 David Robinson
    def extract_bit(self, byte, pos):
        """
        Extract a bit from a given byte using MS ordering.
        ie. B7 B6 B5 B4 B3 B2 B1 B0
        """
        return (byte >> pos) & 0x01

    def manchester_encode(self, byte):
        """
        Encode a byte using Manchester encoding. Returns an array of bits.
        Adds two start bits (1, 1) and one stop bit (0) to the array.
        """
        # Add start bits (encoded 1, 1)
        # manchester_encoded = [0, 1, 0, 1]
        manchester_encoded = []

        # Encode byte
        for i in range(7, -1, -1):
            if self.extract_bit(byte, i):
                manchester_encoded.append(0)
                manchester_encoded.append(1)
            else:
                manchester_encoded.append(1)
                manchester_encoded.append(0)

        # Add stop bit (encoded 0)
        # manchester_encoded.append(1)
        # manchester_encoded.append(0)

        return manchester_encoded
