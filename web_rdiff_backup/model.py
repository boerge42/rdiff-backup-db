# *********************************************************************************************
#
#    model.py
# ----------------
# Uwe Berger; 2025
#
# Datenbankzugriffe für web_rdiff_backup
#
# ---------
# Have fun!
#
# *********************************************************************************************

import web

# welche DB wird benutzt (sqlite|mariadb|mysql)
db_type = "sqlite"
# entsprechende DB öffnen
if db_type == "sqlite":
    db = web.database(dbn="sqlite", db="rdiff_backup.db")
    sql_json_cmd = "json_extract"
elif db_type in ["mariadb", "mysql"]:
    db = web.database(dbn="mysql", host="nanotuxedo", db="drive_control", user="xxxx", pw="yyyy")
    sql_json_cmd = "json_value"
elif True:
    db = web.database(dbn="sqlite", db="rdiff_backup.db")
    sql_json_cmd = "json_extract"

# ***********************************************************************
def get_all_last_backups(ts_old):
    sql = f"""
        SELECT backup_computer,
            backup_dir,
            backup_completed,
            {sql_json_cmd}(backup_statistic, '$.ElapsedTime.extra') as ElapsedTime,
            {sql_json_cmd}(backup_statistic, '$.TotalDestinationSizeChange.extra') as TotalDestinationSizeChange,
            {sql_json_cmd}(backup_statistic, '$.Errors.value') as Errors,
            case
                when {sql_json_cmd}(backup_statistic, '$.StartTime.value') < {ts_old}
                then "x"
                else " "
            end as to_old
        FROM (
            SELECT *,
                ROW_NUMBER() OVER (
                    PARTITION BY backup_computer, backup_dir
                    ORDER BY backup_completed DESC
                ) AS rn
            FROM rdiff_backup
        ) t
        WHERE rn = 1;
            """
    return list(db.query(sql))

# ***********************************************************************
def get_backups(backup_computer, backup_dir, offset, limit):
    sql = f"""
            select
                backup_completed,
                {sql_json_cmd}(backup_statistic, '$.StartTime.value') as StartTime,
                {sql_json_cmd}(backup_statistic, '$.EndTime.value') as EndTime,
                {sql_json_cmd}(backup_statistic, '$.ElapsedTime.extra') as ElapsedTime,
                {sql_json_cmd}(backup_statistic, '$.TotalDestinationSizeChange.extra') as TotalDestinationSizeChange,
                {sql_json_cmd}(backup_statistic, '$.Errors.value') as Errors
            from rdiff_backup
            where
                backup_computer = '{backup_computer}' and
                backup_dir = '{backup_dir}'
            order by backup_completed desc
            limit {limit} offset {offset}
            """
    return list(db.query(sql))

# ***********************************************************************
def get_count_backups(backup_computer, backup_dir):
    sql = f"""
            select
                count(*) as count
            from rdiff_backup
            where
                backup_computer = '{backup_computer}' and
                backup_dir = '{backup_dir}'
            """
    rows = list(db.query(sql))
    return rows[0]["count"]

# ***********************************************************************
def get_backup(backup_computer, backup_dir, backup_completed):
    sql = f"""
            select
                backup_statistic as statistic
            from rdiff_backup
            where
                backup_computer = '{backup_computer}' and
                backup_dir = '{backup_dir}' and
                backup_completed = '{backup_completed}'
            """
    rows = list(db.query(sql))
    return rows[0]
