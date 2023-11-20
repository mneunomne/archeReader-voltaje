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
SEGMENT_OUTPUT_HEIGHT = 700

# ceramic data
COLS = 5
ROWS = 6
INNER_COLS = 7
INNER_ROWS = 7

# paths
FOLDER_PATH = 'app/numerals/'
TEST_FILE = 'app/test_images/teste11.png'

# aruco marker settings
aruco_defaults = {
  "adaptiveThreshWinSizeMin": 3,
  "adaptiveThreshWinSizeMax": 25,
  "adaptiveThreshWinSizeStep": 3,
  "adaptiveThreshConstant": 3,
  "minMarkerPerimeterRate": 160,
  "maxMarkerPerimeterRate": 69,
  "polygonalApproxAccuracyRate": 50,
  "cornerRefinementWinSize": 5,
  "cornerRefinementMaxIterations": 30,
  "minDistanceToBorder": 1,
  "minOtsuStdDev": 5,
  "perspectiveRemovePixelPerCell": 8,
  "adaptiveThreshWinSize": 23,
}