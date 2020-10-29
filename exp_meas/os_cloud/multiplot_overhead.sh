#!/bin/bash

outfnamebase="overhead"

fontsize=30

linewidth=3

gnuplot -persist <<-EOF
  reset
 
  set term pdf size 9.0,6.0 enhanced font "Arial-Bold,$fontsize" linewidth $linewidth
  set out "${outfnamebase}.pdf"

  #set term png size 1200,900 font 'Arial-Bold' $fontsize
  #set out "${outfnamebase}.png"

  set boxwidth 0.5 relative
  #set style fill solid 1.0

  set xlabel " Sampling Ratio N "

  set ylabel " sFlow signalling traffic [Mbits] "

  set nokey

  set key autotitle columnhead

  #set key reverse
  #set key Left
  #set key box top left
  #set key nobox 

  set nogrid

  plot "results_overhead.txt" using (\$2*0.000001):xticlabels(1) with boxes notitle lt 1 lc 0 fs pattern 5, \
    "" using 0:(\$1*0.000001):(\$2*0.000001):(\$3*0.000001) with errorbars notitle lt -1

EOF
