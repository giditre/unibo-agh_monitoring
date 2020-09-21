#!/bin/bash

outfnamebase="multiplot"

fontsize=30

gnuplot -persist <<-EOF
  reset
 
  set term png size 1200,900 font 'Arial-Bold' $fontsize
  set out "${outfnamebase}.png"

  #set term postscript eps size 8.0,6.0 enhanced color font 'Arial-Bold' $fontsize
  #set out "${outfnamebase}.eps"
 
  set xlabel " Time [s] "
  set xrange [0:150]
  set xtics 0,15,180

  set ylabel " Data rate [Mbps] "
  set yrange [0:150]
  set ytics 0,10,150
  #set logscale y
  #set ytics 1,10,500
  #set ytics add (2, 5, 20, 50, 200, 500)
  ##set ytics (1,2,5,10,20,50,100,500)

  set key box top left
  set key nobox 

  set nogrid

  plot "procd_netlab02_ovs20_3_tx.dat" using (\$1):(\$2*0.000001) with linespoints title "Total" lt 2 lc rgb "green" lw 6 pt 0, \
       "procd_netlab02_ovs20_11_tx.dat" using (\$1):(\$2*0.000001) with linespoints title "VNF1" lt 5 lc rgb "red" lw 6 pt 0, \
       "procd_netlab02_ovs20_12_tx.dat" using (\$1):(\$2*0.000001) with linespoints title "VNF2" lt 4 lc rgb "blue" lw 6 pt 0, \
      50 title "Thresh." lt 1 lc rgb "black" lw 2

EOF



