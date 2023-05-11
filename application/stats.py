from application.models import User, Board, List, Card
from application.database import db
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np
import os

IMG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static', 'img'))

def basic_stats(entity, entity_id):
    if entity == 'user':
        stats = {
            'boards': 0,
            'lists': 0,
            'cards': 0,
            'completed': [],
            'pending': [],
            'overdue': []
        }
        user = User.query.get(entity_id)
        if user:
            if user.boards != []:
                stats['boards'] = len(user.boards)
                for board in user.boards:
                    if board.lists != []:
                        stats['lists'] += len(board.lists)
                        for l in board.lists:
                            stats['cards'] += len(l.cards)
                            for card in l.cards:
                                if card.completed == True:
                                    stats['completed'].append(card)
                                elif card.deadline and datetime.now() > card.deadline:
                                            stats['overdue'].append(card)
                                else:
                                    stats['pending'].append(card)
    if entity == 'board':
        stats = {
            'lists': 0,
            'cards': 0,
            'completed': [],
            'pending': [],
            'overdue': []
        }
        board = Board.query.get(entity_id)
        if board:
            if board.lists != []:
                stats['lists'] += len(board.lists)
                for l in board.lists:
                    stats['cards'] += len(l.cards)
                    for card in l.cards:
                        if card.completed == True:
                            stats['completed'].append(card)
                        elif card.deadline and datetime.now() > card.deadline:
                                    stats['overdue'].append(card)
                        else:
                            stats['pending'].append(card)
    if entity == 'list':
        stats = {
            'cards': 0,
            'completed': [],
            'pending': [],
            'overdue': []
        }
        l = List.query.get(entity_id)
        if l:
            if l.cards != []:
                stats['cards'] += len(l.cards)
                for card in l.cards:
                    if card.completed == True:
                        stats['completed'].append(card)
                    elif card.deadline and datetime.now() > card.deadline:
                                stats['overdue'].append(card)
                    else:
                        stats['pending'].append(card)
    if len(stats['completed']) == 0 and len(stats['overdue']) == 0 and len(stats['pending']) == 0:
        pass
    else:
        l1 = ['completed', 'pending', 'overdue']
        l2 = [len(stats[x]) for x in l1]
        # create pie plot
        plt.clf()
        fig1, ax1 = plt.subplots()
        wedges, labels, nums = ax1.pie(
            l2,
            radius=1,
            startangle=60,
            wedgeprops=dict(width=0.5),
            colors=['#8EB897', '#4F6272', '#DD7596'],
            labels=l1,
            autopct='%1.1f%%'
            )
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        for label in labels:
            label.set_color('white')
        for num, wedge in zip(nums, wedges):
            ang = (wedge.theta1 + wedge.theta2) / 2
            x = wedge.r * 0.7 * np.cos(ang*np.pi/180)
            y = wedge.r * 0.7 * np.sin(ang*np.pi/180)
            num.set_position((x, y))
        fig1.set_facecolor('#393847')
        fig1.set_figwidth(4.2)
        fig1.set_figheight(3.8)
        print(IMG_DIR)
        plt.savefig(os.path.join(IMG_DIR, f'{entity}_{entity_id}_card_breakdown_chart.png'))
        plt.close('all')
    return stats

def make_timeline(entity, entity_id, card_list, start_date, numdays):
    date_list = [start_date + timedelta(days=x) for x in range(numdays)]
    y_dict = {}
    for d in date_list:
        y_dict[d] = 0
    for c in card_list:
        if c.completed_datetime.date() in y_dict:
            y_dict[c.completed_datetime.date()] += 1
    x_values, y_values = [], []
    for d, v in y_dict.items():
        x_values.append(d.strftime('%d'))
        y_values.append(v)
    # create graph
    plt.clf()
    fig, ax = plt.subplots()
    fig.set_facecolor('#393847')
    fig.set_figwidth(4.8)
    fig.set_figheight(3.5)
    ax.plot_date(x_values, y_values, linestyle='solid', color='yellow')
    ax.set_title(f"Cards completed per day ({date_list[0].strftime('%d %b')} - {date_list[-1].strftime('%d %b')})")
    ax.title.set_color('#fff')
    ax.xaxis.label.set_color('#fff')
    ax.yaxis.label.set_color('#fff')
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    # ax.set_ylim([0, max(y_values)])
    ax.tick_params(axis='x', which='both', labelrotation = 90, bottom=False)
    ax.tick_params(axis='y', which='both', left=False)
    ax.grid(visible=True, which='major', axis='y', color='#000', linewidth=0.5)
    ax.set_facecolor('#393847')
    # ax.spines['bottom'].set_color('white')
    # ax.spines['top'].set_color('white') 
    # ax.spines['right'].set_color('white')
    # ax.spines['left'].set_color('white')
    for key, spine in ax.spines.items():
        spine.set_visible(False)
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    plt.tight_layout()
    plt.savefig(os.path.join(IMG_DIR, f'{entity}_{entity_id}_timeline.png'))
    plt.close('all')
    return