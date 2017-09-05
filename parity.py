'''
   Copyright 2015 Wolfgang Nagele

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
'''
def bin2dec(buf):
  if 0 == len(buf): # Crap input
    return -1
  return int(buf, 2)

# Ported from: http://www.radarspotters.eu/forum/index.php?topic=5617.msg41293#msg41293
def get_parity(msg, extended):
  msg_length = len(msg)
  payload = msg[:msg_length - 24]
  parity = msg[msg_length - 24:]

  data = bin2dec(payload[0:32])
  if extended:
    data1 = bin2dec(payload[32:64])
    data2 = bin2dec(payload[64:]) << 8

  hex_id = bin2dec(parity) << 8

  for i in range(0, len(payload)):
    if ((data & 0x80000000) != 0):
      data ^= 0xFFFA0480
    data <<= 1

    if extended:
      if ((data1 & 0x80000000) != 0):
        data |= 1
      data1 <<= 1

      if ((data2 & 0x80000000) != 0):
        data1 = data1 | 1
      data2 <<= 1

  return data
  #return (data ^ hex_id) >> 8
