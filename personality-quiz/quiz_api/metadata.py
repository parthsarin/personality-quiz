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
    QUESTION_TYPE = 'question_type'
    SLIDER = 'slider'
    MULTIPLE_CHOICE = 'mc'


class QuizMetadata(TypedDict):
    name: str
    description: str
    author: str
    date: Union[datetime, None]
    img: Union[str, None]
    slug: str
    question_type: Union[QuizCategories.SLIDER, QuizCategories.MULTIPLE_CHOICE]


def meta_from_parser(parser: configparser.ConfigParser) -> QuizMetadata:
    """
    Extracts the QuizMetadata fields from the configparser.
    """
    metadata: QuizMetadata = {
        'name': parser.get('name'),
        'description': parser.get('description'),
        'author': parser.get('author'),
        'date': parser.get('date'),
        'img': parser.get('img'),
        'slug': parser.get('slug'),
        'question_type': parser.get('question_type')
    }

    return metadata


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
        
        if not all_meta.getboolean('enabled', True):
            continue

        output.append(meta_from_parser(all_meta))
        parser.clear()
    
    return output


def get_config(slug: str) -> Union[configparser.ConfigParser, None]:
    """
    Returns the config given the quiz slug or None if the slug isn't found.
    """
    quizzes = glob(path.join(current_app.root_path, "quizzes/*.conf"))
    parser = configparser.ConfigParser()

    for quiz in quizzes:
        parser.read(quiz)

        try:
            all_meta = parser[QuizCategories.META]
        except KeyError:
            # Not correctly formatted
            continue

        if not all_meta.getboolean('enabled', True):
            continue
        
        quiz_slug = all_meta.get('slug')
        if slug == quiz_slug:
            return parser # (filled out with the information for the quiz)
        
        parser.clear()
