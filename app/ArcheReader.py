import cv2
from globals import *
import numpy as np
import cv2.aruco as aruco
from utils import list_ports, load_templates
from flask_server import app, sendVideoOutput, sendCroppedOutput, socketio, imageProcessor
from socket_connection import connectSocket
import threading
import queue

ready_to_read = False
thread_flask = None

class ArcheReader:
  
  capture = None
  
  crop_size = 200
  
  def __init__(self, args):
    print("init")
    # check if test mode
    self.test = args.test 
    self.debug = args.debug
    self.detections = []
    
    self.detections_queue = queue.Queue()  # Queue for passing detections between threads
    
    imageProcessor.init(args, self)
        
    # start flask
    if (args.flask):
      thread_flask = threading.Thread(target=socketio.run, args=(app, FLASK_SERVER_IP, FLASK_SERVER_PORT,))
      thread_flask.start()
    
    # load templates
    self.templates = load_templates(FOLDER_PATH)
    
    self.save_frames = args.save_frames
    self.adaptiveThreshWinSizeMin = aruco_defaults["adaptiveThreshWinSizeMin"]
    self.adaptiveThreshWinSizeMax = aruco_defaults["adaptiveThreshWinSizeMax"]
    self.adaptiveThreshWinSizeStep = aruco_defaults["adaptiveThreshWinSizeStep"]
    self.adaptiveThreshConstant = aruco_defaults["adaptiveThreshConstant"]
    self.minMarkerPerimeterRate = aruco_defaults["minMarkerPerimeterRate"] # / 1000
    self.maxMarkerPerimeterRate = aruco_defaults["maxMarkerPerimeterRate"] # / 10
    self.polygonalApproxAccuracyRate = aruco_defaults["polygonalApproxAccuracyRate"] # / 1000
    cv2.namedWindow('arche-reading')
    #self.createTrackbars()
    self.init()
    
  def init(self):
    # if test enabled, use static image
    self.run_opencv()
    #thread_opencv.start()
  
  def start_cam(self):
    # detect available cameras
    _,working_ports,_ = list_ports()
    print("working_ports", working_ports)
    
  def set_detections(self, detections):
    print("detections", detections)
    self.detections = detections
  
    
  def createTrackbars(self):
    # Create trackbars
    cv2.createTrackbar('adaptiveThreshWinSizeMin', 'arche-reading', aruco_defaults["adaptiveThreshWinSizeMin"], 100, self.on_trackbar)
    cv2.createTrackbar('adaptiveThreshWinSizeMax', 'arche-reading', aruco_defaults["adaptiveThreshWinSizeMax"], 100, self.on_trackbar)
    cv2.createTrackbar('adaptiveThreshWinSizeStep', 'arche-reading', aruco_defaults["adaptiveThreshWinSizeStep"], 100, self.on_trackbar)
    cv2.createTrackbar('adaptiveThreshConstant', 'arche-reading', aruco_defaults["adaptiveThreshConstant"], 100, self.on_trackbar)
    cv2.createTrackbar('minMarkerPerimeterRate', 'arche-reading', aruco_defaults["minMarkerPerimeterRate"], 1000, self.on_trackbar)
    cv2.createTrackbar('maxMarkerPerimeterRate', 'arche-reading', aruco_defaults["maxMarkerPerimeterRate"], 100,  self.on_trackbar)
    cv2.createTrackbar('polygonalApproxAccuracyRate', 'arche-reading', aruco_defaults["polygonalApproxAccuracyRate"], 1000, self.on_trackbar)
    
  def on_trackbar(self, value):
    # Update parameters based on trackbar values
    self.adaptiveThreshWinSizeMin = cv2.getTrackbarPos('adaptiveThreshWinSizeMin', 'arche-reading')
    self.adaptiveThreshWinSizeMax = cv2.getTrackbarPos('adaptiveThreshWinSizeMax', 'arche-reading')
    self.adaptiveThreshWinSizeStep = cv2.getTrackbarPos('adaptiveThreshWinSizeStep', 'arche-reading')
    self.adaptiveThreshConstant = cv2.getTrackbarPos('adaptiveThreshConstant', 'arche-reading')
    self.minMarkerPerimeterRate = cv2.getTrackbarPos('minMarkerPerimeterRate', 'arche-reading')
    self.maxMarkerPerimeterRate = cv2.getTrackbarPos('maxMarkerPerimeterRate', 'arche-reading')
    self.polygonalApproxAccuracyRate = cv2.getTrackbarPos('polygonalApproxAccuracyRate', 'arche-reading')
    
  def run_opencv(self):
    
    # create window
    cv2.startWindowThread()
    cv2.namedWindow("arche-reading")
    cv2.namedWindow("cropped")

    while True:
      
      # Check the queue for new detections
      try:
          new_detections = self.detections_queue.get_nowait()
          self.display_detections(new_detections)
      except queue.Empty:
          pass
      
      # display image
      image = self.get_image()
      
      video_output = image.copy()
        # send video to flask
      sendVideoOutput(video_output)
      print("self.detections", self.detections)
      
      cv2.imshow('arche-reading', image)
      if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # When everything done, release the capture
    self.capture.release()
    cv2.destroyAllWindows()
    
  def display_detections(self, new_detections):
    # Update the OpenCV display with new detections
    # This method should be called from the main thread
    print("New Detections:", new_detections)
    # Implement your display logic here
    
  def set_detections(self, detections):
    print("detections", detections)
    self.detections = detections

    # Put the new detections in the queue for the main thread to pick up
    self.detections_queue.put(detections)
    
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


