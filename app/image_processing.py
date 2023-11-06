import cv2 
import cv2.aruco as aruco
import numpy as np
from math import atan2, cos, sin, sqrt, pi, floor

def find_intersections(lines):
  intersections = []
  for i in range(len(lines)):
    for j in range(i + 1, len(lines)):
      x1, y1, x2, y2 = lines[i][0]
      x3, y3, x4, y4 = lines[j][0]
        
      det = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        
      if det != 0:  # Checking if lines are not parallel
        intersection_x = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / det
        intersection_y = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / det
        intersections.append((int(intersection_x), int(intersection_y)))
  return intersections

def distance_point_to_line(x, y, line):
    x1, y1, x2, y2 = line[0]
    numerator = abs((x2 - x1) * (y1 - y) - (x1 - x) * (y2 - y1))
    denominator = ((x2 - x1)**2 + (y2 - y1)**2)**0.5
    return numerator / denominator

def filter_close_lines(lines, min_distance):
    filtered_lines = []
    for i in range(len(lines)):
        keep_line = True
        for j in range(len(lines)):
            if i != j:
                x1, y1, x2, y2 = lines[i][0]
                _x1, _y1, _x2, _y2 = lines[j][0]
                
                dist1 = distance_point_to_line(x1, y1, lines[j])
                dist2 = distance_point_to_line(x2, y2, lines[j])
                
                if dist1 < min_distance or dist2 < min_distance:
                    keep_line = False
                    break
        
        if keep_line:
            filtered_lines.append(lines[i])
    
    return filtered_lines

def getSmallestDistanceBetweenPoints(points):
    smallest = 100
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            print(points[i], points[j])
            distance = np.linalg.norm(np.array(points[i]) - np.array(points[j]))
            if distance < smallest:
                smallest = distance
    return smallest

def find_intersections2(horizontal_lines, vertical_lines):
    intersections = []

    for h_line in horizontal_lines:
        for v_line in vertical_lines:
            intersection = find_intersection(h_line, v_line)
            if intersection is not None:
                intersections.append(intersection)
    return intersections

def draw_squares(image, intersections, side_length):
  for intersection in intersections:
    x, y = intersection
    half_side = side_length // 2
    cv2.rectangle(image, (x - half_side, y - half_side), (x + half_side, y + half_side), (0, 255, 0), 2)

def getDistanceBetweenLines(line1, line2):
    x1, y1, x2, y2 = line1[0]
    x3, y3, x4, y4 = line2[0]
    return np.linalg.norm(np.array([x1, y1]) - np.array([x3, y3]))

# gray image expected
def findHoughPLine(image, threshold1, threshold2, minLineLength, maxLineGap):
  gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
  edges = cv2.Canny(gray, threshold1, threshold2)
  lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=50, minLineLength=minLineLength, maxLineGap=maxLineGap)
  return lines, edges

def getCroppedImage(image, size):
  height, width, ch = image.shape
  n = int(size / 2)
  cropped_image = image[int(height/2)-n:int(height/2)+n, int(width/2)-n:int(width/2)+n, :]
  return cropped_image

def get_angle(p_, q_):
    p = list(p_)
    q = list(q_)
    angle = atan2(p[1] - q[1], p[0] - q[0])  # angle in radians
    return angle


def filter_lines_by_angle(lines, ref_angle, tolerance=50):
    # print("ref_angle", ref_angle)
    filtered_lines = []
    for i, line in enumerate(lines):
        x1, y1, x2, y2 = line[0]
        is_valid = True
        angle = np.rad2deg(get_angle([x1, y1], [x2, y2]))
        #print("angles: ", angle, ref_angle)
        angle_diff = abs(angle - ref_angle)
        if angle_diff <= tolerance or abs(angle_diff - 180) <= tolerance:
            filtered_lines.append(line)
    return filtered_lines

# merge lines that are very close to one another
max_dist = 10
def mergeLines(lines, max_dist=10):
    merged_lines = []
    i = 0
    while i < len(lines):
        x1, y1, x2, y2 = lines[i][0]
        j = i + 1
        while j < len(lines):
            x3, y3, x4, y4 = lines[j][0]
            if abs(x1 - x3) < max_dist and abs(y1 - y3) < max_dist:
                # Merge the two lines
                lines[i][0] = [(x1 + x3) / 2, (y1 + y3) / 2, (x2 + x4) / 2, (y2 + y4) / 2]
                # Remove line j
                lines = np.delete(lines, j, axis=0)
                # Decrement j as the array length has decreased by 1
                j -= 1
            j += 1
        merged_lines.append(lines[i])
        i += 1
    return merged_lines

def remove_too_close_lines(lines, max_dist=10):
    i = 0
    while i < len(lines):
        x1, y1, x2, y2 = lines[i][0]
        j = i + 1
        while j < len(lines):
            x3, y3, x4, y4 = lines[j][0]
            if abs(x1 - x3) < max_dist and abs(y1 - y3) < max_dist:
                # Remove line j
                lines = np.delete(lines, j, axis=0)
                # Decrement j as the array length has decreased by 1
                j -= 1
            j += 1
        i += 1
    return lines


def find_squares(lines, threshold=10):
    squares = []
    for i in range(len(lines)):
        for j in range(i + 1, len(lines)):
            for k in range(j + 1, len(lines)):
                for l in range(k + 1, len(lines)):
                    # Check for intersections
                    intersection_points = []
                    for p1 in lines[i]:
                        for p2 in lines[j]:
                            intersection = intersection_point(p1, p2)
                            if intersection is not None:
                                intersection_points.append(intersection)
                    for p1 in lines[k]:
                        for p2 in lines[l]:
                            intersection = intersection_point(p1, p2)
                            if intersection is not None:
                                intersection_points.append(intersection)
                    
                    # Check if intersection points form a square
                    if len(intersection_points) == 4:
                        distances = [
                            np.linalg.norm(intersection_points[0] - intersection_points[1]),
                            np.linalg.norm(intersection_points[0] - intersection_points[2]),
                            np.linalg.norm(intersection_points[0] - intersection_points[3])
                        ]
                        if all(abs(d1 - d2) < threshold for d1 in distances for d2 in distances):
                            squares.append(intersection_points)
    
    return squares

def intersection_point(line1, line2):
    x1, y1, x2, y2 = line1
    x3, y3, x4, y4 = line2

    det = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if det != 0:
        intersect_x = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / det
        intersect_y = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / det
        return np.array([intersect_x, intersect_y])
    return None

def getLongestHorizontalLine(lines):
    longest = 0
    longest_line = None
    for line in lines:
        x1, y1, x2, y2 = line[0]
        if abs(x1 - x2) > longest:
            longest = abs(x1 - x2)
            longest_line = line
    return longest_line

def makeGridFromHorizontalLine(line, gap=10, img_shape=(200, 200)):
    x1, y1, x2, y2 = line[0]
    lines = []
    rows = int(img_shape[1] / gap)
    for i in range(-rows, rows):
        _y1 = y1 + i * gap
        _y2 = y2 + i * gap
        lines.append([[x1, _y1, x2, _y2]])
    return lines

def getLongestVerticalLine(lines):
    longest = 0
    longest_line = None
    for line in lines:
        x1, y1, x2, y2 = line[0]
        if abs(y1 - y2) > longest:
            longest = abs(y1 - y2)
            longest_line = line
    return longest_line

def makeGridFromVerticalLine(line, gap=10, img_shape=(200, 200)):
    x1, y1, x2, y2 = line[0]
    lines = []
    cols = int(img_shape[0] / gap)
    for i in range(-cols, cols):
        _x1 = x1 + i * gap
        _x2 = x2 + i * gap
        lines.append([[_x1, y1, _x2, y2]])
    return lines


def find_intersection(line1, line2):
    x1, y1, x2, y2 = line1[0]
    x3, y3, x4, y4 = line2[0]
    
    denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    
    if denominator == 0:
        return None  # Lines are parallel or coincident
    else:
        intersection_x = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / denominator
        intersection_y = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / denominator
        return int(intersection_x), int(intersection_y)

def getRectsFromIntersectionPoints(horizontal_lines, vertical_lines):
    rectangles = []

    for h_line in horizontal_lines:
        for v_line in vertical_lines:
            x = v_line[0]
            y = h_line[1]
            width = v_line[2] - v_line[0]
            height = h_line[3] - h_line[1]

            rect = (x, y, width, height)
            rectangles.append(rect)

    return rectangles

def arrange_points_clockwise(points):
    center = np.mean(points, axis=0)
    return sorted(points, key=lambda p: np.arctan2(p[1] - center[1], p[0] - center[0]))

def create_polygons_and_rectangles(intersection_points):
    polygons = []
    rectangles = []

    # Rearrange points in correct order and generate polygons and rectangles
    for i in range(0, len(intersection_points), 4):
        polygon_points = arrange_points_clockwise(intersection_points[i:i+4])
        polygons.append(polygon_points)

    return polygons, rectangles


def fill_horizontal_lines(horizontal_lines, img_width=200):
    # Sort lines based on the starting Y value
    horizontal_lines.sort(key=lambda line: line[0][1])

    # Smallest y-gap between each horizontal_line
    smallest_gap = smallest_gap_between_horizontal_lines(horizontal_lines)
    
    filled_lines = []

    # Fill gaps with new lines and extend existing lines
    for i in range(len(horizontal_lines) - 1):
        x1, y1, x2, y2 = horizontal_lines[i][0]
        
        x1 = 0
        x2 = img_width
        
        _x1, _y1, _x2, _y2 = horizontal_lines[i + 1][0]
        
        gap = abs((y1 + y2) / 2 - (_y1 + _y2) / 2)
        
        lines_between = gap / smallest_gap
        if lines_between > 1:
            step_size = gap / floor(lines_between)
            new_y1 = y1 + step_size
            new_y2 = y2 + step_size
            for _ in range(int(lines_between)):
                new_line = x1, int(new_y1), x2, int(new_y2)
                
                print("new_line", new_line)
                filled_lines.append([new_line])
                y1 = int(new_y1)
                y2 = int(new_y2)
                new_y1 += step_size
                new_y2 += step_size
        
        # fill the line itself 
        filled_lines.append([[x1, y1, x2, y2]])

    filled_lines.append(horizontal_lines[-1])  # Append the last line

    return filled_lines


def fill_vertical_lines(vertical_lines, img_height):
    # Sort lines based on the starting Y value
    vertical_lines.sort(key=lambda line: line[0][0])

    # Smallest y-gap between each horizontal_line
    smallest_gap = smallest_gap_between_vertical_lines(vertical_lines)
    
    filled_lines = []

    # Fill gaps with new lines and extend existing lines
    for i in range(len(vertical_lines) - 1):
        x1, y1, x2, y2 = vertical_lines[i][0]
        y1 = 0
        y2 = img_height
        _x1, _y1, _x2, _y2 = vertical_lines[i + 1][0]
        gap = abs((x1 + x2) / 2 - (_x1 + _x2) / 2)
        lines_between = gap / smallest_gap
        if lines_between > 1:
            step_size = gap / floor(lines_between)
            new_x1 = x1 + step_size
            new_x2 = x2 + step_size
            for _ in range(int(lines_between)):
                new_line = int(new_x1), y1, int(new_x2), y2
                
                filled_lines.append([new_line])
                x1 = int(new_x1)
                x2 = int(new_x2)
                new_x1 += step_size
                new_x2 += step_size
        
        # fill the line itself 
        filled_lines.append([[x1, y1, x2, y2]])

    filled_lines.append(vertical_lines[-1])  # Append the last line

    return filled_lines

def order_horizontal_lines_by_y(horizontal_lines):
    return sorted(horizontal_lines, key=lambda line: line[0][1])

def smallest_gap_between_horizontal_lines(horizontal_lines):
    smallest = 100
    for i in range(len(horizontal_lines)):
        for j in range(i + 1, len(horizontal_lines)):
            x1, y1, x2, y2 = horizontal_lines[i][0]
            _x1, _y1, _x2, _y2 = horizontal_lines[j][0]
            gap = abs((y1+y2)/2 - (_y1+_y2)/2)
            if gap < smallest:
                smallest = gap
    return smallest

def smallest_gap_between_vertical_lines(vertical_lines):
    smallest = 100
    for i in range(len(vertical_lines)):
        for j in range(i + 1, len(vertical_lines)):
            x1, y1, x2, y2 = vertical_lines[i][0]
            _x1, _y1, _x2, _y2 = vertical_lines[j][0]
            gap = abs((x1+x2)/2 - (_x1+_x2)/2)
            if gap < smallest:
                smallest = gap
    return smallest

def create_rectangles(intersection_points):
    rectangles = []

    # Order intersection points by Y value first, then by X value
    ordered_points = sorted(intersection_points, key=lambda point: (point[1], point[0]))

    for i in range(0, len(ordered_points), 2):
        if i + 1 < len(ordered_points):
            tl = ordered_points[i],       # top-left
            tr = ordered_points[i + 1],   # top-right
            bl = find_closest_lower_y(ordered_points, ordered_points[i]),  # bottom-left
            br = find_closest_lower_y(ordered_points, ordered_points[i + 1]),  # bottom-right
            print("points", tl, tr, bl, br)
            if bl[0] is None or br[0] is None:
                print("bl or br is None")
                continue
            rectangle = np.array([[
                tl,
                tr,
                br,
                bl,
            ]], np.int32)
            print("rectangle", rectangle)
            rectangle = rectangle.reshape((-1, 1, 2))
            rectangles.append(rectangle)
    return rectangles

def find_right_neighbor(points, point):
    closest = None
    for p in points:
        if p[0] > point[0]:
            if closest is None:
                closest = p
            elif p[0] < closest[0]:
                if abs(p[1] - point[1]) < abs(closest[1] - point[1]):
                    closest = p
    return closest

def find_down_neighbor(points, point):
    closest = None
    for p in points:
        if p[1] > point[1]:
            if closest is None:
                closest = p
            elif p[1] < closest[1]:
                if abs(p[0] - point[0]) < abs(closest[0] - point[0]):
                    closest = p
    return closest

def find_closest_lower_y(points, point):
    closest = None
    for p in points:
        if p[1] > point[1]:
            if closest is None:
                closest = p
            elif p[1] < closest[1]:
                if abs(p[0] - point[0]) < abs(closest[0] - point[0]):
                    closest = p
    return closest