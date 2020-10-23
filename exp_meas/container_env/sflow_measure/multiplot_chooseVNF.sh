#!/bin/bash

outfnamebase="chooseVNF"

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

  set ylabel " Load [Mbit/s] "
  set yrange [0:150]
  set ytics 0,10,150

  #set key autotitle columnhead

  set key reverse
  set key Left

  set key box top left
  set key nobox 

  set nogrid

  plot "data_chooseVNF.txt" using (\$1):(\$2*0.000001) title "Total" with linespoint dt 1 lw 3 pt 0 lc rgb "black", \
       "" using (\$1):(\$3*0.000001) with linespoints title "VNF replica 1" dt 2 lw 2 pt 0 lc rgb "red", \
       "" using (\$1):(\$4*0.000001) with linespoints title "VNF replica 2" dt 3 lw 2 pt 0 lc rgb "blue", \
       50 title "Threshold" dt 4 lw 1 lc rgb "grey"

EOF
