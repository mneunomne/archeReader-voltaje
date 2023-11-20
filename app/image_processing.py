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
    
    storedDetections = ([], np.array([], int))
    
    def __init__(self):
        # values for aruco markers
        self.adaptiveThreshWinSizeMin = aruco_defaults["adaptiveThreshWinSizeMin"]
        self.adaptiveThreshWinSizeMax = aruco_defaults["adaptiveThreshWinSizeMax"]
        self.adaptiveThreshWinSizeStep = aruco_defaults["adaptiveThreshWinSizeStep"]
        self.adaptiveThreshConstant = aruco_defaults["adaptiveThreshConstant"]
        self.minMarkerPerimeterRate = aruco_defaults["minMarkerPerimeterRate"] # / 1000
        self.maxMarkerPerimeterRate = aruco_defaults["maxMarkerPerimeterRate"] # / 10
        self.polygonalApproxAccuracyRate = aruco_defaults["polygonalApproxAccuracyRate"] # / 1000
        self.cornerRefinementWinSize = aruco_defaults["cornerRefinementWinSize"]
        self.cornerRefinementMaxIterations = aruco_defaults["cornerRefinementMaxIterations"]
        self.minDistanceToBorder = aruco_defaults["minDistanceToBorder"]
        self.minOtsuStdDev = aruco_defaults["minOtsuStdDev"]
        self.perspectiveRemovePixelPerCell = aruco_defaults["perspectiveRemovePixelPerCell"]
        self.storedDetections = ([], [])
    
    def init(self, args, archeReader):
        self.test = args.test 
        self.debug = args.debug
        self.save_frames = args.save_frames
        self.archeReader = archeReader
    
    def clear_stored_markers(self):
        self.storedDetections = ([], [])

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
        parameters.cornerRefinementWinSize = self.cornerRefinementWinSize
        parameters.cornerRefinementMaxIterations = self.cornerRefinementMaxIterations
        parameters.minDistanceToBorder = self.minDistanceToBorder
        parameters.perspectiveRemovePixelPerCell = self.perspectiveRemovePixelPerCell
    
        detector = aruco.ArucoDetector(aruco_dict, parameters)
                
        # Detect markers
        corners, ids, rejectedImgPoints = detector.detectMarkers(gray)
                
        is_valid, detections = self.validateMarkers(image, corners, ids, segmentIndex)

        # store detections that are valid
        for index, id in enumerate(detections[1]):
            # print("id" ,id)
            if id not in self.storedDetections[1]:
                self.storedDetections[0].append(detections[0][index])
                self.storedDetections[1].append(id)
            else:
                stored_index = self.storedDetections[1].index(id)
                self.storedDetections[0][stored_index] = detections[0][index]

        # Convert ids to a numpy array
        ids_np = np.array(self.storedDetections[1], int)

        # Check if all expected detections are present in storedDetections
        if set(ids_np) == set([segmentIndex, segmentIndex + 1, segmentIndex + COLS, segmentIndex + COLS + 1]):
            is_valid = True
        
        # if stored detection doesnt have specific detection id, add it
        
        message = self.archeReader.set_detections((self.storedDetections[0], ids_np), raw_image, is_valid)
        return is_valid, message
            
    def validateMarkers(self, image, corners, ids, segmentIndex):
        # make new tuple
        validated_markers = []
        validated_ids = np.array([], int)
        if ids is None:
            return False, ([], [])

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
        
        validated_ids = np.array(validated_ids, int)  # Convert to numpy array

        if len(corner_ids) > 0:
            return False, (validated_markers, validated_ids)

        return True, (validated_markers, validated_ids)
    
    def getDetectedMarkers(self):
        return self.lastDetectMarkers

    def clear(self):
        self.archeReader.clear()