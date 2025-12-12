# *********************************************************************************************
#
#  web_rdiff-backup.py
# -----------------
#  Uwe Berger; 2025
#
# web.py - main
#
# Web-Frontend zur rdiff-backup-DB.
# (Zugriffsparameter zur DB sind in model.py zu finden und auch dort anzupassen.)
#
#
# ---------
# Have fun!
#
# *********************************************************************************************

import web
import model
import utils

from web.template import ALLOWED_AST_NODES
ALLOWED_AST_NODES.append('Constant')

# define url mappings
urls = (
        "/", "Index",
        "/backupdetail/", "Detail",
        "/backuplist/", "List",
    )

web.config.debug = False

# define Templates
render = web.template.render("templates", base="base")

app = web.application(urls, globals())

#session = web.session.Session(app, web.session.DiskStore('sessions'))

# ********************************
MAX_ROWS_ON_PAGE   = 20       # maximale Anzahl Zeilen pro Seite (backuplist.html)
DAYS_TO_OLD_BACKUP = 7        # Anzahl Tage, ab dem ein Backup als veraltet markiert wird (index.html)

# ***************************************************************
# Startseite mit jeweils letztem Backup in DB als Tabelle
class Index:

	# ****************************
    def GET(self):
        diff_to_old = DAYS_TO_OLD_BACKUP*24*60*60
        to_old_ts = utils.get_to_old_unixtimestamp(diff_to_old)
        backups = model.get_all_last_backups(to_old_ts)
        return render.index(backups)

# ***************************************************************
# Liste aller Backups zu Backup-Computer/-Dir als Tabelle
class List:

	# ****************************
    def GET(self):
        i = web.input(backup_computer=None, backup_dir=None, prev_offset=None, next_offset=None)
        # Offset für Blätter ermitteln
        # ...Anzahl Zeilen pro Seite
        limit = MAX_ROWS_ON_PAGE
        # ...Anzahl Zeilen in DB
        count = model.get_count_backups(i.backup_computer, i.backup_dir)
        if i.prev_offset is not None:
            offset = int(i.prev_offset)
        elif i.next_offset is not None:
            offset = int(i.next_offset)
        else:
            offset = 0
        prev_offset = offset - limit
        if prev_offset < 0:
            prev_offset = None
        next_offset = offset + limit
        if next_offset >= count:
            next_offset = None
        last_offset = int(count/limit) * limit
        # ...und damit Tabelle lesen
        backups = model.get_backups(i.backup_computer, i.backup_dir, offset, limit)
        # Start-/Ende-Zeitpunkt in lesbare Form bringen
        for idx in range(0, len(backups)):
            if backups[idx]['StartTime'] is not None:
                backups[idx]['StartTime'] = utils.unixtime2datetime(backups[idx]['StartTime']) 
            if backups[idx]['EndTime'] is not None:
                backups[idx]['EndTime'] = utils.unixtime2datetime(backups[idx]['EndTime']) 
        return render.backuplist(i.backup_computer, i.backup_dir, backups, prev_offset, next_offset, last_offset)

# ***************************************************************
# detailierte Statistic zu einem Backup
class Detail:

	# ****************************
    def GET(self):
        i = web.input(backup_computer=None, backup_dir=None, backup_completed=None)
        backup = model.get_backup(i.backup_computer, i.backup_dir, i.backup_completed)
        txt_statistic = utils.json_to_string(backup.statistic)
        txt_statistic = f"<code>{txt_statistic}</code>"
        return render.backupdetails(i.backup_computer, i.backup_dir, i.backup_completed, txt_statistic)

# ***************************************************************
# ***************************************************************
# ***************************************************************
if __name__ == "__main__":
    app.run()
