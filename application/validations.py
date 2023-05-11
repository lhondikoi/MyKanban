from flask import flash
from datetime import datetime
def val_str(string, min_length, max_length, emsg):
    if not string:
        flash(emsg)
        return False
    if min_length <= len(string) <= max_length:
        return string
    else:
        flash(emsg)
        return False

def val_date(datestring):
    if datestring == None or datestring == '':
        return None
    try:
        dt = datetime.strptime(datestring,'%Y-%m-%dT%H:%M')
    except:
        flash('Invalid datetime format')
        return False
    else:
        if datetime.now() >= dt:
            flash('Deadline cannot be before or equal to current time.')
            return False
        else:
            return dt