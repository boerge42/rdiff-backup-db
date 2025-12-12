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
                lines.append(f"{key}:{spaces}{val} ({extra})")
            else:
                lines.append(f"{key}:{spaces}{val}")
        else:
            # Falls der Wert kein Dict ist
            lines.append(f"{key}: {value}")
    return "\n".join(lines)
