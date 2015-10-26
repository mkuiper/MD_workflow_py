# view_change_render.tcl
#
# A script to save current viewpoints and animate
# a smooth 'camera move' between them,
# rendering each frame to a numbered .rgb file
#  (Can also do the 'camera moves' without
#   writing files.)
#

##  Modified by Mike  March 2007.
##   Use TachonInternal for rendering, also progresses through a trajectory during 
##   viewpoint transistions. 


# Barry Isralewitz, 2003-Oct-13 
# barryi@ks.uiuc.edu
#
# Warning: this script does the math cheaply, i.e. only interpolates 
# transformation matrices, many sorts of extreme viewpoint changes will look
# odd to bizzare
#
# Usage:
# In the vmd console type 
#       save_vp 1
# to save your current viewpoint
#
# type
#       retrieve_vp 1  
# to retrieve that viewpoint  (You can replace '1' with an integer < 10000)
#
# After you've saved more than 1 viewpoint
#  move_vp_render 1 8 200 /tmp myMove 25 smooth
# will move from viewpoint 1 to viewpoint 8 smoothly, recording 25 frames 
# to /tmp/myMove####.rgb, with #### ranging from 0200 -- 0224. 
#
#       move_vp 1 43
# will retrieve viewpoint 1 then smoothly move to viewpoint 43.
# (move_vp does not render .rgb files, move_vp_render does) 
#  Note warning above.  Extreme moves that cause obvious protein distortion
#can be done in two or three steps.
#
# To specify animation frames used, use
#    move_vp 1 43 200
# will move from viewpoint 1 to 43 in 200 steps.  If this is not specified, a 
# default 50 frames is used
#
# To specify smooth/jerky accelaration, use
#   move_vp 1 43 200 smooth
#   move_vp_render 1 8 200 /tmp myMove 25 smooth 
#   or
#   move_vp 1 43 200 sharp
#   move_vp_render 1 8 200 /tmp myMove 25 sharp 
#
# the 'smooth' option accelerates and deccelrates the transformation
# the 'sharp' option gives constant velocity
# 
# To write viewpoints to a file, 
# write_vps my_vp_file.tcl
# 
# viewpoints with integer numbers 0-10000 are saved   
#
# To retrieve viewpoints from a file,
# source my_vp_file.tcl  
#
#
proc scale_mat {mat scaling} {
  set bigger ""
  set outmat ""
  for {set i 0} {$i<=3} {incr i} {
    set r ""
    for {set j 0} {$j<=3} {incr j} {            
      lappend r  [expr $scaling * [lindex [lindex [lindex $mat 0] $i] $j] ]
    }
    lappend outmat  $r
  }
  lappend bigger $outmat
  return $bigger
}

proc div_mat {mat1 mat2} {
  set bigger ""
  set outmat ""
  for {set i 0} {$i<=3} {incr i} {
    set r ""
    for {set j 0} {$j<=3} {incr j} {            
      lappend r  [expr  (0.0 + [lindex [lindex [lindex $mat1 0] $i] $j]) / ( [lindex [lindex [lindex $mat2 0] $i] $j] )]

    }
    lappend outmat  $r
  }
  lappend bigger $outmat
  return $bigger
}

proc sub_mat {mat1 mat2} {
  set bigger ""
  set outmat ""
  for {set i 0} {$i<=3} {incr i} {
    set r ""
    for {set j 0} {$j<=3} {incr j} {            
      lappend r  [expr  (0.0 + [lindex [lindex [lindex $mat1 0] $i] $j]) - ( [lindex [lindex [lindex $mat2 0] $i] $j] )]

    }
    lappend outmat  $r
  }
  lappend bigger $outmat
  return $bigger
}

proc power_mat {mat thePower} {
  set bigger ""
  set outmat ""
  for {set i 0} {$i<=3} {incr i} {
    set r ""
    for {set j 0} {$j<=3} {incr j} {            
      lappend r  [expr pow( [lindex [lindex [lindex $mat 0] $i] $j], $thePower)]
    }
    lappend outmat  $r
  }
  lappend bigger $outmat
  return $bigger
}

proc mult_mat {mat1 mat2} {
  set bigger ""
  set outmat ""
  for {set i 0} {$i<=3} {incr i} {
    set r ""
    for {set j 0} {$j<=3} {incr j} {            
      lappend r  [expr  (0.0 + [lindex [lindex [lindex $mat1 0] $i] $j]) * [lindex [lindex [lindex $mat2 0] $i] $j] ]
    }
    lappend outmat  $r
  }
  lappend bigger $outmat
  return $bigger
}

proc add_mat {mat1 mat2} {
  set bigger ""
  set outmat ""
  for {set i 0} {$i<=3} {incr i} {
    set r ""
    for {set j 0} {$j<=3} {incr j} {            
      lappend r  [expr  (0.0 + [lindex [lindex [lindex $mat1 0] $i] $j]) + [lindex [lindex [lindex $mat2 0] $i] $j] ]
    }
    lappend outmat  $r
  }
  lappend bigger $outmat
  return $bigger
}


proc write_vps {filename} {
  global viewpoints

  set myfile [open $filename w]
  puts $myfile "\#This file contains viewpoints for a VMD script, view_change.tcl.\n\#Type 'source $filename' from the VMD command window to load these viewpoints.\n"
  
  foreach mol [molinfo list] {
    for {set v 0} {$v<=10000} {incr v} {
      if  [info exists viewpoints($v,$mol,0)] { 
	for {set mat 0} {$mat <= 3} {incr mat} {
	  puts $myfile "set viewpoints($v,$mol,$mat) { $viewpoints($v,$mol,$mat) }\n "
	}
      }
    }
  }
  puts $myfile "puts \"\\nLoaded viewpoints file $filename \\n\"\n"
  close $myfile
}




proc save_vp {view_num} {
  global viewpoints
  if [info exists viewpoints($view_num)] {unset viewpoints($view_num)}
  # get the current matricies
  foreach mol [molinfo list] {
    set viewpoints($view_num,$mol,0) [molinfo $mol get rotate_matrix]
    set viewpoints($view_num,$mol,1) [molinfo $mol get center_matrix]
    set viewpoints($view_num,$mol,2) [molinfo $mol get scale_matrix]
    set viewpoints($view_num,$mol,3) [molinfo $mol get global_matrix]
  }
} 



proc justify {justify_frame} {
  if { $justify_frame < 1 } { 
    set frametext "0000"
  } elseif { $justify_frame < 10 } {
    set frametext "000$justify_frame"
  } elseif {$justify_frame < 100} {
    set frametext "00$justify_frame"
  } elseif {$justify_frame <1000} {
    set frametext "0$justify_frame"
  }  else {
    set frametext $justify_frame
  }
  return $frametext
  
}


proc move_vp_render {start end first_frame_num dirName filePrefixName {morph_frames 50} {accel smooth} {start_frame 0} {end_frame 0} } {
  
  global viewpoints 
  
  set framenum $first_frame_num  
  foreach mol [molinfo list] {
    
    if [info exists viewpoints($start,$mol,0)] {
      set old_rotate($mol)  $viewpoints($start,$mol,0)
      set old_center($mol) $viewpoints($start,$mol,1)
      set old_scale($mol) $viewpoints($start,$mol,2)
      set old_global($mol)  $viewpoints($start,$mol,3)
    } else {
      cd /	    puts "Starting view $start was not saved"} 

    if [info exists viewpoints($end,$mol,0)] {
      set new_rotate($mol) $viewpoints($end,$mol,0)
      set new_center($mol) $viewpoints($end,$mol,1)
      set new_scale($mol) $viewpoints($end,$mol,2)
      set new_global($mol)  $viewpoints($end,$mol,3)
    } else {
      puts "Ending view $end was not saved"} 

    #leave if don't have both viewpoints
    if {! ([info exists viewpoints($start,$mol,0)] && [info exists viewpoints($end,$mol,0)]) } {
      error "move_vp failed"
    }

    set old_rotate($mol) $viewpoints($start,$mol,0)
    set old_center($mol) $viewpoints($start,$mol,1)
    set old_scale($mol) $viewpoints($start,$mol,2)
    set old_global($mol)  $viewpoints($start,$mol,3)
    
    
    retrieve_vp $start   
    
    set needed_rotate($mol) [sub_mat  $new_rotate($mol) $old_rotate($mol)]

    
    set needed_center($mol) [sub_mat  $new_center($mol) $old_center($mol)]

    
    set needed_scale($mol) [sub_mat  $new_scale($mol) $old_scale($mol)]

    
    set needed_global($mol) [sub_mat  $new_global($mol) $old_global($mol)]

  }	


#  work out trajectory frame rate change:-----------------------------------
 
  set dcd_rate [expr ((0.0+$end_frame-$start_frame)/$morph_frames)] 
  puts " start: $start_frame  end:$end_frame  rate: $dcd_rate "
  
  set dcd_frame $start_frame
  
#  set start frame: --------------------------------------------------------

  animate goto $start_frame
  display update


  
  for {set j 0} {$j<= ($morph_frames - 1)} {incr j} {
    foreach mol [molinfo list] {
      #set scaling to apply for this individual frame
      if {$accel == "smooth"} {
	#accelerate smoothly to start and stop 
	set theta [expr 3.1415927 * (0.0 + $j)/($morph_frames - 1)] 
	set scale_factor [expr (1 -cos ($theta) ) /2]
	
      } else {
	#infinite acceleration to start and stop
	set scale_factor [expr (0.0 + $j)/($morph_frames - 1)] 
      }
      
      if {$j == $morph_frames} {
	#correct for roundoff errors, so ends in correct position
	set scale_factor 1.0
      }
      
      set current_rotate($mol) [add_mat $old_rotate($mol) [
							   scale_mat $needed_rotate($mol) $scale_factor]
			       ]
      
      set current_center($mol) [add_mat $old_center($mol) [
							   scale_mat $needed_center($mol) $scale_factor]
			       ]
      
      set current_scale($mol)  [add_mat $old_scale($mol) [
							  scale_mat $needed_scale($mol) $scale_factor]
			       ]
      
      set current_global($mol) [add_mat $old_global($mol) [
							   scale_mat $needed_global($mol) $scale_factor]
			       ]
      
      molinfo $mol set rotate_matrix $current_rotate($mol)
      molinfo $mol set center_matrix $current_center($mol)
      molinfo $mol set scale_matrix $current_scale($mol)
      molinfo $mol set global_matrix $current_global($mol)
      
      
    }
    display update
    set frametext [justify $framenum]
	
	set framenumber    ${dirName}/${filePrefixName}.${frametext}.plot.dat

##	set cmd_line " /usr/local/lib/vmd/tachyon_LINUXAMD64 -aasamples 8 -rescale_lights 0.36 -add_skylight 1.0 temp_plot -format PPM -o $framenumber" 
##	set cmd_line " /usr/local/lib/vmd/tachyon_LINUXAMD64 -trans_vmd  1.0 temp_plot -format PPM -o $framenumber" 
                      

# plot Tachyon .dat file which is used in rendering process:
# New strategy here is to render the tachyon plot.dat files first then distribute those for parallel processing. 

 render Tachyon $framenumber  
 puts "Rendering frame ${dirName}/${filePrefixName}.${frametext}.plot.dat"
 incr framenum

# update frame number: 
    set dcd_frame [expr (($dcd_frame+$dcd_rate))]
    animate goto $dcd_frame

    display update
    

  }
}



proc retrieve_vp {view_num} {
  global viewpoints
  foreach mol [molinfo list] {
    if [info exists viewpoints($view_num,$mol,0)] {
      molinfo $mol set rotate_matrix   $viewpoints($view_num,$mol,0)
      molinfo $mol set center_matrix   $viewpoints($view_num,$mol,1)
      molinfo $mol set scale_matrix   $viewpoints($view_num,$mol,2)
      molinfo $mol set global_matrix   $viewpoints($view_num,$mol,3)
    } else {
      puts "View $view_num was not saved"}
  }
}


proc move_vp {start end {morph_frames 50} {accel smooth} {start_frame 0} {end_frame 0}} {
  global viewpoints
  

  foreach mol [molinfo list] {

    if [info exists viewpoints($start,$mol,0)] {
      set old_rotate($mol)  $viewpoints($start,$mol,0)
      set old_center($mol) $viewpoints($start,$mol,1)
      set old_scale($mol) $viewpoints($start,$mol,2)
      set old_global($mol)  $viewpoints($start,$mol,3)
    } else {
      puts "Starting view $start was not saved"} 

    if [info exists viewpoints($end,$mol,0)] {
      set new_rotate($mol) $viewpoints($end,$mol,0)
      set new_center($mol) $viewpoints($end,$mol,1)
      set new_scale($mol) $viewpoints($end,$mol,2)
      set new_global($mol)  $viewpoints($end,$mol,3)
    } else {
      puts "Ending view $end was not saved"} 

    #leave if don't have both viewpoints
    if {! ([info exists viewpoints($start,$mol,0)] && [info exists viewpoints($end,$mol,0)]) } {
      error "move_vp failed"
    }

    set old_rotate($mol) $viewpoints($start,$mol,0)
    set old_center($mol) $viewpoints($start,$mol,1)
    set old_scale($mol) $viewpoints($start,$mol,2)
    set old_global($mol)  $viewpoints($start,$mol,3)
    
    
    retrieve_vp $start   
    
    set needed_rotate($mol) [sub_mat  $new_rotate($mol) $old_rotate($mol)]

    
    set needed_center($mol) [sub_mat  $new_center($mol) $old_center($mol)]

    
    set needed_scale($mol) [sub_mat  $new_scale($mol) $old_scale($mol)]

    
    set needed_global($mol) [sub_mat  $new_global($mol) $old_global($mol)]

  }	

#  work out trajectory frame rate change:-----------------------------------
 
  set dcd_rate [expr ((0.0+$end_frame-$start_frame)/$morph_frames)] 
  puts " start: $start_frame  end:$end_frame  rate: $dcd_rate "
  
  set dcd_frame $start_frame
  
#  set start frame: --------------------------------------------------------

  animate goto $start_frame
  display update

# --------------------------------------------------------------------------

  for {set j 0} {$j<= ($morph_frames - 1)} {incr j} {
    foreach mol [molinfo list] {
      #set scaling to apply for this individual frame
      if {$accel == "smooth"} {
	#accelerate smoothkly to start and stop 
	set theta [expr 3.1415927 * (0.0 + $j)/($morph_frames - 1)] 
	set scale_factor [expr (1 -cos ($theta) ) /2]
	
      } else {
	#infinite acceleration to start and stop
	set scale_factor [expr (0.0 + $j)/($morph_frames - 1)] 
      }
      
      if {$j == $morph_frames} {
	#correct for roundoff errors, so ends in correct position
	set scale_factor 1.0
      }
      
      set current_rotate($mol) [add_mat $old_rotate($mol) [
							   scale_mat $needed_rotate($mol) $scale_factor]
			       ]
      
      set current_center($mol) [add_mat $old_center($mol) [
							   scale_mat $needed_center($mol) $scale_factor]
			       ]
      
      set current_scale($mol)  [add_mat $old_scale($mol) [
							  scale_mat $needed_scale($mol) $scale_factor]
			       ]
      
      set current_global($mol) [add_mat $old_global($mol) [
							   scale_mat $needed_global($mol) $scale_factor]
			       ]
      
      molinfo $mol set rotate_matrix $current_rotate($mol)
      molinfo $mol set center_matrix $current_center($mol)
      molinfo $mol set scale_matrix $current_scale($mol)
      molinfo $mol set global_matrix $current_global($mol)
      
      
    }
    
    set dcd_frame [expr (($dcd_frame+$dcd_rate))]
    animate goto $dcd_frame

    display update
    



  }
}
