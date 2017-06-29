import os
import glob
import shutil
import subprocess
import time
import csv

from odbAccess import *
from abaqus import *
from abaqusConstants import *
from caeModules import *
from driverUtils import executeOnCaeStartup

import numpy as np

dict_connectivity={}
dict_coordinates={}

#calculate the center coordinate
def center_calculate(node_coordinates):
    node1= node_coordinates[0]
    node2= node_coordinates[1]
    node3= node_coordinates[2]
    coordinate1= dict_coordinates[node1]#type =numpy.ndarray
    coordinate2= dict_coordinates[node2]
    coordinate3= dict_coordinates[node3]
    c_x=(coordinate1[0]+coordinate2[0]+coordinate3[0])/3
    c_y=(coordinate1[1]+coordinate2[1]+coordinate3[1])/3
    c_z=(coordinate1[2]+coordinate2[2]+coordinate3[2])/3
    return (c_x,c_y,c_z)
            
def evaluatePlyAndScreenshot(odb,instance):
    esets = odb.rootAssembly.elementSets
    inst = instance
    allStepNames = odb.steps.keys()
    lastStep  = allStepNames[-1]
    lastFrame = odb.steps[lastStep].frames[-1] #Liste mit allen frames
	
    ef_data = []	#Initialisiere eine Liste 

    if(esets.has_key('ELEMSTOEVAL')):	#Falls es das Element-Set Quadrant 1 gibt, dann schreibe die Dehnungsdaten in die Liste
        elq1 = odb.rootAssembly.elementSets['ELEMSTOEVAL'] #type=odbSet
    ef_dataQ1=lastFrame.fieldOutputs['EFABRIC'].getSubset(region=elq1,position=INTEGRATION_POINT,elementType = 'M3D3').values
    iter_num =len(ef_dataQ1)
    for i in range(0,iter_num):
        if ef_dataQ1[i].instance.name== 'PLY_01':
            ef_data.append(ef_dataQ1[i])   
    return ef_data

path="D:/DrapeOpti"
data_directory=path + '/' +'Draping_Data_extracted'
if not os.path.exists(data_directory):
    os.mkdir(directory)
#total_csv =open(path+'/'+'total.csv','wb')
#csv_writer0 = csv.writer(total_csv,quoting=csv.QUOTE_ALL)

#list_total_row=[]

files=os.listdir(path)
file_index=1
for file in files:
    if os.path.isdir(path+'/'+file) and os.path.exists(path+'/'+file+'/'+'DrapingJob.odb'):
        new_path=path +'/' +file
        os.chdir(new_path)
        odb=session.openOdb('DrapingJob.odb')
        ass = odb.rootAssembly
        
        model_index = file.split('.')[1]
        data_name = "shearAngle_Run"+model_index+".csv"
        csv_path = data_directory +'/' + data_name 
        
        #f_csv =open('shear_angle.csv','wb')
        f_csv =open(csv_path,'wb')
        csv_writer = csv.writer(f_csv,quoting=csv.QUOTE_ALL)
        csv_writer.writerow(['ID','connect','gravity center','shear angle'])
        if ass.instances.has_key('PLY_01'):
            inst = odb.rootAssembly.instances['PLY_01']
        ef_data = evaluatePlyAndScreenshot(odb=odb,instance=inst)
        
        for element in inst.elements:
            elemType = element.type
            if elemType=='M3D3':
                elemLabel=element.label
                elemconnectivity = element.connectivity
                dict_connectivity[elemLabel]=elemconnectivity
                
        for node in inst.nodes:
            nodeLabel = node.label
            nodecoordinates = node.coordinates
            dict_coordinates[nodeLabel]=nodecoordinates
        list_row=[]      
        for index,ef_data1 in enumerate(ef_data):
            eF_eps12= ef_data1.data[3] 
            elmnLabel = ef_data1.elementLabel
            list_row.append(elmnLabel)
            
#            index_label=(file_index-1)*4
#            list_total_row[index,index_label] =elmnLabel#
            
            nodes_connectivity=dict_connectivity[elmnLabel]
            list_row.append(nodes_connectivity)
            
#            index_connect=1+(file_index-1)*4
#            list_total_row[index,index_connect]=nodes_connectivity#
            
            center_node = center_calculate(nodes_connectivity)
            list_row.append(center_node)
            
#            index_center=2+(file_index-1)*4
#            list_total_row[index,index_center]=center_node#
            
            list_row.append(eF_eps12)
            
#            index_eps12=3+(file_index-1)*4
#            list_total_row[index,index_eps12]=eF_eps12#
            
            csv_writer.writerow(list_row)
            
#            if file_index==1:
#                list_total_row.append(list_row)
#            else:
#                #list_total_row[index].append(list_row) 
#                list_total_row[index].append(elmnLabel) 
#                list_total_row[index].append(nodes_connectivity) 
#                list_total_row[index].append(center_node) 
#                list_total_row[index].append(eF_eps12) 
            list_row=[]
        f_csv.close()
        dict_connectivity.clear()
        dict_coordinates.clear()
        file_index+=1            

#heading_row=[]
#for i in range(1,file_index):
#    add_str = 'ID'+str(i)
#    heading_row.append(add_str)
#    add_str = 'connect'+str(i)
#    heading_row.append(add_str)
#    add_str = 'gravity center'+str(i)
#    heading_row.append(add_str)
#    add_str = 'shear angle'+str(i)
#    heading_row.append(add_str)
#csv_writer0.writerow(heading_row)
#
#for total_item in list_total_row:
#    csv_writer0.writerow(total_item)
#total_csv.close()        





