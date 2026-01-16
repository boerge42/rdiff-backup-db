# *********************************************************************************************
#
#    utils.py
# ----------------
# Uwe Berger; 2025
#
# Helfer für web_rdiff_backup 
#
# ---------
# Have fun!
#
# *********************************************************************************************

import json
from datetime import datetime

hover_texts = [
    {"keys": ["StartTime", "EndTime", "ElapsedTime"],
     "text": ("StartTime and EndTime are measured in seconds since the epoch. ElapsedTime is just "
              "EndTime - StartTime, the length of the rdiff-backup session.")},

    {"keys": ["SourceFiles", "SourceFileSize", "MirrorFiles", "MirrorFileSize"],
     "text": ("SourceFiles are the number of files found in the source directory, and SourceFileSize "
              "is the total size of those files. MirrorFiles are the number of files found in the "
              "mirror directory (not including the rdiff-backup-data directory) and MirrorFileSize is "
              "the total size of those files. All sizes are in bytes. If the source directory hasn’t "
              "changed since the last backup, MirrorFiles == SourceFiles and SourceFileSize == MirrorFileSize.")},

    {"keys": ["NewFiles", "NewFileSize"],
     "text": ("NewFiles and NewFileSize are the total number and size of the files found in the source "
              "directory but not in the mirror directory. They are new as of the last backup.")},

    {"keys": ["DeletedFiles", "DeletedFileSize"],
     "text": ("DeletedFiles and DeletedFileSize are the total number and size of the files found "
              "in the mirror directory but not the source directory. They have been deleted since the "
              "last backup.")},

    {"keys": ["ChangedFiles", "ChangedSourceSize", "ChangedMirrorSize"],
     "text": ("ChangedFiles are the number of files that exist both on the mirror and on the source "
              "directories and have changed since the previous backup. ChangedSourceSize is their "
              "total size on the source directory, and ChangedMirrorSize is their total size on the "
              "mirror directory.")},
     
    {"keys": ["IncrementFiles", "IncrementFileSize"],
     "text": ("IncrementFiles is the number of increment files written to the rdiff-backup-data "
              "directory, and IncrementFileSize is their total size. Generally one increment file "
              "will be written for every new, deleted, and changed file.")},
     
    {"keys": ["TotalDestinationSizeChange"],
     "text": ("TotalDestinationSizeChange is the number of bytes the destination directory as a "
              "whole (mirror portion and rdiff-backup-data directory) has grown during the given "
              "rdiff-backup session. This is usually close to IncrementFileSize + NewFileSize - "
              "DeletedFileSize + ChangedSourceSize - ChangedMirrorSize, but it also includes the "
              "space taken up by the hardlink_data file to record hard links.")},
     
]

# ***********************************************************************
def get_hover_text(key):
    ret = ""
    for hover_text in hover_texts:
        if key in hover_text["keys"]:
            ret = f'<span title="{hover_text["text"]}">{key}</span>'
            break
    if len(ret) == 0:
        ret = key
    return ret	

# ***********************************************************************
def get_to_old_unixtimestamp(diff_from_now_in_sec):
    return (int(datetime.now().timestamp()) - diff_from_now_in_sec)

# ***********************************************************************
def unixtime2datetime(unixtime):
    dt = datetime.fromtimestamp(float(unixtime))
    return dt.strftime("%Y-%m-%d %H:%M:%S")

# ***********************************************************************
def json_to_string(json_string):
    value_begin = 27
    data = json.loads(json_string)
    lines = []
    for key, value in data.items():
        if isinstance(value, dict):
            val = value.get("value", "")
            extra = value.get("extra")
            spaces = " " * (value_begin - len(key))
            if extra is not None:
                lines.append(f'<div class="hover-line">{get_hover_text(key)}:{spaces}{val} ({extra})</div>')
            else:
                lines.append(f'<div class="hover-line">{get_hover_text(key)}:{spaces}{val}</div>')
        else:
            # Falls der Wert kein Dict ist
            lines.append(f"{key}: {value}")
    return "\n".join(lines)
