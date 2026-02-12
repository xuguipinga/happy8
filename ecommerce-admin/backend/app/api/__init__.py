from flask import Blueprint

api = Blueprint('api', __name__)

from app.api import auth
from app.api import upload
from app.api import orders
from app.api import purchases
from app.api import logistics
from app.api import analysis
from app.api import tenants
from app.api import profile
from app.api import statistics

