import os
from dotenv import load_dotenv

# load .env file
load_dotenv()

# get environment variables
WEBCAM = int(os.environ.get("WEBCAM"))

# flask server settings
FLASK_SERVER_IP = os.environ.get("FLASK_SERVER_IP")
FLASK_SERVER_PORT = int(os.environ.get("FLASK_SERVER_PORT"))

# size of cropped images
SEGMENT_WIDTH = 68
SEGMENT_HEIGHT = 68

SEGMENT_OUTPUT_WIDTH = 700
SEGMENT_OUTPUT_HEIGHT = 800

# ceramic data
COLS = 5
ROWS = 6
INNER_COLS = 7
INNER_ROWS = 8

# paths
FOLDER_PATH = 'app/numerals/'
TEST_FILE = 'app/test_images/test8.jpg'

# aruco marker settings
aruco_defaults = {
  "adaptiveThreshWinSizeMin": 3,
  "adaptiveThreshWinSizeMax": 25,
  "adaptiveThreshWinSizeStep": 2,
  "adaptiveThreshConstant": 3,
  "minMarkerPerimeterRate": 100,
  "maxMarkerPerimeterRate": 40,
  "polygonalApproxAccuracyRate": 50
}