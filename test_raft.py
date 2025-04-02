#!/usr/bin/env python
# coding: utf-8

# In[1]:


import subprocess
import sys
import argparse
import os
import time
from octo import octoprint
import json


# In[ ]:





# In[5]:


def parseArguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("-s", "-source", dest='source', type=str, default="./data_structure_test/scan_0/body_scan.stl")
    parser.add_argument("-s_obj", "-source_obj", dest='source_obj', type=str, default="./data_structure_test/scan_0/body_scan.obj")
    parser.add_argument("-sc", "-source_cut", dest='source_cut', type=str, default="./data_structure_test/scan_0/body_scan.stl_lower.stl")
    parser.add_argument("-scc", "-source_cut_cut", dest='source_cut_cut', type=str, default="./data_structure_test/scan_0/body_scan.stl_lower.stl_upper.stl")
    parser.add_argument("-t", "-target", dest='target', type=str, default="./data_structure_test/scan_0/body_scan_0.gcode")
    parser.add_argument("-sg", "-start_gcode", dest='start_gcode', type=str, default="start.gcode")
    parser.add_argument("-eg", "-end_gcode", dest='end_gcode', type=str, default="end.gcode")

    parser.add_argument("-c", "-cut", dest='cut', type=int, default=20)
    parser.add_argument("-n", "-number", dest='number', type=int, default=10)
    parser.add_argument("-off", "-offset", dest='offset', type=str, default=20)
    parser.add_argument("-r", "-raft", dest='raft', type=str, default=100)

    parser.add_argument("-cen", "-center", dest='center', type=str, default=125)
    parser.add_argument("-sca", "-scale", dest='scale', type=int, default=0.5)#2.5
    parser.add_argument("-n_scan", "-scan_number", dest='scan_number', type=int, default=0)

    args = parser.parse_args()
    return args


def rotate_model(source_obj,source,scaling_factor):
    command_cut = "prusa-slicer --export-stl --rotate-x 90 --scale {} {} -o {}".format(scaling_factor,source_obj,source)
    print(command_cut)
    subprocess.run(command_cut, shell=True)


def cut_model(cutting_parameter, source):
    command_cut = "slic3r --cut {} {}".format(cutting_parameter,source)
    print(command_cut)
    subprocess.run(command_cut, shell=True)
     

def slice_model(source,offset,center,target):
    #command = "slic3r {} --scale {} --z-offset {} -o {}".format(source,scaling_factor,offset,target)
    command = "slic3r {} --z-offset {} --print-center {},{} -o {}".format(source,offset,center,center,target)
    print(command)
    subprocess.run(command, shell=True) 

def slice_model_raft(source,offset,center,target,raft):
    #command = "slic3r {} --scale {} --z-offset {} -o {}".format(source,scaling_factor,offset,target)
    command = "slic3r {} --raft-layers {} --z-offset {} --print-center {},{} -o {}".format(source,raft,offset,center,center,target)
    print(command)
    subprocess.run(command, shell=True) 


    
def main(source, source_obj,target, cut, 
         number, source_cut,source_cut_cut,
         offset,scan_number,scale,center,
         start_gcode,end_gcode,raft):
    #parameters to repeat same process
    n_scan = scan_number
    offset_ = offset * scan_number
    raft_layer=raft
    cut_down = (cut * scan_number) - raft
    cut_up = cut_down + cut
    scaling_factor=scale
    center_=center
    start_code = start_gcode
    end_code = end_gcode
    ns_rep= source.rfind("/")
    nt_rep = target.rfind("/")
    nsc_rep = source_cut.rfind("/")
    nscc_rep = source_cut_cut.rfind("/")
    


    # 9 octoprint instances
    with open("octopi_config.json") as json_data_file:
        data = json.load(json_data_file)
        #print(data['connect']['url'])
       




        ##upload startgcode
    print('--> Uploading start_gcode !!!') 



    ## define printer profile::bed temperature...
    ##Important
    try:
        while(n_scan <= number):

            ## resume printers if the operation is not finished
            source_obj  = source_obj[:(ns_rep-1)] + '{}'.format(n_scan) + source_obj[(ns_rep):]
            source  = source[:(ns_rep-1)] + '{}'.format(n_scan) + source[(ns_rep):]
            #target  = target[:(nt_rep-1)] + '{}'.format(n_scan) + target[(nt_rep):]
            target  = target[:(nt_rep-1)] + '{}'.format(n_scan) + target[nt_rep:(nt_rep+11)]  + '{}'.format(n_scan) + target[(nt_rep+12):]

            source_cut  = source_cut[:(nsc_rep-1)] + '{}'.format(n_scan) + source_cut[(nsc_rep):]
            source_cut_cut  = source_cut_cut[:(nscc_rep-1)] + '{}'.format(n_scan) + source_cut_cut[(nscc_rep):]


            if os.path.isfile(source_obj):
                ## rotate 90 degree the model around x and save as stl
                rotate_model(source_obj,source,scaling_factor) 
                print('--> Model rotated,scaled and saved as stl')

                ##Add raft layer
                #add_raft(raft_layer,source)

                # Cutter upper boundary
                cut_model(cut_up,source)
                print('--> Upper part is cut')

                 # Cutter downer boundary
                if cut_down==0:
                    command_c_ = "prusa-slicer --export-stl {} -o {}".format(source_cut,source_cut_cut)
                    print(command_c_)
                    subprocess.run(command_c_, shell=True)
                    print('--> Downer part is created')
                else:
                    cut_model(cut_down,source_cut)
                    print('--> Downer part is cut')


                # offset,cented,slice the stl
                #slice_model(source_cut_cut,offset_,target)
                if (n_scan==0):
                    print('--> Raft Added!!!')
                    slice_model_raft(source_cut_cut,offset_,center_,target,raft_layer)
                else:
                    slice_model(source_cut_cut,offset_,center_,target)

                print('--> Model scalled,offset and sliced')
                print('Model saved in {}'.format(target))


                n_scan +=1
                cut_down = cut_down + cut - raft_layer
                cut_up = cut_up + cut -raft_layer
                offset_ =(offset * n_scan) +raft_layer
                time.sleep(5)            





                ##octoprint start printing
                ## if printing continues, wait until it finishes


            else:
                print("No new scan found, waiting for the scan {} !!!".format(n_scan))
                time.sleep(20)
    except KeyboardInterrupt:
        print('--> Procedure is killed!!!')
        print('--> Running end_gcode !!!') 


if __name__ == '__main__':
    args = parseArguments()
    main(args.source, args.source_obj, args.target, args.cut,args.number,
    args.source_cut,args.source_cut_cut,args.offset,args.scan_number,args.scale,
    args.center,args.start_gcode,args.end_gcode,args.raft)








#




