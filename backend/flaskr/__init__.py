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
        """Retrieve All available categories"""

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
        """Fetch all the questions belonging to a specific category"""
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

    @app.route('/questions/search', methods=['POST'])
    def search():
        """Search for questions with the search term"""
        body = request.get_json()

        searchTerm = body.get('searchTerm', None)

        if not searchTerm: abort(400)

        try:
            qs = Question.query.filter(Question.question.ilike(f'%{searchTerm}%'))

            return jsonify({
                'success': True,
                'questions': [data.format() for data in qs],
                'totalQuestions': qs.count(),
                'currentCategory': None
            })
        except:
            abort(422)

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

    @app.route('/quizzes', methods=['POST'])
    def quizzes():
        """Playing the trivia quiz:
        Questions are generated randomly and can be based on categories.
        Question are also checked against a list of previous questions to avoid
        duplicate questions
        """
        body = request.get_json()

        quiz_category = body.get('quiz_category', None)
        previous_questions = body.get('previous_questions', None)

        if previous_questions is None: abort(400)

        try:
            qs = Question.query.filter(Question.id.notin_(previous_questions))
            question = None

            if quiz_category:
                qs = qs.filter(Question.category == quiz_category['id'])

            if qs.count():
                question = qs[random.randint(0, qs.count() - 1)]
                question = question.format()

            return jsonify({
                'success': True,
                'question': question
            })
        except:
            abort(500)

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

