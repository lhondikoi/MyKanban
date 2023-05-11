from flask import redirect, url_for, flash, send_file, current_app as app
from application.models import User, Board, List, Card
from application.database import db
from application.validations import val_str, val_date
from datetime import date
import os, csv
from zipfile import ZipFile, ZIP_DEFLATED

REPORTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'reports'))

def generate_report(list_obj):
    try:
        data = [['Sl.no', 'Created on', 'Last Updated on', 'Title', 'Description', 'Deadline', 'Completed', 'Completed on']]
        uname, bname, lname = list_obj.board.user.user_name, list_obj.board.board_name, list_obj.list_name
        for index, card in enumerate(list_obj.cards):
            last_updated = '-' if card.updated is None else card.updated
            content = '-' if card.content is None else card.content
            deadline = '-' if card.deadline is None else card.deadline
            completed = 'yes' if card.completed is True else 'no'
            completed_on = card.completed_datetime if card.completed_datetime is not None else '-'
            row = [
                    index+1,
                    card.created,
                    last_updated,
                    card.title,
                    content,
                    deadline,
                    completed,
                    completed_on
                ]
            data.append(row)
        FILE_NAME = f"EXPORT-{date.today()}-{'-'.join(uname.split(' '))}-{'-'.join(bname.split(' '))}-{'-'.join(lname.split(' '))}.csv"
        FILE_URI = os.path.join(REPORTS_DIR, FILE_NAME)
        with open(FILE_URI, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for row in data:
                writer.writerow(row)
    except:
        return False
    else:
        return True, FILE_URI, FILE_NAME

# export list
@app.route('/export/<string:entity>/<int:entity_id>')
def export(entity, entity_id):
    if entity == 'list':
        l = List.query.get_or_404(entity_id)
        report = generate_report(l)
        if report[0]:
            return send_file(report[1], as_attachment=True) #download
        else:
            flash('There was an error generating your report.')
            return redirect(url_for('dashboard_lists', board_id=l.board.board_id))
    
    if entity == 'board':
        # getting board
        board = Board.query.get(entity_id)

        # generating reports for every list in the board and getting their URIs
        reports = []
        for l in board.lists:
            report = generate_report(l)
            if report[0]:
                reports.append((report[1],  report[2]))
        
        # if atleast one report was generated, initiate zipping process
        if reports != []:
            
            # set the zip filename and its URI
            ZIP_FILE_NAME = f"EXPORT-{date.today()}-{'-'.join(board.board_name.split(' '))}.zip"
            ZIP_FILE_URI = os.path.join(REPORTS_DIR, ZIP_FILE_NAME)
            
            # create the zipfile and write the reports into the zip file
            with ZipFile(ZIP_FILE_URI, 'w') as zf:
                for report in reports:
                    zf.write(report[0], report[1], compress_type=ZIP_DEFLATED)
            
            # download
            return send_file(ZIP_FILE_URI, as_attachment=True)
        else:
            return redirect(url_for('boards'))