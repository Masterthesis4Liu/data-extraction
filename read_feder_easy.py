# -*- coding: utf-8 -*-
"""
Created on Wed Jun 07 20:31:57 2017

@author: Jinzhao Liu
"""
#read festigkeit
from odbAccess import *
from abaqus import *
from abaqusConstants import *
import os
import sys
import string
import collections
import shutil
import csv
import copy
import numpy as np

path ="D:/DrapeOpti"
data_directory=path + '/' +'Draping_Data_extracted'
if not os.path.exists(data_directory):
    os.mkdir(directory)
files = os.listdir(path)

csv_path = os.getcwd()
total_csv = open(path+'/'+'total_spring.csv','wb')
csv_writer0 = csv.writer(total_csv,quoting=csv.QUOTE_ALL)
#50 spring festigkeit, can not be changed in the process
List_spring_festikeit=[]
#---------------------------------------------------
def readDisplacementAndForce(odbfile):
    odb = openOdb(odbfile)
    myAssembly = odb.rootAssembly
    allStepNames = odb.steps.keys()
    lastStep  = allStepNames[-1]
    lastFrame = odb.steps[lastStep].frames[-1]
    
    
#function to get the displacement and the force of spring
    dict_spring_displacement ={} 
    dict_spring_force = {}
    def GetValue(eleName):
        SpringEle = myAssembly.elementSets[eleName]
        SpringEle_value0 = lastFrame.fieldOutputs['E'].getSubset(region = SpringEle).values[0]#E11 is the ralative displacement across the spring
        SpringEle_value1 = lastFrame.fieldOutputs['S'].getSubset(region = SpringEle).values[0]#S11 force in the spring
        springLabel = SpringEle_value0.elementLabel
        springDisplacemnet = SpringEle_value0.data[0]
        springForce = SpringEle_value1.data[0]
        dict_spring_displacement[springLabel] = springDisplacemnet
        dict_spring_force[springLabel] = springForce    
#get the 50 spring elementsets
    spring_ele_name_list =[]
    spring_ele_sets = myAssembly.elementSets.keys()
    for eleSet in spring_ele_sets:
        if 'SPRINGS' in eleSet:
            spring_ele_name_list.append(eleSet)
            GetValue(eleSet)

    sorted_dict_spring_displacement = collections.OrderedDict(sorted(dict_spring_displacement.items()))
    sortes_dict_spring_force = collections.OrderedDict(sorted(dict_spring_force.items()))

    list_spring_displacement = []
    list_spring_force = []
    for k,v in sorted_dict_spring_displacement.items():
        list_spring_displacement.append(v)
    for k,v in sortes_dict_spring_force.items():
        list_spring_force.append(v)    
   
   
    return list_spring_displacement,list_spring_force
    
#-----------------------------------------------------
def ReadOutFestigkeit():
    try:
        Feder_festigkeit_csv=open(os.path.join(path,'Feder_festigkeit.csv'),'r')
        reader= csv.reader(Feder_festigkeit_csv,quoting=csv.QUOTE_ALL)
        Dict_reader=csv.DictReader(Feder_festigkeit_csv)
        for row in reader:
            if reader.line_num==1:
                continue
            List_spring_festikeit.append(row)

    except IOError:
        print 'Error can not find or read the file Feder_festigkeit.csv'
    Feder_festigkeit_csv.close()

ReadOutFestigkeit()
#total list item
List_total_item = copy.deepcopy(List_spring_festikeit)

def ReadInput(file,model_index,list_displacement,list_force):
    if os.path.exists('test.txt'):
        os.remove("test.txt")
    t_f=open("test.txt",'w')
    list_festigkeit=[]

    for line in file:
        if len(line)>0 and not line.startswith('*'):
            if line.find(",")==-1 and not line=='\n':
                t_f.write(line)
                line=line.strip('\n')
                list_festigkeit.append(line)
            else:
                Id=line.split(',')[0]
                string.strip(Id)
                t_f.write(Id)
    t_f.close()
    data_name = "springStiffness_Run"+model_index+".csv"
    csv_path = data_directory +'/' + data_name
    #f_csv=open('feder_festigkeit.csv','wb')
    f_csv=open(csv_path,'wb')
    csv_writer=csv.writer(f_csv,quoting=csv.QUOTE_ALL)
    csv_writer.writerow(['ID','Number','x','y','z','c','d','f'])
    New_List_spring_festikeit = copy.deepcopy(List_spring_festikeit)
    for i in range(0,len(list_festigkeit)):
        row_list=New_List_spring_festikeit[i]
        row_list.append(list_festigkeit[i])
        row_list.append(list_displacement[i])
        row_list.append(list_force[i])
        #csv_writer.writerow([row_list[0],row_list[1],row_list[2],row_list[3],row_list[4],list_festigkeit[i]])
        csv_writer.writerow(row_list)
        total_row_list = List_total_item[i]
        total_row_list.append(list_festigkeit[i])
        total_row_list.append(list_displacement[i])
        total_row_list.append(list_force[i])
    f_csv.close()

#write all the spring festigkeit in one table
#def WriteInTotal():
file_index=0
for file in files:
    if os.path.isdir(path+'/'+file) and os.path.exists(path+'/'+file+'/'+'Springs.inp'):
        new_path = path +'/' +file
        os.chdir(new_path)
        odbfile = new_path + '/' + 'DrapingJob.odb'
        list_displacement,list_force = readDisplacementAndForce(odbfile)
        #can not direct manipulate a .inp type file
        if os.path.exists('Springs.txt'):
            os.remove("Springs.txt")
        shutil.copy("Springs.inp","Springs.txt")
        f=open("Springs.txt",'r')
        model_index = file.split('.')[1]
        ReadInput(f,model_index,list_displacement,list_force)
        f.close()
        os.remove("Springs.txt")
        file_index +=1

row_in_total=['ID','Number','x','y','z']
for i in range(1,file_index+1):
    add_str = 'c'+str(i)
    add_str1 = 'd' + str(i)
    add_str2 = 'f' + str(i)
    row_in_total.append(add_str)
    row_in_total.append(add_str1)
    row_in_total.append(add_str2)
    

csv_writer0.writerow(row_in_total)
for total_item in List_total_item:
    csv_writer0.writerow(total_item)
total_csv.close()








