set mysqldump_path="C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe"

set mysql_user=root
set mysql_password=quang2015

set backup_path=D:\Backup
set backup_name=cinema_management_backup

if not exist "%backup_path%" mkdir "%backup_path%"

%mysqldump_path% --user=%mysql_user% --password=%mysql_password% cinema_management --default-character-set=utf8mb4 --routines --result-file="%backup_path%\%backup_name%.sql"
if %ERRORLEVEL% neq 0 (
    (echo Backup failed: error during dump creation) >> "%backup_path%\mysql_backup_log.txt"
) else (echo Backup successful) >> "%backup_path%\mysql_backup_log.txt"

pause