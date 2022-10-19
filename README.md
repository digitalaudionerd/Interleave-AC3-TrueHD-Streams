# Interleave-AC3-TrueHD-Streams
This is a Python script that interleaves the AC3 and TrueHD bit streams exactly as they are interleaved in blu-ray discs for compatibility with tsMuxer.
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
The .thd+ac3 output of this script has been tested against .thd+ac3 files extracted from .m2ts files and .thd+ac3 files created by eac3to. The output of this script was exactly the same as the original .thd+ac3 files.
