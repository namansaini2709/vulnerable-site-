import os
from dotenv import load_dotenv
load_dotenv('/path/to/.env')
app = Flask(__name__)
app.config.from_envvar('ENV_FILE')