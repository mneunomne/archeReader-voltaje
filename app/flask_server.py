from flask import Flask, render_template, Response
# from flask_socketio import SocketIO, send, emit
from image_processing import ImageProcessor
import numpy as np
import cv2
from globals import SEGMENT_OUTPUT_WIDTH, SEGMENT_OUTPUT_HEIGHT, FLASK_SERVER_IP, FLASK_SERVER_PORT

app = Flask(__name__, static_url_path='', static_folder='static', template_folder='static')

app.config['SECRET_KEY'] = 'secret!'
# socketio = SocketIO(app)

video_output = None
cropped_output = None

# make cropped image blank with SEGMENT_OUTPUT_WIDTH and SEGMENT_OUTPUT_HEIGHT with 3 channels using opencv / np
# cropped_output = np.zeros((SEGMENT_OUTPUT_HEIGHT, SEGMENT_OUTPUT_WIDTH, 3), np.uint8)
# video_output = np.zeros((SEGMENT_OUTPUT_HEIGHT, SEGMENT_OUTPUT_WIDTH, 3), np.uint8)

current_segment_index = 0

imageProcessor = ImageProcessor()

def sendVideoOutput(frame):
    global video_output
    video_output = frame

def sendCroppedOutput(frame):
    global cropped_output
    cropped_output = frame

def gen_frames():  # generate frame by frame from camera
    global video_output
    # Capture frame-by-frame
    if video_output is None:
        return
    else:
        frame = video_output.copy()
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

def gen_cropped():  # generate frame by frame from camera
    global cropped_output
    # Capture frame-by-frame
    if cropped_output is None:
        return
    else:
        frame = cropped_output.copy()
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

def getState():
    global ready_to_read
    return ready_to_read

@app.route('/video_feed')
def video_feed():
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/cropped_image')
def cropped_image():
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_cropped(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/movement_end/<int:direction>')
def on_movement_end(direction):
    global ready_to_read
    ready_to_read = True
    print('movement end', direction)
    return Response('done', mimetype='text/plain')

@app.route('/test/<string:json>', methods=['GET', 'POST'])
def test(json):
    global video_output
    print('video_output', video_output)
    if video_output is None:
        print('cropped_output is None')
        return Response('fail', mimetype='text/plain')
    else:
        imageProcessor.process_image(video_output)
    ready_to_read = True
    print('received test', json)
    return Response('done', mimetype='text/plain')

@app.route('/on_segment/<int:segmentIndex>', methods=['GET', 'POST'])
def on_segment(segmentIndex):
    print('received segmentIndex', segmentIndex)
    global video_output
    if video_output is None:
        print('cropped_output is None')
        return Response('fail', mimetype='text/plain')
    else:
        imageProcessor.clear_stored_markers()
        is_valid = False
        attempts = 0
        while not is_valid and attempts < 1000:
            is_valid, msg = imageProcessor.process_image(video_output, segmentIndex)
            # print('is_valid', is_valid)
            if is_valid: 
                attempts = 1000
        if is_valid:
            print('is_valid', is_valid)
            return Response(msg, mimetype='text/plain')
        else:
            print('not valid', is_valid)
            return Response('fail', mimetype='text/plain')

@app.route('/clear', methods=['GET', 'POST'])
def on_clear():
    imageProcessor.clear()
    return Response('ok', mimetype='text/plain')

@app.route('/cropped_feed')
def cropped_feed():
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_cropped(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')

@app.route('/dates')
def dates():
    """Video streaming home page."""
    return render_template('dates.html')