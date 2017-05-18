echo off
title HealthNet Initial Database Loader
echo WARNING: This will delete any existing HealthNet database!
set INPUT=
set /P INPUT=Do you wish to continue? (Y/N) %=%
if "%INPUT%"=="y" goto yes
if "%INPUT%"=="Y" goto yes
if "%INPUT%"=="n" goto no
if "%INPUT%"=="N" goto no

:yes
:: Delete any existing database(so it doesnt cause unique constraint errors)
echo Deleting old database...
del db.sqlite3
echo Creating new database...
python manage.py makemigrations
python manage.py migrate
echo Importing initial.csv...
echo                       *-----------------------------*
echo                       *    This will take about     *
echo                       *        15-20 seconds        *
echo                       *      Please be patient      *
echo                       *-----------------------------*
:: Calls a python script via manage.py
python manage.py shell < startup.py
echo Starting the server...
start "" http://localhost:8000
python manage.py runserver
pause

:no
echo Exiting startup...
pause