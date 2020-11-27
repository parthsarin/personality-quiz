"""
File: db.py
-----------

Handles interactions with the database.
"""
from flask import current_app
from unqlite import UnQLite
from typing import Dict
from datetime import datetime

DB_PATH = '{root}/results.db'


def connect():
    """
    Connects to the database and returns the database connection.
    """
    return UnQLite(DB_PATH.format(root=current_app.root_path))


def add_quiz_submission(slug: str, submission: Dict):
    """
    Adds the quiz submission to the database.
    """
    db = connect()

    submission['time'] = datetime.now().strftime(r"%b %d, %Y (%I:%M %p)")

    with db.transaction():
        submissions = db.collection(slug)
        submissions.create()
        submissions.store([submission])


def get_submissions_for(slug: str):
    """
    Returns all submissions to the specified form.
    """
    db = connect()

    with db.transaction():
        submissions = db.collection(slug)
        submissions = submissions.all()
    
    for submission in submissions:
        del submission['__id']
    
    return submissions
