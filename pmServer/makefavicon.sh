#!/bin/sh

if [ -z $1 ] ; then
    echo -e "\\nUsage: \"makefavicon <image_filename.png>\"\\n"
    echo -e "Suitable file types are: PAM, PNM, PPM, PGM, or PBM.\\n"
    exit
fi

rm -f favicon.ico

pamscale -linear -xsize=48 -ysize=48 $1 > tmp_logo48.ppm
pamscale -linear -xsize=32 -ysize=32 $1 > tmp_logo32.ppm
pamscale -linear -xsize=16 -ysize=16 $1 > tmp_logo16.ppm

pnmquant 256 tmp_logo48.ppm > tmp_logo48x48.ppm
pnmquant 256 tmp_logo32.ppm > tmp_logo32x32.ppm
pnmquant 256 tmp_logo16.ppm > tmp_logo16x16.ppm

ppmtowinicon tmp_logo16x16.ppm tmp_logo32x32.ppm tmp_logo48x48.ppm -output favicon.ico

rm -f tmp_logo*.ppm

