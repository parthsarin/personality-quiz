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


def add_quiz_submission(slug: str, submission: Dict) -> int:
    """
    Adds the quiz submission to the database.

    Returns
    -------
    The id of the added submission
    """
    db = connect()

    submission['time'] = datetime.now().strftime(r"%b %d, %Y (%I:%M %p)")

    with db.transaction():
        submissions = db.collection(slug)
        submissions.create()
        output = submissions.store([submission], return_id=True)
    
    return output


def get_submissions_for_form(slug: str):
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


def get_submission_for_form(slug: str, record_id: int):
    """
    Returns the specified submission for the form or None if the record doesn't
    exist.
    """
    db = connect()

    with db.transaction():
        submissions = db.collection(slug)
        output = submissions.fetch(record_id)
    
    if output:
        del output['__id']
    
    return output


def get_num_submissions(slug: str) -> int:
    """
    Returns the number of submissions to a form.
    """
    db = connect()

    with db.transaction():
        submissions = db.collection(slug)
        
        if not submissions.exists():
            return None
        
        last_id = submissions.last_record_id()
    
    return last_id + 1