#-*- coding:utf-8 -*-
import sys 
import re
import os
import time
import fnmatch
import codecs
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
FWR_counter = 0	
ANR_counter = 0
Force_close_counter = 0
OOS_counter = 0
FWR_counter	= 0 
def filter_path(root,single_level=False,yield_folder=False,pattern=""):
	for path,subdir,filename in os.walk(root):
			if yield_folder:
				filename.extend(subdir)
			for name in filename:
				if re.match(pattern,name) and os.path.isfile(os.path.join(path,name)) and (int(hour_line)*3600- (time.time()-os.path.getmtime(os.path.join(path,name)))>0):
					yield os.path.join(path,name)
			if single_level:
				break

def search_event(device):
	return filter_path(device,single_level=False,pattern="event")

def search_radio(device):
	return filter_path(device,single_level=False,yield_folder=False,pattern="radio")

def parse_event(file_name):
	global ANR_counter
	global Force_close_counter
	global FWR_counter
	with file(file_name) as f:
		for line in f.readlines():
			if re.search("am_crash",line):
				print "Found force close issue!!!"
				print "Issue log : %s"%file_name
				write_to_log(file_name+"\r\n"+line+"\r\n",log_name)
				Force_close_counter +=1				
			elif re.search("am_anr",line):
				print "Found anr issue!!!"
				print "Issue log : %s"%file_name
				write_to_log(file_name+"\r\n"+line+"\r\n",log_name)
				ANR_counter +=1				
			elif re.search("boot_progress_start",line):
				print "Found boot restart issue!!!"
				print "Issue log : %s"%file_name
				write_to_log(file_name+"\r\n"+line+"\r\n",log_name)
				FWR_counter +=1
				
def parse_radio(file_name):
	global OOS_counter
	lines=''
	with file(file_name) as f :
		for line in f.readlines():
			if re.search("无服务",line):	
				lines = lines+line.encode('utf-8')+"\r\n"
		if len(lines)>0:
			print "Found OOS issue!!!"
			print "Issue log : %s"%file_name
			write_to_log(file_name+"\r\n"+lines+"\r\n",log_name)
			OOS_counter +=1
	
def write_to_log(msg,log):
	with codecs.open(log,"a",'utf-8') as f:
		f.write('#---------------------------------------------------------#\n# Found issue                                             #\n#---------------------------------------------------------#\n')
		f.write(msg)

def finder():
	for device in device_log_path:		
		for event_log in search_event(device):
			parse_event(event_log)
			
		for radio_log in search_radio(device):
			parse_radio(radio_log)				

if __name__ == '__main__':
	log_name = "report_%s.txt"%time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
	hour_line = raw_input("Please input hours number:")
	hour_line = int(hour_line)
	print "you want to scan %d hours' log  , it will take a few minutes"%hour_line
	branch_path = r"\d\adblogs"
	runner_root_list = []
	#with codecs.open(log_name,"w",'utf-8') as f:
	#	pass
	with file('RunnerRoot.txt','r') as f:
		runner_root_list = f.readlines()
		runner_root_list = [r"\\" +i.strip().encode('utf-8').decode('utf-8')+branch_path for i in runner_root_list]
	device_log_path=[]
	for path in runner_root_list:
		for file_name in os.listdir(path):
			if os.path.isdir(os.path.join(path,file_name)) and (3*24 * 3600-(time.time()-os.path.getmtime(os.path.join(path,file_name)))>0) and re.search("\w{6,12}",file_name) and len(file_name)<12:
				device_log_path.append(os.path.join(path,file_name))
	#print device_log_path
	print "Total devices: %d"%len(device_log_path)
	finder()
