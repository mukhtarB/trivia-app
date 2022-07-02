import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
        return response


    def pagination(request, selection):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        page_data = [data.format() for data in selection]
        current_page = page_data[start:end]
        return current_page


    @app.route('/categories', methods=['GET'])
    def categories():
        """
        @TODO:
        Create an endpoint to handle GET requests
        for all available categories.
        """

        all_categories = Category.query.all()

        if len(all_categories) == 0: abort(404)
        
        formatted_catgegory = \
        {category.format()['id'] : category.format()['type'] for category in all_categories}

        return jsonify({
            'categories': formatted_catgegory
        })

    @app.route('/questions', methods=['GET'])
    def questions():
        """
        GET: Paginated Questtions
        This endpoint should return a list of questions paginated every
        10 questions, number of total questions, current category, categories.
        """

        all_questions = Question.query.all()

        current_page = pagination(request, all_questions)

        if len(current_page) == 0: abort(404)

        all_categories = Category.query.all()

        return jsonify({
            'success': True,
            'questions': current_page,
            'totalQuestions': len(all_questions),
            'categories': {category.id: category.type for category in all_categories},
            'currentCategory': None
        })
    

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def categories_questions(category_id):
        """Fetch all the questions belonging to a specific category
        """
        questions = Question.query.filter(Question.category == category_id)
        current_page = pagination(request, questions)

        if len(current_page) == 0: abort(404)

        current_Category = Category.query.filter(Category.id == category_id).one_or_none()

        return jsonify({
            'success': True,
            'questions': current_page,
            'totalQuestions': questions.count(),
            'currentCategory': current_Category.format()['type']
        })


    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        """Delete a question from db and ensure it persists"""
        question = Question.query.filter(Question.id == question_id).one_or_none()

        if not question: abort(404)

        try:
            question.delete()

            return jsonify({
                'success': True,
                'deleted': question_id
            })
        except:
            abort(422)

    @app.route('/questions', methods=['POST'])
    def add_question():
        """Populate the Question table with a new question"""

        body = request.get_json()

        question = body.get('question', None)
        answer = body.get('answer', None)
        difficulty = body.get('difficulty', None)
        category = body.get('category', None)

        if not (question and answer and difficulty and category): abort(400)

        try:
            q = Question(
                question=question,
                answer=answer,
                difficulty=difficulty,
                category=category
            )

            q.insert()

            return jsonify({
                'success': True,
                'created': q.id
            }), 201

        except:
            abort(422)
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(400)
    def bad_request(error):
        return (
            jsonify({
                'success': False,
                'error': 400,
                'message': 'bad request',
            }),
            400
        )

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({
                'success': False,
                'error': 404,
                'message': 'resource not found',
            }),
            404
        )

    @app.errorhandler(405)
    def not_allowed(error):
        return (
            jsonify({
                'success': False,
                'error': 405,
                'message': 'method not allowed',
            }),
            405
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({
                'success': False,
                'error': 422,
                'message': 'unprocessable',
            }),
            422
        )

    @app.errorhandler(500)
    def internal_server_error(error):
        return (
            jsonify({
                'success': False,
                'error': 500,
                'message': 'internal server error',
            }),
            500
        )

    return app

