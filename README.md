# HealthNet
Software Engineering Project. Software that manages hospitals’ day-to-day workflow.  
********************
Narhwal Software
HealthNet Release 2
Readme.txt
********************

---Team Members---
Grant Larsen
Ayana Adylova
Matt Gibson
Jonathan Foley


---Instructions for Running HealthNet---
1. Unzip the 'healthnet' folder to the location you want the site to be stored
2. Within the healthnet folder, run 'startup.bat'.
	a. This will delete all previous records in the database.
	b. The new contents are taken from 'initial.csv', which can be edited/replaced.
3. When startup.bat completes, it will open HealthNet in your default browser. 
4. On future uses, to start the web server without overwriting the database:
	a. Open a command line in the 'healthnet' folder.
	b. run 'python manage.py runserver'
	c. Leave the command window open.
	d. HealthNet can be accessed at '127.0.0.1:8000'.
5. To stop HealthNet, end startup.bat/the command line.


---Creating Django Admins---
Startup.bat does not create a Django Admin to go with HealthNet.
To do so, run 'python manage.py createsuperuser' from the command line
and provide the necessary information. Django Admins can log in at
'127.0.0.1:8000/admin' in order to do admin things.


---Known Bugs---
* Uploading a .csv that contains duplicate records, or similar
records to those in the current database, causes an IntegrityError.

* Patients may choose a hospital without any doctors/where all
doctors have a full patient list, and have no options in the
second page of registration.


---Login Information for Intial Users---
# 's vary depending on user type. They are all numbered 1-x.
All the passwords are pass1234
	Hospital Admins:	hadmin#@gmail.com
		Doctors:	doctor#@gmail.com
		 Nurses:	nurse#@gmail.com
		Patient:	patient#@gmail.com
