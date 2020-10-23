#!/bin/bash

outfnamebase="os_load_incr"

fontsize=30

linewidth=3

gnuplot -persist <<-EOF
  reset
 
  set term pdf size 9.0,6.0 enhanced font "Arial-Bold,$fontsize" linewidth $linewidth
  set out "${outfnamebase}.pdf"

  #set term png size 1200,900 font 'Arial-Bold' $fontsize
  #set out "${outfnamebase}.png"

  set boxwidth 0.8 relative
  #set style fill solid 1.0

  set xlabel " Time [s] "
  set xrange [0:480]
  set xtics 0,40,480

  set ylabel " Load [Gbit/s] "
  set yrange [0:12]
  set ytics 0,1,12

  set ytics nomirror

  set y2label " CPU utilization [%] "
  set y2range [0:120]
  set y2tics 0,10,120

  set nokey

  #set key autotitle columnhead
  #set key reverse
  #set key Left
  #set key box top left
  #set key nobox 

  set nogrid

  plot "results_os_ceilo_load_incr.txt" using 1:3 with boxes axes x1y2 lt 1 lc 0 fs pattern 5, \
       "" using (\$1):(\$5*0.000000001) with lines lt 1 lw 3 lc 0 axes x1y1
EOF
