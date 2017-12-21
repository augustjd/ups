# -*- coding: utf-8 -*-
"""Creates the API blueprint."""
from flask import Blueprint


blueprint = Blueprint('api', __name__, url_prefix='/api/v1')
