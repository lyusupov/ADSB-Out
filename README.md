# "ADS-B Out" add-on for SoftRF-Emu, Stratux, etc...

This repository contains "ADS-B Out" encoder for Tx-capable SDR hardware.

It is currently written in architecture independent Python language and can be used as an add-on for existing
open source "ADS-B In" solutions. One known good example is [Stratux](https://github.com/cyoung/stratux).

## Disclaimer
The source code is published for academic purpose only.

## Instructions
1. Execute *ADSB_Encoder.py* all the options have defaults so none are needed to generate with defaults. Running help will show you the optiosn you can change:
```
$ ADSB_Encoder.py

$ ADSB_Encoder.py -h
Usage: ADSB_Encoder.py [options]

Options:
  -h, --help            show this help message and exit
  -i ICAO, --icao=ICAO  The ICAO number for the plane in hex. Ensure the ICAO
                        is prefixed with '0x' to ensure this is parsed as a
                        hex number. Default: 0xABCDEF
  --lat=LATITUDE, --latitude=LATITUDE
                        Latitude for the plane in decminal degrees. Default:
                        12.34
  --lon=LONGITUDE, --long=LONGITUDE, --longitude=LONGITUDE
                        Longitude for the place in decminal degrees. Default:
                        56.78
  -a ALTITUDE, --alt=ALTITUDE, --altitude=ALTITUDE
                        Altitude in decminal feet. Default: 9876.5
  --ca=CAPABILITY, --capability=CAPABILITY
                        The capability. (Think this is always 5 from ADSB
                        messages. More info would be appreciate).  Default: 5
  --tc=TYPECODE, --typecode=TYPECODE
                        The type for the ADSB messsage. See https://adsb-
                        decode-guide.readthedocs.io/en/latest/content/introduc
                        tion.html#ads-b-message-types for more information.
                        Default: 11
  --ss=SURVEILLANCESTATUS, --surveillancestatus=SURVEILLANCESTATUS
                        The surveillance status. (Think this is always 0 from
                        ADSB messages. More info would be appreciate).
                        Default: 0
  --nicsb=NICSUPPLEMENTB, --nicsupplementb=NICSUPPLEMENTB
                        The  NIC supplement-B.(Think this is always 0 from
                        ADSB messages. More info would be appreciate).
                        Default: 0
  --time=TIME           The  time. (Think this is always 0 from ADSB messages.
                        More info would be appreciate).  Default: 0
  -s SURFACE, --surface=SURFACE
                        If the plane is on the ground or not. Default: False
  -o OUTPUTFILENAME, --out=OUTPUTFILENAME, --output=OUTPUTFILENAME
                        The iq8s output filename. This is the file which you
                        will feed into the hackRF. Default: Samples_256K.iq8s
```
2. Transmit the signal into air:
```
$ hackrf_transfer -t Samples_256K.iq8s -f 868000000 -s 2000000 -x 10
call hackrf_sample_rate_set(2000000 Hz/2.000 MHz)
call hackrf_baseband_filter_bandwidth_set(1750000 Hz/1.750 MHz)
call hackrf_set_freq(868000000 Hz/868.000 MHz)
Stop with Ctrl-C
 0.5 MiB / 1.000 sec =  0.5 MiB/second

User cancel, exiting...
Total time: 1.00038 s
hackrf_stop_tx() done
hackrf_close() done
hackrf_exit() done
fclose(fd) done
exit
$
```
 * -t is the input file to transmit
 * -f is the frequency in hertz. In the real world this would be 1090000000 but do not use that
 * -s is the sample rate in hertz
 * -x is the gain
## Validation
```
$ sudo dump1090 --net --freq 868000000
...
```
![](https://github.com/lyusupov/ADSB-Out/raw/master/documents/images/dump1090.JPG)

## References
1. "*Gr-Air-Modes*", **Nick Foster**, 2012
2. "*EXPLOITING THE AUTOMATIC DEPENDENT SURVEILLANCE BROADCAST SYSTEM VIA FALSE TARGET INJECTION*", **Domenic Magazu III**, 2012
3. "*ADS-B out by HACKRF and received over the air by rtl-sdr dongle and dump1090*", **Jiao Xianjun**, 2014
4. "*Ghost in the Air(Trafﬁc): On insecurity of ADS-B protocol and practical attacks on ADS-B devices*", **Andrei Costin and Aurelien Francillon**, 2015
5. "*ADS-B Decoding Guide*", **Junzi Sun**, 2017

# History
This is a fork orginally from https://github.com/lyusupov/ADSB-Out in September 2017. 
