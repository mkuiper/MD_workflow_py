# Example movie script file.                 April 2012  MKuiper    
# 
# to use with view_change_render_2012_v1.tcl 

# After loading a scene in a tk console  type:  
#       play movie_script_01.tcl  

#  new usage of move_vp_render: 
# move_vp_render start end first_frame_num dirName filePrefixName morph_frames  start_frame end_frame transitions* 
    # start              - starting viewpoint
    # end                - finishing viewpoint
    # first_frame_num    - numbering of first frame 
    # dirName            - directory where to store tachyon .dat files. 
    # filePrefixName     - prefix of file name 
    # morph_frames       - how many frames in the transition between viewpoints 
    # start_frame        - first frame in dcd trajectory for this movie segment. 
    # end_frame          - last frame in dcd trajectory for this movie segment.  
    # transitions* (optional)   default: smooth
    #                    - can specify the type of transition between viewpoints with keywords:
    #                      smooth, sharp, smooth_start, smooth_end, tumble, and ninja  

move_vp_render 1  2   1    movie_frames movie_segment_1  200   200    0 smooth;
move_vp_render 2  2   201  movie_frames movie_segment_1  200     0  200 sharp;

# change rendering: 
mol showrep    0 0 off;

move_vp_render 2  2   1    movie_frames movie_segment_2  200     0   200;
move_vp_render 2  3   201  movie_frames movie_segment_2  200   200   200;

mol showrep    0 1 off;
mol showrep    0 2 off;

move_vp_render 2  3   1    movie_frames movie_segment_3  200   200   200;



