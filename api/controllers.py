import json
import logging
import traceback

import flask
from flask import Blueprint, current_app

from api.db.questions import Questions


QUESTION_EXPIRATION_SECONDS = 86400

logger = logging.getLogger(__name__)

controllers = Blueprint('controllers', __name__)

question = Questions()


@controllers.route('/questionsById/<question_id>', methods=['GET'])
def questionsById(question_id):
    pass
