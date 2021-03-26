import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import random
import json
import sys

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
  @TODO: Set up CORS. Allow '*' for origins.
   Delete the sample route after completing the TODOs
  '''
    cros = CORS(app, resources={r"/api/*": {"origins": "*"}})
    '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Headers", "*")
        response.headers.add("Access-Control-Allow-Methods", "*")
        return response
    '''
  @TODO:
  Create an endpoint to handle GET requests
  for all available categories.
  '''
    @app.route('/categories')
    @cross_origin()
    def get_categories():
        try:
            all_categories = [category.format()
                              for category in
                              Category.query.order_by('id').all()]
            if len(all_categories) == 0:
                abort(404)
            return jsonify({
                "is_success": True,
                "message": "Successfully Loaded\
                {} Category".format(len(all_categories)),
                "categories": all_categories
            })
        except:
            print(sys.exc_info())
            abort(422)

    '''
  @TODO:
  Create an endpoint to handle GET requests for questions,
  including pagination (every 10 questions).
  This endpoint should return a list of questions,
  number of total questions, current category, categories.
  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom 
  of the screen for three pages.
  Clicking on the page numbers should update the questions.
  '''
    @app.route('/questions')
    @cross_origin()
    def get_questions():
        try:
            page_number = request.args.get('page', 1, type=int)
            end = page_number * 10
            start = end - 10
            # Select All Questions
            all_questions = Question.query.order_by('id').all()
            all_total_questions = len(all_questions)
            if all_total_questions == 0:
                abort(404)
            # Select Page Questions
            page_questions = [question.format()
                              for question in all_questions[start:end]]
            page_total_questions = len(page_questions)
            if page_total_questions == 0:
                abort(404)
            return jsonify({
                "is_success": True,
                "message": "Successfully Loaded\
                     {} Question".format(page_total_questions),
                "total_questions": all_total_questions,
                "questions": page_questions,
                "categories": [category.format() for category
                               in Category.query.order_by('id').all()],
                "current_category": None
            })
        except:
            abort(422)

    '''
  @TODO:
  Create an endpoint to DELETE question using a question ID.

  TEST: When you click the trash icon next to
   a question, the question will be removed.
  This removal will persist in the database 
  and when you refresh the page.
    '''
    @app.route('/questions/<int:questionid>', methods=['DELETE'])
    @cross_origin()
    def delete_questions(questionid):
        try:
            question_target = Question.query.filter_by(
                id=questionid).one_or_none()
            if question_target is None:
                abort(404)
            question_target.delete()
            return jsonify({
                "is_success": True,
                "message": "Deleted Successfully",
                'deleted': questionid
            })
        except:
            print(sys.exc_info())
            abort(422)
    '''
  @TODO:
  Create an endpoint to POST a new question,
  which will require the question and answer text,
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab,
  the form will clear and the question will
   appear at the end of the last page
  of the questions list in the "List" tab.
  '''
    @app.route('/questions', methods=['POST'])
    @cross_origin()
    def add_questions():
        try:
            body = request.get_json()
            new_question = Question(question=body.get('question'), answer=body.get(
                'answer'), difficulty=body.get('difficulty'), category=str(body.get('category')))
            new_question.insert()
            return jsonify({
                "is_success": True,
                "message": "Successfully Added",
            })
        except:
            abort(422)

    '''
  @TODO:
  Create a POST endpoint to get questions based on a search term.
  It should return any questions for whom the search term
  is a substring of the question.

  TEST: Search by any phrase. The questions
   list will update to include
  only question that include that string 
  within their question.
  Try using the word "title" to start.
  '''
    @app.route('/questions/search', methods=['POST'])
    @cross_origin()
    def get_questions_by_search():
        try:
            search_term = request.get_json().get('search_term')
            if search_term is None:
                abort(404)
            all_questions = [question.format() for question in Question.query.filter(
                Question.question.ilike('%{}%'.format(search_term))).order_by('id').all()]
            total_questions = len(all_questions)
            if total_questions == 0:
                abort(404)
            return jsonify({
                "is_success": True,
                "message": "Successfully Loaded {} Question".format(total_questions),
                "questions": all_questions,
                "total_questions": total_questions,
                "current_category": None
            })
        except:
            abort(422)
    '''
  @TODO:
  Create a GET endpoint to get questions based on category.

  TEST: In the "List" tab / main screen,
   clicking on one of the
  categories in the left column will 
  cause only questions of that
  category to be shown.
  '''
    @app.route('/categories/<string:categoryid>/questions')
    def get_questions_by_category(categoryid):
        try:
            all_questions = [question.format() for question in Question.query.filter_by(
                category=categoryid).order_by('id').all()]
            total_questions = len(all_questions)
            if total_questions == 0:
                abort(404)
            return jsonify({
                "is_success": True,
                "message": "Successfully Loaded {} Question".format(total_questions),
                "questions": all_questions,
            })
        except:
            abort(422)

    '''
  @TODO:
  Create a POST endpoint to get questions to play the quiz.
  This endpoint should take category 
  and previous question parameters
  and return a random questions within the given category,
  if provided, and that is not one of the previous questions.

  TEST: In the "Play" tab, after a user
   selects "All" or a category,
  one question at a time is displayed, 
  the user is allowed to answer
  and shown whether they were correct or not.
  {'previous_questions': [], 'quiz_category': {'type':  'Science', 'id': 1}}
  '''
    @app.route('/quizzes', methods=['POST'])
    @cross_origin()
    def get_quizzes():
        try:
            body = request.get_json()
            print(body)
            # Get Privious Questions
            previous_questions = body.get('previous_questions', None)
            if previous_questions is None:
                abort(404)

            # Get Target Categoey
            target_category = body.get('quiz_category', None)
            categoryId = target_category.get('id')
            all_allow_questions = []

            # Check If Search By All Categories
            if target_category is None or categoryId == 0:
                # Search By Category
                all_allow_questions = [question.format() for
                                       question in Question.query.order_by('id').all(
                ) if question not in previous_questions]
            else:
                # Search By Category
                all_allow_questions = [question.format() for
                                       question in Question.query.filter_by(
                    category=str(categoryId)).all() if question not in previous_questions]

            if len(all_allow_questions) == 0:
                abort(404)
            return jsonify({
                "is_success": True,
                "message": "Successfully Loaded Question",
                # Select Random
                "question": all_allow_questions[random.randrange(0,
                                                                 len(all_allow_questions), 1)],
            })
        except:
            abort(422)

    '''
  @TODO:
  Create error handlers for all expected errors
  including 404 and 422.
  '''
  # Error Handler To 422
    @app.errorhandler(422)
    def error_handler_422(error):
        return jsonify({
            "is_success": False,
            "error": 422,
            "message": "Soory, Some Error Has Been"
        }), 422

    # Error Handler To 404
    @app.errorhandler(404)
    def error_handler_404(error):
        return jsonify({
            "is_success": False,
            "error": 404,
            "message": "Soory, Resources Is Not Found"
        }), 404
    return app
