#! /bin/python3

#How to run this script:

#format:	python3 <thisfilename>.py <authlogfilename>.log
#example:	python3 auth-log-reader.py auth.log
#example2:	python3 auth-log-reader.py /var/log/auth.log
#==================================================

#to do:
#display log entries with ip address and count
#option to print only the categories the user wants to see

# if log file has too many lines, hard to navigate and read
# some types of lines do not belong to any category?
#some filters not working on some log entries.
#==================================================

#	TABLE OF CONTENTS
#	1. Log Parse auth.log: Extract command usage. 
#	1.1. Include the Timestamp. 
#	1.2. Include the executing user. 
#	1.3. Include the command. 

#	2. Log Parse auth.log: Monitor user authentication changes. 
#	2.1. Print details of newly added users, including the Timestamp. 
#	2.2. Print details of deleted users, including the Timestamp. 
#	2.3. Print details of changing passwords, including the Timestamp. 
#	2.4. Print details of when users used the su command.
#	2.5. Print details of users who used the sudo; include the command. 
#	2.6. Print ALERT! If users failed to use the sudo command; include the command

#==================================================
# ~ ---------------
# ~ EVENT TYPE: new_user
# ~ EXECUTION_USERNAME: abc    # the user who executed this useradd command
# ~ NEW_USERNAME: testuser      # the username created
# ~ TIMESTAMP: 10-04-2024 06:34:21     # preferably in dd-mm-yyyy HH:MM:SS format
# ~ ---------------
#==================================================

banner = """
    ██╗      ██████╗  ██████╗                                   
    ██║     ██╔═══██╗██╔════╝                                   
    ██║     ██║   ██║██║  ███╗                                  
    ██║     ██║   ██║██║   ██║                                  
    ███████╗╚██████╔╝╚██████╔╝                                  
    ╚══════╝ ╚═════╝  ╚═════╝                                   
                                                                
 █████╗ ███╗   ██╗ █████╗ ██╗  ██╗   ██╗███████╗███████╗██████╗ 
██╔══██╗████╗  ██║██╔══██╗██║  ╚██╗ ██╔╝╚══███╔╝██╔════╝██╔══██╗
███████║██╔██╗ ██║███████║██║   ╚████╔╝   ███╔╝ █████╗  ██████╔╝
██╔══██║██║╚██╗██║██╔══██║██║    ╚██╔╝   ███╔╝  ██╔══╝  ██╔══██╗
██║  ██║██║ ╚████║██║  ██║███████╗██║   ███████╗███████╗██║  ██║
╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝╚═╝   ╚══════╝╚══════╝╚═╝  ╚═╝
""" 
print(banner)

#import modules
from datetime import *
import sys

#save log filepath+filename input when user ran this script
# (e.g. python3 <this-file.py> <log-file.log>)
authfile = sys.argv[1] 

#read auth.log file
file = open(authfile,"r")
fdata = file.readlines()

#1.1. Reformat the line's timestamp into a readable setting
def showtime(original_timestamp):
	reformat_time = datetime.strptime(original_timestamp, "%Y-%m-%dT%H:%M:%S.%f%z")
	return reformat_time.strftime("%a %d %b %Y, %I:%M:%S%p")
	
#==================================================
#file info script

#save as variable, log file's time start/end/duration
first_time=showtime(fdata[0].split()[0])
last_time=showtime(fdata[-1].split()[0])
time_format="%a %d %b %Y, %I:%M:%S%p"
tduration = datetime.strptime(last_time, time_format) - datetime.strptime(first_time, time_format)
                                 
# returns total duration in minutes, seconds
minutes1 = divmod(tduration.total_seconds(), 60) 
 
# returns the difference of the time of the day (minutes, seconds)
minutes2 = divmod(tduration.seconds, 60) 

#display log file's info
print(f"""
Log File		{sys.argv[1]}
Total Lines		{len(fdata)}
Start Time		{first_time}
Stop Time		{last_time}
Duration		{tduration.days} Days, {minutes2[0]} Minutes, {minutes2[1]} Seconds (Total Minutes: {int(minutes1[0])})
""")

#==================================================
#data counter script

#save as variable, counters for data
count_newuser = 0
count_deluser = 0
count_chpass = 0
count_su = 0
count_sudo = 0
count_failsudo = 0
count_uncat = 0

#save as variable, if statement conditions
newuser="new user"
deluser="delete user"
passch="password changed"
suuser="(to "

sudocmd=("sudo" and "command=")
sudofail=("sudo" and "not")
loginopen="session opened"

#define function to count data
def countall():
	global count_newuser,count_deluser,count_chpass,count_su,count_sudo,count_failsudo,count_uncat

	if (newuser in line):
		count_newuser += 1
	elif (deluser in line):
		count_deluser += 1
	elif (passch in line):
		count_chpass += 1
	elif (suuser in line):
		count_su += 1
		
	elif (sudofail in line.lower()):
		count_failsudo += 1
	elif (sudocmd in line.lower()):
		count_sudo += 1

	else:
		count_uncat += 1

#loop through log and count
for line in fdata:
	section = line.split(" ") 	
	countall()

#display log data
print(f"""
New Users Created	{count_newuser}
Users Deleted		{count_deluser}
Passwords Changed	{count_chpass}
Times Switched User	{count_su}
Sudo Commands Used	{count_sudo+count_failsudo} ({count_failsudo} Fails)
Uncategorised Lines	{count_uncat}
""")

#==================================================
#1.2. Display name of user who executed the command
showuser = section[1]

#==================================================

def main_blocks():
	#category line counter, start with 1 instead of 0 for readability
	countblocklines=1

	
	#prepare in a list, unique content for each category, to be printed when called
	fillintheblanks=[
	("'useradd' Add-User Logs		", count_newuser, "CREATED USER", newuser),
	("'userdel' Delete-User Logs		", count_deluser, "DELETED USER", deluser),
	("'passwd' Password-Change Logs		", count_chpass, "PASSWORD CHANGED FOR", passch),
	("'su' Switched-to-Substitute-User Logs	", count_su, "SWITCHED TO USER", suuser),
	("'sudo' Super-User-Command Logs		", count_sudo+count_failsudo, "SUDO COMMAND", sudocmd),
	("[ALERT!] 'sudo' Failed-Sudo-Command Logs", count_failsudo, "FAILED SUDO COMMAND", sudofail),
	("Uncategorised lines			", count_uncat, "LINE", " ")
	]
	
	#save a list of fillintheblanks's index numbers
	lengthofcategories = [i for i in range(len(fillintheblanks))]
	
	#print header for each category
	for idx, (block_title, count_title, subtitle_col, text_condition) in enumerate(fillintheblanks):
		print(f"""
===========================================================================================
 {block_title}					Count:[{count_title}]
===========================================================================================
#	TIME				USER	SU USER		{subtitle_col}""")

		#loop through log file
		for line in fdata:
			line = line.strip()
			section = line.split(" ")
				
			#filter file's content to fit category conditions
			if (text_condition in line.lower()):
					
				#Display 'su' username if applicable
				if 'pam_unix' not in section[3] and ':' == section[4]:
					col_runas=section[3]
				else:
					col_runas='-	'
						
				#Uncategorised lines put together
				if idx == lengthofcategories[-1]:
					#if don't fulfill ANY text condition
					if all(x not in line.lower() for x in ['new user','delete user','password changed', '(to ', 'command=', 'not']):
						#print whole line as-is, except time and user
						col_cmd=" ".join(section[2:])
						
						#1.1 + 1.2 + 1.3
						print(f"[{countblocklines}]	{showtime(section[0])}	{showuser}	{col_runas}	{col_cmd}")
						countblocklines+=1	
				
				#If line belong to any category
				if idx != lengthofcategories[-1]:
					
					#2.1. Print details of newly added users 
					if idx == lengthofcategories[0]:
						col_cmd=section[5][5:-1]
						
					#2.2. Print details of deleted users
					if idx == lengthofcategories[1]:
						col_cmd=section[5][1:-1]
						
					#2.3. Print details of changing passwords. 
					if idx == lengthofcategories[2]:
						col_cmd=section[7]
						
					#2.4. Print details of when users used the su command.
					if idx == lengthofcategories[3]:
						col_cmd=section[4][:-1]
					
					
					#2.5. Print details of users who used the sudo; include the command. 
					if idx == lengthofcategories[4]:
						cutatcmd=line.split("COMMAND=")	
						#if failed sudo 2.6. Print ALERT!
						if "not" in line.lower():
							col_cmd=(f"[ALERT! Failed sudo] {cutatcmd[1]}")
						#sucessful sudo
						else:
							col_cmd=cutatcmd[1]
						
					#2.6. Print ALERT! If users failed to use the sudo command; include the command
					if idx == lengthofcategories[5]:
						col_cmd=(f"[ALERT! Failed sudo] {cutatcmd[1]}")
					
					#1.1 + 1.2 + 1.3
					print(f"[{countblocklines}]	{showtime(section[0])}	{showuser}	{col_runas}	{col_cmd}")
					countblocklines+=1	

		#after looping through whole log once and filled one category, reset counter for next category
		countblocklines=1

#call main function
main_blocks()

print("""

~ End of Log Anaylser ~
""")
	
# End.