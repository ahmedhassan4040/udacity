import os
import unittest
import json
import sys
from flask_sqlalchemy import SQLAlchemy
from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        # self.database_path = "postgres://{}/{}".format(
        # 'localhost:5432', self.database_name)
        self.database_path = "postgres:///{}".format(self.database_name)
        setup_db(self.app, self.database_path)
        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    # Get Categories Test
    def test_get_categories(self):
        response = self.client().get('/categories')
        data = json.loads(response.data)
        # Check From Status Code
        self.assertEqual(response.status_code, 200)
        # Check From Reposne Is Succces Its Equal True
        self.assertEqual(data['is_success'], True)
        # Check From Another Data Must Be Found In The Reposnse
        self.assertTrue(data['categories'])

    # Get Qustions Test
    def test_get_questions(self):
        response = self.client().get('/questions')
        data = json.loads(response.data)
        # Check From Status Code
        self.assertEqual(response.status_code, 200)
        # Check From Reposne Is Succces Its Equal True
        self.assertEqual(data['is_success'], True)
        # Check From Another Data Must Be Found In The Reposnse
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])

    # Delete Qustion Test
    def test_delete_question(self):
        question = Question(question='new question', answer='new answer',
                            difficulty=1, category=1)
        question.insert()
        question_id = question.id

        response = self.client().delete(f'/questions/{question_id}')
        data = json.loads(response.data)

        # Check From Status Code
        self.assertEqual(response.status_code, 200)
        # Check From Reposne Is Succces Its Equal True
        self.assertEqual(data['is_success'], True)
        # Check From Another Data Must Be Found In The Reposnse
        self.assertTrue(data['deleted'])

    # Create Qustion Test
    def test_create_question(self):
        response = self.client().post(
            '/questions',
            json={
                'question':
                'Which four states make up the 4 Corners region of the US?',
                'answer': 'Colorado, New Mexico, Arizona, Utah',
                'difficulty': 3,
                'category': '3'
            })
        data = json.loads(response.data)
        # Check From Status Code
        self.assertEqual(response.status_code, 200)
        # Check From Reposne Is Succces Its Equal True
        self.assertEqual(data['is_success'], True)

    # Search Qustions Test

    def test_search_question(self):
        question = Question(question='new question', answer='new answer',
                            difficulty=1, category=1)
        question.insert()
        response = self.client().post('/questions/search',
                                      json={"search_term": "question"})
        data = json.loads(response.data)
        # Check From Status Code
        self.assertEqual(response.status_code, 200)
        # Check From Reposne Is Succces Its Equal True
        self.assertEqual(data['is_success'], True)
        # Check From Another Data Must Be Found In The Reposnse
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    # Get Qustions By Category Test
    def test_get_questions_by_category(self):
        question = Question(question='new question', answer='new answer',
                            difficulty=1, category=1)
        question.insert()
        
        response = self.client().get('/categories/1/questions')
        data = json.loads(response.data)
        # Check From Status Code
        self.assertEqual(response.status_code, 200)
        # Check From Reposne Is Succces Its Equal True
        self.assertEqual(data['is_success'], True)
        # Check From Another Data Must Be Found In The Reposnse
        self.assertTrue(data['questions'])


    # Get Quizzes Test
    def test_get_quizzes(self):
        response = self.client().post('/quizzes',
                                      json={
                                          'previous_questions': [],
                                          'quiz_category': {
                                              'type': 'Science',
                                              'id': 1
                                          }
                                      })
        data = json.loads(response.data)
        # Check From Status Code
        self.assertEqual(response.status_code, 200)
        # Check From Reposne Is Succces Its Equal True
        self.assertEqual(data['is_success'], True)
        # Check From Another Data Must Be Found In The Reposnse
        self.assertTrue(data['question'])

    # Error 404 Test
    def test_get_categories_error(self):
        response = self.client().get('/categoriesnotNotFound')
        data = json.loads(response.data)
        # Check From Status Code
        self.assertEqual(response.status_code, 404)
        # Check From Reposne Is Succces Its Equal Flase
        self.assertEqual(data['is_success'], False)
        # Check From Another Data Must Be Found In The Reposnse
        self.assertEqual(data['message'], 'Soory, Resources Is Not Found')

    # Error 422 Test
    def test_get_quizzes_error(self):
        response = self.client().post('/quizzes', json={})
        data = json.loads(response.data)
        # Check From Status Code
        self.assertEqual(response.status_code, 422)
        # Check From Reposne Is Succces Its Equal False
        self.assertEqual(data['is_success'], False)
        # Check From Another Data Must Be Found In The Reposnse
        self.assertEqual(data['message'], 'Soory, Some Error Has Been')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
