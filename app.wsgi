import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, current_dir)

from app import create_app

application = create_app()