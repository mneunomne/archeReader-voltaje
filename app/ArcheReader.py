import cv2
from globals import *
from image_processing import *
import numpy as np
import cv2.aruco as aruco

from utils import list_ports, get_center_point, load_templates, perspective_transform, template_matching

COLS = 5
ROWS = 6
INNER_COLS = 7
INNER_ROWS = 8
FOLDER_PATH = 'app/numerals/'

TEST_FILE = 'app/test5.jpg'

default_adaptiveThreshWinSizeMin = 3
default_adaptiveThreshWinSizeMax = 16
default_adaptiveThreshWinSizeStep = 13
default_adaptiveThreshConstant = 2
default_minMarkerPerimeterRate = 223
default_maxMarkerPerimeterRate = 40
default_polygonalApproxAccuracyRate = 50

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
  
  def __init__(self, args):
    print("init")
    # check if test mode
    self.test = args.test 
    self.debug = args.debug
    
    # load templates
    self.templates = load_templates(FOLDER_PATH)
    
    self.save_frames = args.save_frames
    self.adaptiveThreshWinSizeMin = default_adaptiveThreshWinSizeMin
    self.adaptiveThreshWinSizeMax = default_adaptiveThreshWinSizeMax
    self.adaptiveThreshWinSizeStep = default_adaptiveThreshWinSizeStep
    self.adaptiveThreshConstant = default_adaptiveThreshConstant
    self.minMarkerPerimeterRate = default_minMarkerPerimeterRate # / 1000
    self.maxMarkerPerimeterRate = default_maxMarkerPerimeterRate # / 10
    self.polygonalApproxAccuracyRate = default_polygonalApproxAccuracyRate # / 1000
    cv2.namedWindow('arche-reading')
    self.createTrackbars()
    self.init()
    
  def createTrackbars(self):
    # Create trackbars
    cv2.createTrackbar('adaptiveThreshWinSizeMin', 'arche-reading', default_adaptiveThreshWinSizeMin, 100, self.on_trackbar)
    cv2.createTrackbar('adaptiveThreshWinSizeMax', 'arche-reading', default_adaptiveThreshWinSizeMax, 100, self.on_trackbar)
    cv2.createTrackbar('adaptiveThreshWinSizeStep', 'arche-reading', default_adaptiveThreshWinSizeStep, 100, self.on_trackbar)
    cv2.createTrackbar('adaptiveThreshConstant', 'arche-reading', default_adaptiveThreshConstant, 100, self.on_trackbar)
    cv2.createTrackbar('minMarkerPerimeterRate', 'arche-reading', default_minMarkerPerimeterRate, 1000, self.on_trackbar)
    cv2.createTrackbar('maxMarkerPerimeterRate', 'arche-reading', default_maxMarkerPerimeterRate, 100,  self.on_trackbar)
    cv2.createTrackbar('polygonalApproxAccuracyRate', 'arche-reading', default_polygonalApproxAccuracyRate, 1000, self.on_trackbar)
  
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
      path = TEST_FILE
      frame = cv2.imread(path)
      return frame
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
    
    if self.debug == True:
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
        # print("center_point", center_point)
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
      
      # Define the dimensions of the output square
      output_side_length = 200  # Adjust this value as needed

      output_width = 700
      output_height = 800

      # Define the coordinates of the output rectangle
      output_rect = np.array([[0, 0], [output_width - 1, 0], [output_width - 1, output_height - 1], [0, output_height - 1]], dtype=np.float32)

      # Calculate the perspective transformation matrix
      perspective_matrix = cv2.getPerspectiveTransform(roi_corners.astype(np.float32), output_rect)

      # Apply the perspective transformation to the original image
      rect_roi = cv2.warpPerspective(image, perspective_matrix, (output_width, output_height))

      roi_cropped = rect_roi
      
      # rotate 90 degrees
      _w = output_width
      _h = output_height
      padding = 20
      padding_x = padding
      padding_y = padding + 10
      # Calculate the dimensions of each segment
      segment_width = (_w - padding_x * 2) // INNER_COLS
      segment_height = (_h - padding_y * 2)  // INNER_ROWS
      
      # Convert the cropped image to grayscale
      # gray_cropped = cv2.cvtColor(roi_cropped, cv2.COLOR_BGR2GRAY)

      # Loop through the grid and extract each segment
      for i in range(INNER_ROWS):
        for j in range(INNER_COLS):
          # Calculate the coordinates for the current segment
          x_start = j * segment_width + padding_x
          y_start = i * segment_height + padding_y
          x_end = (j + 1) * segment_width + padding_x
          y_end = (i + 1) * segment_height + padding_y
          segment_corners = np.array([[x_start, y_start], [x_end, y_start], [x_end, y_end], [x_start, y_end]], dtype='float32')

          # draw rect from segment_corners
          for k in range(4):
            start_point = segment_corners[k]
            end_point = segment_corners[(k + 1) % 4]
            # convert to int 
            start_point = (int(start_point[0]), int(start_point[1]))
            end_point = (int(end_point[0]), int(end_point[1]))
            roi_cropped = cv2.line(roi_cropped, start_point, end_point, (0, 255, 0), 2)
          
          # Extract the segment
          segment = roi_cropped[y_start:y_end, x_start:x_end]
          
          # gray segment
          gray_segment = cv2.cvtColor(segment, cv2.COLOR_BGR2GRAY)
          
          # Perform template matching
          matched_template, matched_filename = template_matching(gray_segment, self.templates)
          matched_filename = matched_filename.split(".")[0]
          roi_cropped = cv2.putText(roi_cropped, matched_filename, (x_start, y_start+20),  cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0) )

          # Display the matched template
          cv2.imshow(f'Matched Template ({i}, {j})', gray_segment)
          
          # Display the segment in a separate window
          if self.save_frames == True:
            # random id for now
            id = np.random.randint(low=0, high=100000000000000)
            filename = f'frames/segment_{i}_{j}_{id}.jpg'
            cv2.imwrite(filename, segment)
          # cv2.imshow(f'Segment ({i}, {j})', segment)
        # draw lines
      if self.save_frames == True:
        # after saving, quit software
        self.capture.release()
        cv2.destroyAllWindows()
        quit()
      # Display the cropped ROI in a separate window
      cv2.imshow('Cropped ROI', roi_cropped)
    return image
  
  def onDetectedMarker (self, corners, ids):
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
  
