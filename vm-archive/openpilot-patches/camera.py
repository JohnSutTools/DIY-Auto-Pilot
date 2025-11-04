import av
import cv2 as cv

class Camera:
  def __init__(self, cam_type_state, stream_type, camera_id):
    try:
      camera_id = int(camera_id)
    except ValueError: # allow strings, ex: /dev/video0
      pass
    self.cam_type_state = cam_type_state
    self.stream_type = stream_type
    self.cur_frame_id = 0

    print(f"Opening {cam_type_state} at {camera_id}")

    # Use V4L2 backend for Linux webcams (more reliable)
    self.cap = cv.VideoCapture(camera_id, cv.CAP_V4L2)
    
    # Set MJPEG format (works best with USB webcams)
    self.cap.set(cv.CAP_PROP_FOURCC, cv.VideoWriter_fourcc('M','J','P','G'))
    self.cap.set(cv.CAP_PROP_FRAME_WIDTH, 1280.0)
    self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, 720.0)
    self.cap.set(cv.CAP_PROP_FPS, 25.0)

    self.W = self.cap.get(cv.CAP_PROP_FRAME_WIDTH)
    self.H = self.cap.get(cv.CAP_PROP_FRAME_HEIGHT)
    
    # Verify camera opened successfully
    if not self.cap.isOpened():
      raise RuntimeError(f"Failed to open camera at {camera_id}")
    
    print(f"Camera initialized: {self.W}x{self.H}")

  @classmethod
  def bgr2nv12(self, bgr):
    frame = av.VideoFrame.from_ndarray(bgr, format='bgr24')
    return frame.reformat(format='nv12').to_ndarray()

  def read_frames(self):
    frame_count = 0
    while True:
      ret, frame = self.cap.read()
      if not ret or frame is None:
        print(f"Failed to read frame {frame_count}, retrying...")
        continue
      
      # Rotate the frame 180 degrees (flip both axes)
      frame = cv.flip(frame, -1)
      
      try:
        yuv = Camera.bgr2nv12(frame)
        yield yuv.data.tobytes()
        frame_count += 1
      except Exception as e:
        print(f"Error converting frame {frame_count}: {e}")
        continue
    self.cap.release()
