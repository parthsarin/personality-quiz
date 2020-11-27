"""
File: __init__.py
-----------------

Handles the quiz endpoints.
"""
from flask import Blueprint, render_template, request, redirect, url_for
from .metadata import get_config, QuizCategories, meta_from_parser
from .db import add_quiz_submission, get_submission_for_form
from .process import all_results

quiz = Blueprint(__name__, 'quiz')

@quiz.route('/quiz/<slug>')
def get_quiz(slug: str):
    """
    Serves the quiz.
    """
    quiz = get_config(slug)
    
    if not quiz:
        return render_template("404.html"), 404

    # Metadata
    metadata = quiz[QuizCategories.META]
    metadata = meta_from_parser(metadata)

    # Remaining questions
    questions = quiz._sections
    del questions[QuizCategories.META]
    questions = zip(range(len(questions)), questions.keys(), questions.values())
    questions = list(questions)

    quiz_type = metadata[QuizCategories.QUESTION_TYPE]
    if quiz_type == QuizCategories.SLIDER:
        return render_template('slider-quiz.html', 
                               metadata=metadata, 
                               questions=questions)


@quiz.route('/result/<slug>/<int:record_id>', methods=['GET'])
def all_comparisons(slug: str, record_id: int):
    """
    Compares this submission to all other submissions for the form.
    """
    # Metadata
    quiz = get_config(slug)
    
    if not quiz:
        return render_template("404.html"), 404

    metadata = quiz[QuizCategories.META]
    metadata = meta_from_parser(metadata)

    # Results
    curr = get_submission_for_form(slug, record_id)
    
    if not curr:
        return render_template("404.html"), 404
    
    results = all_results(slug, record_id, expanded=False)

    return render_template(
        'all_results.html', 
        curr=curr, slug=slug, results=enumerate(results), metadata=metadata
    )


@quiz.route('/quiz/submit/<slug>', methods=['POST'])
def submit_quiz(slug: str):
    """
    Handles the quiz submission.
    """
    submission = dict(request.form)
    for k, v in submission.items():
        # Convert the slider answers to integers
        if not k == 'name':
            try:
                submission[k] = int(v)
            except ValueError:
                pass
    
    # Write to the database
    submission_id = add_quiz_submission(slug, submission)

    # Redirect to the results
    return redirect(
        url_for('personality-quiz.quiz_api.all_comparisons',
                slug=slug, record_id=submission_id)
    )
