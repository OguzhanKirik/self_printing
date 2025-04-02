#!/usr/bin/env python
# coding: utf-8




import subprocess
import sys
import argparse
import os
import time
from octo import octoprint
import json







def parseArguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("-s", "-source", dest='source', type=str, default="./data_structure_test/scan_0/body_scan.stl")
    parser.add_argument("-s_obj", "-source_obj", dest='source_obj', type=str, default="./data_structure_test/scan_0/body_scan_.obj")
    parser.add_argument("-sc", "-source_cut", dest='source_cut', type=str, default="./data_structure_test/scan_0/body_scan.stl_lower.stl")
    parser.add_argument("-scc", "-source_cut_cut", dest='source_cut_cut', type=str, default="./data_structure_test/scan_0/body_scan.stl_lower.stl_upper.stl")
    parser.add_argument("-t", "-target", dest='target', type=str, default="./data_structure_test/scan_0/body_scan_0.gcode")
    parser.add_argument("-sg", "-start_gcode", dest='start_gcode', type=str, default="start_g.gcode")
    parser.add_argument("-eg", "-end_gcode", dest='end_gcode', type=str, default="end_g.gcode")

    parser.add_argument("-c", "-cut", dest='cut', type=int, default=20)
    parser.add_argument("-n", "-number", dest='number', type=int, default=13)
    parser.add_argument("-off", "-offset", dest='offset', type=str, default=20)
    parser.add_argument("-cen", "-center", dest='center', type=str, default=117)
    parser.add_argument("-sca", "-scale", dest='scale', type=int, default=2.0) #2.5
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
    command = "slic3r {} --first-layer-speed 15 --z-offset {} --print-center {},166 -o {}".format(source,offset,center,target)
    print(command)
    subprocess.run(command, shell=True) 


    
def main(source, source_obj,target, cut, 
         number, source_cut,source_cut_cut,
         offset,scan_number,scale,center,
         start_gcode,end_gcode):
    #parameters to repeat same process
    n_scan = scan_number
    offset_ = offset * scan_number
    cut_down = cut * scan_number
    cut_up = cut_down + cut
    scaling_factor=scale
    center_=center
    start_gcode_ = start_gcode
    end_gcode_ = end_gcode
    ns_rep= source.rfind("/")
    nt_rep = target.rfind("/")
    nsc_rep = source_cut.rfind("/")
    nscc_rep = source_cut_cut.rfind("/")
    



    #run start_gccode
    print('--> Running start_gcode !!!') 
#             octopi.start_print(start.gcode)
#             octopi2.start_print(start.gcode)
#             octopi3.start_print(start.gcode)
#             octopi4.start_print(start.gcode)
#             octopi5.start_print(start.gcode)
#             octopi6.start_print(start.gcode)
#             octopi7.start_print(start.gcode)
#             octopi8.start_print(start.gcode)
#             octopi9.start_print(start.gcode)    

    # 9 octoprint instances
    with open("octopi_config.json") as json_data_file:
        data = json.load(json_data_file)
        #print(data['connect']['url'])
       
    
    print('--> Connecting printers')    
#     octopi = octoprint(data['connect']['url'],data['connect']['apikey'])
#     octopi2 = octoprint(data['connect2']['url'],data['connect2']['apikey'])
#     octopi3 = octoprint(data['connect3']['url'],data['connect3']['apikey'])
#     octopi4 = octoprint(data['connect4']['url'],data['connect4']['apikey'])
#     octopi5 = octoprint(data['connect5']['url'],data['connect5']['apikey'])
#     octopi6 = octoprint(data['connect6']['url'],data['connect6']['apikey'])
#     octopi7 = octoprint(data['connect7']['url'],data['connect7']['apikey'])
#     octopi8 = octoprint(data['connect8']['url'],data['connect8']['apikey'])
#     octopi9 = octoprint(data['connect9']['url'],data['connect9']['apikey'])
#     octopi.connect()
#     octopi2.connect()
#     octopi3.connect()
#     octopi4.connect()

#     octopi5.connect()
#     octopi6.connect()

#     octopi7.connect()
#     octopi8.connect()
#     octopi9.connect()


    ## define printer profile::bed temperature...
    ##Important
    try:
        while(n_scan <= number):

            ## resume printers if the operation is not finished
            source_obj  = source_obj[:(ns_rep-1)] + '{}'.format(n_scan) + source_obj[(ns_rep):]
            source  = source[:(ns_rep-1)] + '{}'.format(n_scan) + source[(ns_rep):]
            #target  = target[:(nt_rep-1)] + '{}'.format(n_scan) + target[(nt_rep):]
            #target  = target[:(nt_rep-1)] + '{}'.format(n_scan) + target[nt_rep:(nt_rep+10)] + '_' + '{}'.format(n_scan) + target[(nt_rep+10):]
            target  = target[:(nt_rep-1)] + '{}'.format(n_scan) + target[nt_rep:(nt_rep+11)]  + '{}'.format(n_scan) + target[(nt_rep+12):]

            source_cut  = source_cut[:(nsc_rep-1)] + '{}'.format(n_scan) + source_cut[(nsc_rep):]
            source_cut_cut  = source_cut_cut[:(nscc_rep-1)] + '{}'.format(n_scan) + source_cut_cut[(nscc_rep):]


            if os.path.isfile(source_obj):
                ## rotate 90 degree the model around x and save as stl
                rotate_model(source_obj,source,scaling_factor) 
                print('--> Model rotated,scaled and saved as stl')


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
                slice_model(source_cut_cut,offset_,center_,target)

                print('--> Model scalled,offset and sliced')
                print('Model saved in {}'.format(target))


                n_scan +=1
                cut_down += cut
                cut_up += cut
                offset_ =offset * n_scan
                #time.sleep(5)            





                ## Octo-print upload files
    #             octopi.upload(target)
    #             octopi2.upload(target)
    #             octopi3.upload(target)
    #             octopi4.upload(target)
    #             octopi5.upload(target)
    #             octopi6.upload(target)
    #             octopi7.upload(target)
    #             octopi8.upload(target)
    #             octopi9.upload(target)
                print('--> Files uploaded on printers')    


                ##octoprint start printing
                ## if printing continues, wait until it finishes

#                 while True:
#                     n_octo = target.rfind("/")
#                     target_octoprint =  target[(n_octo+1):]
#                     if (octopi.is_printing==False and octopi2.is_printing==False and octopi3.is_printing==False
#                        and octopi4.is_printing==False and octopi5.is_printing==False and octopi6.is_printing==False
#                        and octopi7.is_printing==False and octopi8.is_printing==False and octopi9.is_printing==False):
#                         octopi.start_print(target_octoprint)
#                         octopi2.start_print(target_octoprint)
#                         octopi3.start_print(target_octoprint)
#                         octopi4.start_print(target_octoprint)
#                         octopi5.start_print(target_octoprint)
#                         octopi6.start_print(target_octoprint)
#                         octopi7.start_print(target_octoprint)
#                         octopi8.start_print(target_octoprint)
#                         octopi9.start_print(target_octoprint)
#                         print('--> Print started') 
#                         break
#                     else:
#                         print('Printers are busy!!!Print continues..')
#                         time.sleep(20)

            else:
                print("No new scan found, waiting for the scan {} !!!".format(n_scan))
                time.sleep(20)
    except KeyboardInterrupt:
        print('--> Procedure is killed!!!')
        print('--> Running end_gcode !!!') 
#             octopi.start_print(end.gcode)
#             octopi2.start_print(end.gcode)
#             octopi3.start_print(end.gcode)
#             octopi4.start_print(end.gcode)
#             octopi5.start_print(end.gcode)
#             octopi6.start_print(end.gcode)
#             octopi7.start_print(end.gcode)
#             octopi8.start_print(end.gcode)
#             octopi9.start_print(end.gcode)        


# In[4]:


if __name__ == '__main__':
    args = parseArguments()
    main(args.source, args.source_obj, args.target, args.cut,args.number,
    args.source_cut,args.source_cut_cut,args.offset,args.scan_number,args.scale,
    args.center,args.start_gcode,args.end_gcode)







