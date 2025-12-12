# **********************************************************************
#    rdiff_backup.py
#  -------------------
#   Uwe Berger, 2025
#
# Einlesen der Statistikdateien von rdiff-backup und Einfügen in eine
# Datenbank als JSON
#
#
# Inhalt Statistikdatei: 
# ------
# StartTime 1764756062.00 (Wed Dec  3 11:01:02 2025)
# EndTime 1764756063.75 (Wed Dec  3 11:01:03 2025)
# ElapsedTime 1.75 (1.75 seconds)
# SourceFiles 58
# SourceFileSize 55352 (54.1 KB)
# MirrorFiles 58
# MirrorFileSize 55352 (54.1 KB)
# NewFiles 0
# NewFileSize 0 (0 bytes)
# DeletedFiles 0
# DeletedFileSize 0 (0 bytes)
# ChangedFiles 3
# ChangedSourceSize 0 (0 bytes)
# ChangedMirrorSize 0 (0 bytes)
# IncrementFiles 3
# IncrementFileSize 0 (0 bytes)
# TotalDestinationSizeChange 0 (0 bytes)
# Errors 0
# -----
#
#
# Als Script-Parameter muss das Backup-Verzeichnis angegeben werden
#
#
# ---------
# Have fun!
#
# **********************************************************************
import glob
import platform
import os
import sys
import json
from datetime import datetime


# **********************************************************************
# backup-dir wird via Kommandozeilenparameter angegeben!
if len(sys.argv) == 2:
    backup_dir = sys.argv[1]
else:
    print("Backup-Dir muss beim Scriptaufruf als Parameter angegeben werden!")
    exit(1)
# Pattern
file_pattern = "session_statistic*"
pattern = f"{backup_dir}/rdiff-backup-data/{file_pattern}"


# **********************************************************************
# alle oder nur jüngste Statistikdatei(en) aus Backup-Dir einlesen
# --> all|latest
mode="all"


# **********************************************************************
# je nach DB-Type entsp. Modul einbinden und DB-Connection öffnen
# --> sqlite|mariadb|
db_type = "sqlite"
if db_type == "mariadb":
    import sqlite3
    connect_data = "rdiff_backup.db"
    conn = sqlite3.connect(connect_data)
    sql_replace = "insert or replace"
elif db_type == "mariadb":
    import mysql.connector
    conn = mysql.connector.connect(
                    host='nanotuxedo',
                    user='xxxx',
                    password='yyyy',
                    database='drive_control',
                    connection_timeout=10
                )
    sql_replace = "replace"
else:
    print("Kein sinnvoller DB-Typ angegeben!")
    exit(1)



# **********************************************************************
def convert_log2json(log):
    data = {}
    for line in log.splitlines():
        parts = line.split(maxsplit=2)
        key = parts[0]
        value = parts[1]
        extra = parts[2] if len(parts) > 2 else None
        # numerische Werte in INT|Float konvertieren
        try:
            if "." in value:
                value = float(value)
            else:
                value = int(value)
        except ValueError:
            pass
        # json zusammenbauen
        if extra:
            data[key] = {"value": value, "extra": extra.strip("()")}
        else:
            #data[key] = value
            data[key] = {"value": value}
    return json.dumps(data, indent=2)


# **********************************************************************
def get_latest_log(pattern):
    # alle Dateien zu Pattern
    file_found = False
    files = glob.glob(pattern)
    if not files:
        pass
    else:
        # jüngste Datei anhand des Änderungszeitpunkts
        file_found = True
        latest_file = max(files, key=os.path.getmtime)
        # mtime der Log-Datei ist Ende des Backups
        mtime = os.path.getmtime(latest_file)
        # Datei einlesen
        with open(latest_file, "r", encoding="utf-8") as f:
            content = f.read()
    return file_found, mtime, content


# **********************************************************************
def db_table_create():
    cursor = conn.cursor()
    # eventuell Tabellen anlegen
    sql =  """
        create table if not exists rdiff_backup (
            backup_computer varchar(100) not null,
            backup_dir varchar(500) not null,
            backup_completed datetime default 0,
            backup_statistic json,
            primary key (backup_computer, backup_dir, backup_completed)
        )
    """
    cursor.execute(sql)


# **********************************************************************
def db_insert(backup_computer, backup_dir, backup_completed, backup_statistic):
    cursor = conn.cursor()
    # insert
    backup_completed_str = datetime.fromtimestamp(backup_completed).strftime("%Y-%m-%d %H:%M:%S")
    sql = f"{sql_replace} into rdiff_backup values ('{backup_computer}', '{backup_dir}', '{backup_completed_str}', '{backup_statistic}')"
    cursor.execute(sql)


# **********************************************************************
# **********************************************************************
# **********************************************************************

computer = platform.node()
db_table_create()

if mode == "latest":
    # jüngste Datei zu Pattern
    file_found, mtime, content = get_latest_log(pattern)
    if file_found:
        json_str = convert_log2json(content)
        db_insert(computer, backup_dir, mtime, json_str)
    else:
        print("Zu Backup-Dir und Pattern keine passenden Dateien gefunden!")
elif mode == "all":
    # alle Dateien zu Pattern
    files = glob.glob(pattern)
    if not files:
        print("Zu Backup-Dir und Pattern keine passenden Dateien gefunden!")
    else:
        for file in files:
            # mtime der Log-Datei ist Ende des Backups
            mtime = os.path.getmtime(file)
            # Datei einlesen
            with open(file, "r", encoding="utf-8") as f:
                content = f.read()
            json_str = convert_log2json(content)
            db_insert(computer, backup_dir, mtime, json_str)


# DB commit/schliessen
conn.commit()
conn.close()
