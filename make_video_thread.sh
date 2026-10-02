#!/bin/bash
# piano roll + moving playhead + audio -> mp4 (plot area x 115..1382 px, 120 s)
set -e; P=${1:-day1001}
ffmpeg -loglevel error -y -loop 1 -framerate 25 -i $P.png -f lavfi -i "color=c=white@0.85:s=3x800:r=25" -i $P.mp3 \
  -filter_complex "[0:v][1:v]overlay=x='115+t/300*1267':y=151:shortest=0[v]" -map "[v]" -map 2:a \
  -c:v libx264 -pix_fmt yuv420p -preset veryfast -tune stillimage -c:a aac -b:a 160k -t 304 $P.mp4
