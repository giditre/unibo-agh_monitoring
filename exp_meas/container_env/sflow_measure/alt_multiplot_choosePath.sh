#!/bin/bash

outfnamebase="choosePath"

fontsize=30

linewidth=3

gnuplot -persist <<-EOF
  reset
 
  set term pdf size 9.0,6.0 enhanced font "Arial-Bold,$fontsize" linewidth $linewidth
  set out "${outfnamebase}.pdf"

  #set term png size 1200,900 font 'Arial-Bold' $fontsize
  #set out "${outfnamebase}.png"

  set xlabel " Time [s] "
  set xrange [0:150]
  set xtics 0,15,180

  set ylabel " Data rate [Mbps] "
  set yrange [0:1200]
  set ytics 0,100,1200

  #set key autotitle columnhead

  set key box top left
  set key nobox 

  set nogrid

  plot "data_choosePath.txt" using (\$1):(\$2*0.000001) title "Total" with linespoint dt 2 lw 2 pt 0 lc rgb "black", \
       "" using (\$1):(\$3*0.000001) with linespoints title "Path1" lw 0 pt 6 ps 1 lc rgb "red", \
       "" using (\$1):(\$4*0.000001) with linespoints title "Path2" lw 0 pt 2 ps 1 lc rgb "blue", \
       300 title "Thresh." dt 2 lw 1 lc rgb "grey"

EOF
