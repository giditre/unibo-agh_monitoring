#!/bin/bash

outfnamebase="changeN_C10"

fontsize=30

linewidth=3

gnuplot -persist <<-EOF
  reset
 
  set term pdf size 10.0,7.0 enhanced font "Arial-Bold,$fontsize" linewidth $linewidth
  set out "${outfnamebase}.pdf"

  #set term png size 1200,900 font 'Arial-Bold' $fontsize
  #set out "${outfnamebase}.png"

  set xlabel " Time [s] "
  set xrange [0:200]
  set xtics 0,20,200

  set ylabel " Load [Mbit/s] "
  set yrange [0:100]
  set ytics 0,20,100

  #set nokey

  set key autotitle columnhead
  set key reverse
  set key Left
  set key box top left
  #set key nobox 

  set nogrid

  plot "results_changeN_C10.txt" using 1:(\$3*0.000001) with lines t "Gen. load" lt 1 lw 1 lc 0, \
      "" using 1:(\$4*0.000001) with points t "sFlow samples" pt 1 ps 2 lt -1, \
      "" using 1:(\$5*0.000001) with lines t "EWMA N=1" dt 3 lw 1 lc 0, \
      "" using 1:(\$6*0.000001) with lines t "EWMA N=5" dt 2 lw 1 lc 0, \
      "" using 1:(\$7*0.000001) with lines t "EWMA N=10" dt 4 lw 1 lc 0, \
      "" using 1:(\$8*0.000001) with lines t "EWMA N=20" dt 5 lw 1 lc 0

EOF