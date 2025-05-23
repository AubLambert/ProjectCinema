cd "C:\Program Files\MySQL\MySQL Server 8.0\bin"

set mysql_user=admin
set mysql_password=quang123

set backup_path=D:\Backup
set backup_name=cinema_management_backup

mysqldump --user=%mysql_user% --password=%mysql_password% cinema_management --default-character-set=utf8mb4 --routines --result-file="%backup_path%\%backup_name%.sql"
if %ERRORLEVEL% neq 0 (
    (echo Backup failed: error during dump creation) >> "%backup_path%\mysql_backup_log.txt"
) else (echo Backup successful) >> "%backup_path%\mysql_backup_log.txt"