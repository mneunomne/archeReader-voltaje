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
    
    lastDetectSegment = None
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
        # create window
        # cv2.startWindowThread()
        # cv2.namedWindow("processor")
        
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
        
        # self.archeReader.show_image(image)
        
        # self.archeReader.draw_detections(image, corners, ids)
                
        is_valid, detections  = self.validateMarkers(image, corners, ids, segmentIndex)
        
        if is_valid:
            self.archeReader.set_detections(detections)
            # self.archeReader.validate_detections()
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

        top_left = segmentIndex + 1
        top_right = segmentIndex + 2
        bottom_left = top_left + COLS
        bottom_right = top_right + COLS
        
        # find if ids contains top_left, top_right, bottom_left, bottom_right
        corner_ids = [top_left, top_right, bottom_left, bottom_right]
        
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
    
    def processDetectedMarkers(self, image, corners, ids):
        image = aruco.drawDetectedMarkers(image, corners, ids)
        # store last detected markers...
        self.onDetectedMarker(corners, ids)
        
        center_points = []
        if len(self.lastDetectMarkers) == 4:
            # draw corners
            for index, (id, center_point) in enumerate(self.lastDetectMarkers):
                # print("center_point", center_point)
                image = cv2.circle(image, center_point, 5, (0, 0, 255), -1)
                center_points.append(center_point)
        else: 
            return image

        ordered_corners = [center_points[0], center_points[1], center_points[3], center_points[2]]
            
        for i, corner in enumerate(ordered_corners):
            start_point = ordered_corners[i]
            end_point = ordered_corners[(i + 1) % 4]  # Connect the last point to the first point
            # draw line between each marker
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
        
        # size of output image segment
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
        
        segment_data = []

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
                
                # segment data
                data = {
                    "matched_filename": matched_filename,
                    "row": i,
                    "col": j,
                }
                segment_data.append(data)
                
                # Display the matched template
                # cv2.imshow(f'Matched Template ({i}, {j})', gray_segment)
                
                # Display the segment in a separate window
                if self.save_frames == True:
                    # random id for now
                    id = np.random.randint(low=0, high=100000000000000)
                    filename = f'frames/segment_{i}_{j}_{id}.jpg'
                    cv2.imwrite(filename, segment)
                # cv2.imshow(f'Segment ({i}, {j})', segment)
                # draw lines
        
        #if segment_data != []:
            # send segment data to flask
            # self.decode_segments(segment_data)
        # cv2.imshow('cropped', roi_cropped)
        return segment_data
    
    def getDetectedMarkers(self):
        return self.lastDetectMarkers
    
    
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
        
    def decode_segments(self, data):
        print("segment_data", data)
        json_object = json.dumps(data, indent = 4) 
        socketio.emit('segment_data', json_object)
        # decode segments
        pass