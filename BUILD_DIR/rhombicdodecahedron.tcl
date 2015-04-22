# To run execute: vmd -dispdev text  -e xxx.tcl

# All pairs calculation to work out the maximum distance between two
# atoms in an atomselection
proc dmax {selection} {

    # some error checking
    if {[$selection num] <= 0} {
	error "dmax: needs a selection"
    }
    
    set dmax2 -1.0
    set coord [$selection get {x y z}]
    for { set i 0 } { $i < [$selection num] } { incr i } {
	puts "$i [$selection num]"
	set seli [lindex $coord $i]
	set ix [lindex $seli 0]
	set iy [lindex $seli 1]
	set iz [lindex $seli 2]
	for { set j [expr $i + 1]} { $j < [$selection num] } { incr j } {
	    set selj [lindex $coord $j]
	    set dx [expr $ix - [lindex $selj 0]]
	    set dy [expr $iy - [lindex $selj 1]]
	    set dz [expr $iz - [lindex $selj 2]]
	    set d2 [expr $dx*$dx + $dy*$dy + $dz*$dz]
	    if {$d2 > $dmax2} {set dmax2 $d2}
	}
    }        
    return [expr sqrt($dmax2)]
}

# A slightly tuned version of the above routine
proc dmax_alt {selection {inc 1}} {

    if {[$selection num] <= 0} {
	error "dmax: needs a selection"
    }
    
    set dmax2 -1.0
    set coord [$selection get {x y z}]
    set imax [expr [$selection num] - 1]
    set jmax [$selection num]
    for { set i 0 } { $i < $imax } { incr i $inc} {
	set ri [lindex $coord $i]
	for { set j [expr $i + 1]} { $j < $jmax } { incr j $inc} {
	    set rj [lindex $coord $j]
	    set rij [vecsub $ri $rj]
	    set d2 [vecdot $rij $rij]
	    if {$d2 > $dmax2} {set dmax2 $d2}
	}
    }
    return [expr sqrt($dmax2)]
}

################################################################
#                 MAIN PART STARTS HERE
#
# For small proteins (order 1000 residues) set 'inc' to 1, it can be
# increased for very large protein systems such as entire viral
# capsids up to, say, 5
#
# For very large proteins, the number of water segments can be such
# that a four letter limit in the segment id is breached. Set the
# variable 'prefix' to W instead of the default (WT).
#
################################################################

set psf         xxx.psf
set pdb         xxx.pdb
set prefix      W
set inc         5
set box         box
set rbddh       zzz
set padding     12.0
package require psfgen

resetpsf

mol load psf $psf pdb $pdb
set sel [atomselect top all]
set ca [atomselect top "name CA"]
puts "Calculating distance between C_alpha's. May take some time . . ."
set Dm [expr [dmax_alt $ca $inc] / 2]
set R [expr ($Dm + $padding)*sqrt(2)]
set D $R

# find mass center
#set center [center_of_mass $sel]
set center [lindex [measure inertia $sel] 0]

$sel moveby [vecinvert $center]
set tmp tmp.pdb
$sel writepdb $tmp
mol delete all
package require solvate

set xymm [expr $R*sqrt(2.)/2]
set min "-$xymm -$xymm -$R"
set max "$xymm $xymm $R"
set minmax [list $min $max]
solvate $psf $tmp -s $prefix -b 1.5 -o $box -minmax $minmax
mol delete top
resetpsf
mol load psf ${box}.psf pdb ${box}.pdb
readpsf  ${box}.psf
coordpdb ${box}.pdb

#rotate along z-axis
set all [atomselect top all]
$all move [trans z 45.0]

set seltext "same residue as not (x+y>-$D and x-y<$D and z-y<$D and z+y>-$D and x+z>-$D and x-z<$D and x+y<$D and z+y<$D and z+x<$D and z-y>-$D and x-z>-$D and x-y>-$D)"
set selDel [atomselect top "$seltext"]
set sel [atomselect top "not ($seltext)"]
puts  "Deleting [$selDel num] atoms"
set delList [$selDel get {segid resid}]
set delList [lsort -unique $delList]

foreach record $delList {
    foreach {segid resid} $record { break }
    delatom $segid $resid
}

#rotate along z-axis
$sel move [trans z 45.0]

$sel writepsf "$rbddh.psf"
$sel writepdb "$rbddh.pdb"

# remove temp files
file delete ${box}.psf ${box}.pdb combine.pdb combine.psf $tmp temp.psf temp.pdb

puts "Center of mass is at: 0.0 0.0 0.0"
puts "Radius: $D"
puts "Maximum distance between C-alphas: [expr $Dm * 2.0]"
puts "Dimensions:"
set D [expr $D*sqrt(2)]
set a "cellBasisVector1 $D 0.0 0.0"
set b "cellBasisVector2 0.0 $D 0.0"
set c "cellBasisVector3 [expr $D/2] [expr $D/2] [expr $D/sqrt(2)]"
set fh [open "cell_basis_vectors.text" "w"]
puts $fh "cellBasisVector1 $D 0.0 0.0"
puts $fh "cellBasisVector2 0.0 $D 0.0"
puts $fh  "cellBasisVector3 [expr $D/2] [expr $D/2] [expr $D/sqrt(2)]"
close $fh
exit
