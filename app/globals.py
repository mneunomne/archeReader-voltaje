import os
from dotenv import load_dotenv

# load .env file
load_dotenv()

# get environment variables
WEBCAM = int(os.environ.get("WEBCAM"))
THRESHOLD_1 = int(os.environ.get("THRESHOLD_1"))
THRESHOLD_2 = int(os.environ.get("THRESHOLD_2"))
MIN_LINE_LENGTH = int(os.environ.get("MIN_LINE_LENGTH"))
MAX_LINE_GAP  = int(os.environ.get("MAX_LINE_GAP"))
