#!/bin/sh
# usage: mux.sh video.mp4 out.mp4
ffmpeg -y -v error -i "$1" -i build/mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k -ar 48000 -shortest -movflags +faststart "$2"
