#
# MovieBox                                                    MKuiper April 2012
#

Notes are not yet complete!!!             			- April 2012

#------------------------------------------------------------------------------

Often once we have made a molecular simulation we would like to make  
illustrations or movies to highlight important findings. This directory 
structure is designed to help make movies from a molecular trajectory using VMD 
and tcl scripts and then stitching frames together using Blender 
(or other movie making software).  

Software requirements for making movies: 
- you should have the latest version of VMD installed 
(currently 1.9.1 as of April 2012)

     http://www.ks.uiuc.edu/Research/vmd/

*  If using vmd for publications please cite:
Humphrey, W., Dalke, A. and Schulten, K., "VMD - Visual Molecular Dynamics", 
J. Molec. Graphics, 1996, vol. 14, pp. 33-38. 

- Blender or similar movie editing software. 
      http://www.blender.org/


>-------------------------------------------------------------------------------

The basic workflow is divided into 5 sections. 

1)  Setting the scene
2)  The molecular choreography 
3)  Making movie script / generating plot files.  
4)  Rendering the plot.dat files.
5)  Editing the images to make a movie. 


>-------------------------------------------------------------------------------
1) Setting the scene. 
>-------------------------------------------------------------------------------

Start vmd in the appropriate resolution for the type of movie you wish to make. 
for example:  
vmd -size 1024 768      - for projector presentations. (XGA)
vmd -size 1280 720      - for HD 720 movies. 
vmd -size 1920 1080     - for HD 1080 movies. -(takes a lot of CPU grunt!)

- or use the following command in a tk console: 
  display resize 1280 720     

Using vmd then read in the appropriate molecular files and create various 
representations you wish to illustrate. Once you are satisfied, make sure 
to save visualization state. 
eg) File -> Save Visualization State 

This is so you can easily reproduce a particular state should something go wrong.  
Make sure to turn on ambient occlusion lighting if special (time consuming and 
CPU intensive!) effects are desired! 
 
 eg) Display -> Display Settings -> External Renderer Options  -> shadows   on  
                                                               -> Amb.Occl  on
                                                             (ambient occlusion) 

>-------------------------------------------------------------------------------
2) The molecular choreography. 
>-------------------------------------------------------------------------------

In this section we use a modified version of the vmd tcl script "view_change_render.tcl"

This allows us to smoothly render from one specified viewpoint to another while 
stepping through the trajectory. The original tcl script would render frames at 
each step, but this can be rather time consuming if you want to use fancy ambient 
occlusion lighting effects. The new approach is to write and save the plot.dat files, 
to be rendered later on a cluster or desktop.  (Using the RenderBox subdirectory).  


*** New GUI in vmd ************************************************************
As of VMD version 1.9.1,  there is a new gui to be found under: 
   Extensions -> Visualization -> ViewChangeRender 

Though limited in its functionality, it can be a useful way of setting and saving 
viewpoints and using the movie maker plugin to quickly make a "User Defined Proceedure" 
animation. 

See  http://www.ks.uiuc.edu/Research/vmd/plugins/viewchangerender/ for more details. 

******************************************************************************

For more control, we'll use a modified version of the view_change_render_2012_v1 
script. This is a hacked version of the original view_change_render.tcl file which 
includes functionality to transition between trajectory frames while moving between 
viewpoints. 

Load into vmd the molecule and trajectory you wish to render.  Add molecular 
representations as desired. 

Open a tk console in vmd.    Extensions -> tk console 

In the console, source the view_change_render_script (the path depends on your computer!)
    
source ~mike/Desktop/Namd_jobdir_v4x/Project/MovieBox/Scripts/view_change_render_2012_v1.tcl


Move your molecule in vmd to your starting viewpoint you wish to render.  
Save the view point by typing in the tk console: 

 save_vp 1 

Now move the molecule to the second viewpoint and save: 

 save_vp 2 

To move from viewpoint 1 to viewpoint 2  simply type: 

 move_vp 1 2 500             (500 is the number of steps in the transistion) 




Once you have a number of viewpoints it is a good idea to save them into a file.  Type: 

 write_vps   my_viewpoints.tcl 

To retrieve them simply type in the tk console:

 source my_viewpoints.tcl 

The command move_vp simply moves the molecule from one viewpoint to another in the specified 
number of steps.  To render these frame use  "move_vp_render"  instead.   In our hacked 
version of the script, we generate tachyon dat files (the native vmd renderer) to be rendered later. 

The new usage of move_vp_render has a few extra arguments:  

move_vp_render start end first_frame_num dirName filePrefixName morph_frames  start_frame end_frame transitions* 

 # start              - starting viewpoint
 # end                - finishing viewpoint
 # first_frame_num    - numbering of first frame 
 # dirName            - directory where to store tachyon .dat files. 
 # filePrefixName     - prefix of file name 
 # morph_frames       - how many frames in the transition between viewpoints 
 # start_frame        - first frame in dcd trajectory for this movie segment. 
 # end_frame          - last frame in dcd trajectory for this movie segment.  
 # transitions* (optional)   default: smooth
 #    -can specify the type of transition between viewpoints with keywords:
 #           smooth, sharp, smooth_start, smooth_end, tumble, and ninja  



>-------------------------------------------------------------------------------
3) Making movie script / generating plot files.   
>-------------------------------------------------------------------------------

We can put a number of these render commands into a script and play them from the Tk console.  
An example movie script is found in: MovieBox/Scripts/movie_script_example_01.tcl 

We would play it to generate the .dat files (after loading the molecule, trajectory and viewpoints) by typing: 

 play Scripts/movie_script_example_01.tcl

which looks something like: 

 move_vp_render 1  2   1    movie_frames movie_segment_1  200   200    0 smooth;
 move_vp_render 2  2   201  movie_frames movie_segment_1  200     0  200 sharp;
  

This would populate the directory /movie_frames with movie_segment_1.dat files for later rendering.  

Make sure to enable ambient occlusion lighting for fancy effects! 
Display → Display Settings → Shadows (on) Amb. Occl. (on)
 

>-------------------------------------------------------------------------------
4) Rendering the plot.dat files. 
>-------------------------------------------------------------------------------

In order to render the frames we've just generated we will use RenderBox_v1

RenderBox is its own directory structure to systematically render .dat frames.  
It can be used on a local machine or pushed to a cluster to process the images in parallel. 

Basically we copy the .dat files to /Inbox  and then start the rendering script in the top directory. 

ie)  from the Renderbox directory: 
 
 mv ../movie_frames/* Inbox/ 

Before we start we can edit the render script to change the resolution and the anti-alias sampling  
of the image processing: (useful for creating higher resolution movies from the same .dat files.  
Note! The resolution should be the same ratio as you created the original files)    

 sed 's/^Resolution.*/Resolution 1280 720/' ../Temp/$i >../Temp/temp.dat
 sed 's/^    Samples.*/    Samples 16/' ../Temp/temp.dat >../Temp/temp_file.dat

Also check the vmd path to the Tachyon renderer is the same: 

 "/usr/local/lib/vmd/tachyon_LINUXAMD64" ../Temp/temp_file.dat -format TARGA -o ../Frames/$i.tga
   

Launch the local rendering script: 

 ./local_render_tachyon  

This takes a .dat file in /Inbox   moves it to /Temp,  generates the image which is put into /Frames


  
>-------------------------------------------------------------------------------
5) Editing the images to make a movie. 
>-------------------------------------------------------------------------------

Many programs can be used to stitch together image frames to form a movie. 
(Blender, kino, after-effects, etc) 

Blender has a steep learning curve, but also has much functionality plus can be used for animation work.  
In this capacity we are only using blender as a video sequence editor.  

Google “blender video editing “  for tutorials and videos on how to use the editor!  

Certain effects can be used in Blender such as merging video streams to create fade in/fade out cross 
over effects.  All the images frames should be stored in RenderBox/Frames

 
