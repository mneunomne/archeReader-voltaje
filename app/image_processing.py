import cv2 
import cv2.aruco as aruco
import numpy as np
from utils import get_center_point, template_matching
import cv2 
import cv2.aruco as aruco
import numpy as np
from math import atan2, cos, sin, sqrt, pi, floor
from globals import *
        
class ImageProcessor:
    
    lastDetectMarkers = []
    
    def __init__(self):
        # values for aruco markers
        self.adaptiveThreshWinSizeMin = aruco_defaults["adaptiveThreshWinSizeMin"]
        self.adaptiveThreshWinSizeMax = aruco_defaults["adaptiveThreshWinSizeMax"]
        self.adaptiveThreshWinSizeStep = aruco_defaults["adaptiveThreshWinSizeStep"]
        self.adaptiveThreshConstant = aruco_defaults["adaptiveThreshConstant"]
        self.minMarkerPerimeterRate = aruco_defaults["minMarkerPerimeterRate"] # / 1000
        self.maxMarkerPerimeterRate = aruco_defaults["maxMarkerPerimeterRate"] # / 10
        self.polygonalApproxAccuracyRate = aruco_defaults["polygonalApproxAccuracyRate"] # / 1000
    
    def init(self, args, archeReader):
        self.test = args.test 
        self.debug = args.debug
        self.save_frames = args.save_frames
        self.archeReader = archeReader

    def process_image(self, raw_image, segmentIndex):        
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
    
        detector = aruco.ArucoDetector(aruco_dict, parameters)
                
        # Detect markers
        corners, ids, rejectedImgPoints = detector.detectMarkers(gray)
                
        is_valid, detections  = self.validateMarkers(image, corners, ids, segmentIndex)
        
        if is_valid:
            self.archeReader.set_detections(detections)
            return True
        else:
            self.archeReader.set_detections(detections)
            return False
    
    def validateMarkers(self, image, corners, ids, segmentIndex):   
        # make new tuple
        validated_markers = []
        validated_ids = np.array([], int)
        if ids is None:
            return False, (corners, ids)
        if len(ids) < 4:
            return False, (corners, ids)

        top_left = segmentIndex
        top_right = segmentIndex + 1
        bottom_left = top_left + COLS
        bottom_right = top_right + COLS
        
        # find if ids contains top_left, top_right, bottom_left, bottom_right
        corner_ids = [top_left, top_right, bottom_left, bottom_right]
        
        print("corner_ids", corner_ids, ids)
        
        for index, id in enumerate(ids):
            if id in corner_ids:
                # remove element from corners
                validated_markers.append(corners[index])
                validated_ids = np.append(validated_ids, id)
                corner_ids.remove(id)
        
        print("len(corner_ids)", len(corner_ids))
        if len(corner_ids) > 0:
            return False, (corners, ids)
                
        return True, (validated_markers, validated_ids)
    
    def getDetectedMarkers(self):
        return self.lastDetectMarkers

    def clear(self):
        self.archeReader.clear()