#!/usr/bin/env python3
"""
File: __init__.py
-----------------

A flask application that serves a personality quiz and allows users to compare
their similarity to others that have taken the quiz before.
"""
from flask import Flask, render_template
from .quiz_api.metadata import get_metadata

app = Flask(__name__)

@app.route('/')
def index():
    """
    Renders the home page with a list of quizzes.
    """
    quizzes = get_metadata()

    return render_template('index.html', quizzes=quizzes)