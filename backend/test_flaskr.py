import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from decouple import config

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = '{}://{}:{}@{}/{}' \
            .format(config('DB_DIALECT'), config('DB_USER'), config('DB_PASSWORD'), config('DB_ADDRESS'), self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        self.new_question = {
            'question': 'Is Shrodingers cat dead or alive',
            'answer': "It's in a constant state of dead and alive",
            'difficulty': 5,
            'category': 5,
        }

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful
    operation and for expected errors.
    """

    def test_get_categories(self):
        """Gets all categories."""
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['categories'])
        self.assertEqual(len(data['categories']), 6)

    def test_paginated_questions(self):
        """GETS all questions and return them with pagination."""
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

        self.assertTrue(data['questions'])
        self.assertTrue(data['totalQuestions'])
        self.assertTrue(data['categories'])
        self.assertIsNone(data['currentCategory'])

        self.assertGreaterEqual(len(data['questions']), 10)
        self.assertGreaterEqual(len(data['categories']), 6)
        self.assertGreaterEqual(data['totalQuestions'], 19)

        self.assertIsInstance(data['questions'], list)
        self.assertIsInstance(data['categories'], dict)
        self.assertEqual(data['questions'][0]['id'], 5)

    def test_404_if_page_does_not_exist(self):
        """Return Error Code 404 if page does not exist"""
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_question_based_on_category_id(self):
        """Fetch all Questions based on Category"""
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

        self.assertTrue(data['currentCategory'])
        self.assertEqual(data['currentCategory'], 'Science')

        self.assertEqual(data['totalQuestions'], 3)
        self.assertIsInstance(data['questions'], list)

    def test_404_if_category_questions_does_not_exist(self):
        """Return Error Code 404 if Fetch all Questions
        based on Category fails
        """
        res = self.client().get('/categories/1/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_delete_single_question(self):
        """Delete a single question"""
        question = Question(**self.new_question)
        question.insert()

        res = self.client().delete(f'/questions/{question.id}')

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_delete_single_question_fails(self):
        """Delete a single question fails"""
        res = self.client().delete('/questions/1500')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_add_question(self):
        """Test add a new question"""
        res = self.client().post('/questions', json=(self.new_question))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 201)
        self.assertTrue(data['success'])
        self.assertTrue(data['created'])

    def test_add_question_fails(self):
        """Test adding a new question fails"""
        res = self.client().post('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'bad request')

    def test_search(self):
        """Test search endpoint"""
        res = self.client().post('/questions/search', json=({
            'searchTerm': 'Shrodingers'
        }))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

        self.assertTrue(data['totalQuestions'])
        self.assertIsNone(data['currentCategory'])
        self.assertIsInstance(data['questions'], list)

    def test_search_fails_due_to_bad_request_body(self):
        """Test search endpoint fail due to bad request"""
        res = self.client().post('/questions/search')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'bad request')

    def test_play_quiz(self):
        """Test playing the trivia quiz"""
        res = self.client().post('/quizzes', json=({
            'quiz_category': {'type': 'custom type', 'id': '5'},
            'previous_questions': []
        }))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['question'])
        self.assertTrue(data['question']['question'])
        self.assertTrue(data['question']['answer'])
        self.assertTrue(data['question']['difficulty'])
        self.assertTrue(data['question']['category'])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
