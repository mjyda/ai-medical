@echo off
cd /d "%~dp0"
"C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe" -u root -p < mysql_init.sql
pause