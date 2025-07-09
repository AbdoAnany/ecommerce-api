from flask import Blueprint

bp = Blueprint('shipping', __name__)

from app.shipping import routes
