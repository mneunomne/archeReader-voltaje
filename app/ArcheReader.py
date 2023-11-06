import cv2
from globals import *
from image_processing import *
import numpy as np
import cv2.aruco as aruco

from utils import list_ports

COLS = 5
ROWS = 6
INNER_COLS = 7
INNER_ROWS = 8

def get_center_point(corners):
    # Calculate the average of x-coordinates and y-coordinates
    avg_x = np.mean(corners[:, :, 0])
    avg_y = np.mean(corners[:, :, 1])

    return int(avg_x), int(avg_y)

class ArcheReader:
  
  capture = None
  
  # default values for canny edge detection and hough lines
  threshold1 = 7
  threshold2 = 12
  minLineLength = 40
  maxLineGap = 75
  set_update= True
  
  lastDetectSegment = None
  
  lastDetectMarkers = []
  
  crop_size = 200
  
  def __init__(self, test):
    self.test = test
    print("init")
    self.adaptiveThreshWinSizeMin = 3
    self.adaptiveThreshWinSizeMax = 23
    self.adaptiveThreshWinSizeStep = 10
    self.adaptiveThreshConstant = 8
    self.minMarkerPerimeterRate = 160 # / 1000
    self.maxMarkerPerimeterRate = 40 # / 10
    self.polygonalApproxAccuracyRate = 50 # / 1000
    cv2.namedWindow('arche-reading')
    self.createTrackbars()
    self.init()
    
  def createTrackbars(self):
    # Create trackbars
    cv2.createTrackbar('adaptiveThreshWinSizeMin', 'arche-reading', 3, 100, self.on_trackbar)
    cv2.createTrackbar('adaptiveThreshWinSizeMax', 'arche-reading', 23, 100, self.on_trackbar)
    cv2.createTrackbar('adaptiveThreshWinSizeStep', 'arche-reading', 10, 100, self.on_trackbar)
    cv2.createTrackbar('adaptiveThreshConstant', 'arche-reading', 8, 100, self.on_trackbar)
    cv2.createTrackbar('minMarkerPerimeterRate', 'arche-reading', 160, 1000, self.on_trackbar)
    cv2.createTrackbar('maxMarkerPerimeterRate', 'arche-reading', 40, 100,  self.on_trackbar)
    cv2.createTrackbar('polygonalApproxAccuracyRate', 'arche-reading', 50, 1000, self.on_trackbar)
  
  def on_trackbar(self, value):
    # Update parameters based on trackbar values
    self.adaptiveThreshWinSizeMin = cv2.getTrackbarPos('adaptiveThreshWinSizeMin', 'arche-reading')
    self.adaptiveThreshWinSizeMax = cv2.getTrackbarPos('adaptiveThreshWinSizeMax', 'arche-reading')
    self.adaptiveThreshWinSizeStep = cv2.getTrackbarPos('adaptiveThreshWinSizeStep', 'arche-reading')
    self.adaptiveThreshConstant = cv2.getTrackbarPos('adaptiveThreshConstant', 'arche-reading')
    self.minMarkerPerimeterRate = cv2.getTrackbarPos('minMarkerPerimeterRate', 'arche-reading')
    self.maxMarkerPerimeterRate = cv2.getTrackbarPos('maxMarkerPerimeterRate', 'arche-reading')
    self.polygonalApproxAccuracyRate = cv2.getTrackbarPos('polygonalApproxAccuracyRate', 'arche-reading')
    
  def init(self):
    # if test enabled, use static image
    self.run()
  
  def start_cam(self):
    # detect available cameras
    _,working_ports,_ = list_ports()
    print("working_ports", working_ports)
  
  def get_image(self):
    # if test enabled, use static image
    if self.test:
      return "test.jpg"
    # get current frame from webcam
    if self.capture == None:
      self.start_cam()
      self.capture = cv2.VideoCapture(WEBCAM)
    if self.capture.isOpened():
      #do something
      ret, frame = self.capture.read()
      return frame
    else:
      print("Cannot open camera")
    
  def run(self):
    while True:
      # display image
      if self.set_update:
        image = self.get_image()
        image = self.process_image(image)
        cv2.imshow('arche-reading', image)
        # self.set_update = False
      if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    # When everything done, release the capture
    self.capture.release()
    cv2.destroyAllWindows()
  
  def process_image(self, raw_image):
    image = raw_image.copy()
    # Convert the image to grayscale (if necessary)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    
    # Load the ArUco dictionary (you may need to adjust the dictionary type)
    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_1000)
    
    # Initialize the detector parameters
    parameters = aruco.DetectorParameters()
    parameters.adaptiveThreshWinSizeMin = self.adaptiveThreshWinSizeMin
    parameters.adaptiveThreshWinSizeMax = self.adaptiveThreshWinSizeMax
    parameters.adaptiveThreshWinSizeStep = self.adaptiveThreshWinSizeStep
    parameters.adaptiveThreshConstant = self.adaptiveThreshConstant
    parameters.minMarkerPerimeterRate = self.minMarkerPerimeterRate / 1000
    parameters.maxMarkerPerimeterRate = self.maxMarkerPerimeterRate / 10
    parameters.polygonalApproxAccuracyRate = self.polygonalApproxAccuracyRate / 1000
    
    print("values")
    print("adaptiveThreshWinSizeMin", self.adaptiveThreshWinSizeMin)
    print("adaptiveThreshWinSizeMax", self.adaptiveThreshWinSizeMax)
    print("adaptiveThreshWinSizeStep", self.adaptiveThreshWinSizeStep)
    print("adaptiveThreshConstant", self.adaptiveThreshConstant)
    print("minMarkerPerimeterRate", self.minMarkerPerimeterRate / 1000)
    print("maxMarkerPerimeterRate", self.maxMarkerPerimeterRate / 10)
    print("polygonalApproxAccuracyRate", self.polygonalApproxAccuracyRate / 1000)
    
  
    detector = aruco.ArucoDetector(aruco_dict, parameters)

    # Detect markers
    corners, ids, rejectedImgPoints = detector.detectMarkers(gray)
    
    # Draw the detected markers on the image
    if ids is not None:
      image = aruco.drawDetectedMarkers(image, corners, ids)
      self.onDetectedMarker(corners, ids)
      min_id = min(ids)[0]
      N = min_id
      lt = N            # left top corner
      rt = N + 1        # right top corner
      lb = N + COLS     # left bottom corner
      rb = N + COLS + 1 # right bottom corner
      
    if len(self.lastDetectMarkers) == 4:
      # draw corners
      center_points = []
      for index, (id, center_point) in enumerate(self.lastDetectMarkers):
        print("center_point", center_point)
        image = cv2.circle(image, center_point, 5, (0, 0, 255), -1)
        center_points.append(center_point)        
        
      ordered_corners = [center_points[0], center_points[1], center_points[3], center_points[2]]
        
      for i, corner in enumerate(ordered_corners):
        start_point = ordered_corners[i]
        end_point = ordered_corners[(i + 1) % 4]  # Connect the last point to the first point
        image = cv2.line(image, start_point, end_point, (0, 255, 0), 2)
      
      # Define the ROI using the corner points of the markers
      
      roi_corners = np.array([marker for marker in ordered_corners], dtype=np.int32)
      roi_corners = roi_corners.reshape((-1, 1, 2))
      
      # Create a mask for the ROI
      mask = np.zeros_like(image)
      cv2.fillPoly(mask, [roi_corners], (255, 255, 255))
      
      # Apply the mask to the original image
      roi_image = cv2.bitwise_and(image, mask)
      
      # Get the bounding box of the ROI
      x, y, w, h = cv2.boundingRect(roi_corners)
      
      # Crop the image using the bounding box
      roi_cropped = roi_image[y:y+h, x:x+w]
      
      # rotate 90 degrees
      roi_cropped = cv2.rotate(roi_cropped, cv2.ROTATE_90_COUNTERCLOCKWISE)
      padding = 20
      _w = h
      _h = w
      # Calculate the dimensions of each segment
      segment_width = (_w - padding * 2) // INNER_COLS
      segment_height = (_h - padding * 2)  // INNER_ROWS
      
       # Convert the cropped image to grayscale
      gray_cropped = cv2.cvtColor(roi_cropped, cv2.COLOR_BGR2GRAY)

      # Draw lines separating the columns
      for i in range(0, INNER_COLS+1):
        x = i * segment_width + padding
        roi_cropped = cv2.line(roi_cropped, (x, padding), (x, _h-padding), (0, 255, 0), 2)

      # Draw lines separating the rows
      for i in range(0, INNER_ROWS+1):
        y = i * segment_height + padding
        roi_cropped = cv2.line(roi_cropped, (padding, y), (_w-padding, y), (0, 255, 0), 2)

      # Display the cropped ROI in a separate window
      cv2.imshow('Cropped ROI', roi_cropped)

      # Loop through the grid and extract each segment
      #for i in range(ROWS):
      #  for j in range(COLS):
      #    # Calculate the coordinates for the current segment
      #    x_start = j * segment_width
      #    y_start = i * segment_height
      #    x_end = (j + 1) * segment_width
      #    y_end = (i + 1) * segment_height
      #    # Extract the segment
      #    segment = roi_cropped[y_start:y_end, x_start:x_end]
      #    # Display the segment in a separate window
      #    cv2.imshow(f'Segment ({i}, {j})', segment)
      #  # draw lines
    return image
  
  def onDetectedMarker (self, corners, ids):
    # print("onDetectedMarker")
    #print("corners", corners)
    print("ids", ids)
    for index, id in enumerate(ids):
      if id > COLS * ROWS:
        # invalid, continue
        continue
      center_point = get_center_point(corners[index])
        
      # check if lastDetectMarkers contains id
      found = False
      for _index, (_id, _center_point) in enumerate(self.lastDetectMarkers):
        if id == _id:
          found = True
          break
      if not found:
        self.lastDetectMarkers.append((id, center_point))
      else:
        # update center point
        self.lastDetectMarkers[_index] = (id, center_point)
    # order lastDetectMarkers by id
    self.lastDetectMarkers = sorted(self.lastDetectMarkers, key=lambda x: x[0])
    print("lastDetectMarkers", self.lastDetectMarkers)
  
