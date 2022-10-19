# Interleave-AC3-TrueHD-Streams
A Python script to interleave AC3 and TrueHD bit streams
```
usage: interleaveDolbyStreams [-h] [-o OUTPUT] AC3 THD

Interleave the bitstreams of an AC3 (Dolby Digital) file and a THD (Dolby TrueHD
or MLP) file to create a THD+AC3 file compatible with tsMuxer and blu-ray.

If a name for the THD+AC3 file isn't provided with the -o argument, the file
name will automatically be output.thd+ac3

Only AC3 files with a sampling frequency of 48 kHz are supported.

positional arguments:
  AC3         the Dolby Digital .ac3 file
  THD         the Dolby TrueHD (MLP) .thd file

optional arguments:
  -h, --help  show this help message and exit
  -o OUTPUT   the name of the interleaved .thd+ac3 file
```
