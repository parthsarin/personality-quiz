"""
File: metadata.py
-----------------

Exports functions that retrieve metadata about the loaded quizzes.
"""
import configparser
from datetime import datetime
from flask import current_app
from typing import TypedDict, List, Union
from glob import glob
from os import path
import enum


class QuizCategories:
    META = 'META'
    SLIDER = 'slider'
    MULTIPLE_CHOICE = 'mc'


class QuizMetadata(TypedDict):
    name: str
    description: str
    author: str
    date: Union[datetime, None]
    img: Union[str, None]
    slug: str


def get_metadata() -> List[QuizMetadata]:
    """
    Returns a list of metadata for all of the currently enabled quizzes.
    """
    quizzes = glob(path.join(current_app.root_path, "quizzes/*.conf"))
    output = []
    parser = configparser.ConfigParser()

    for quiz in quizzes:
        parser.read(quiz)

        try:
            all_meta = parser[QuizCategories.META]
        except KeyError:
            # Not correctly formatted
            continue
        
        metadata: QuizMetadata = {
            'name': all_meta.get('name'),
            'description': all_meta.get('description'),
            'author': all_meta.get('author'),
            'date': all_meta.get('date'),
            'img': all_meta.get('img'),
            'slug': all_meta.get('slug'),
        }

        output.append(metadata)
        parser.clear()
    
    return output
