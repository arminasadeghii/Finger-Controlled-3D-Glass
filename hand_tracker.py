import math
import os
import shutil
import ssl
import time
import urllib.request

import numpy as np
import mediapipe as mp
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import (
    HandLandmarker,
    HandLandmarkerOptions,
    RunningMode,
)
from mediapipe.tasks.python.vision import hand_landmarker as hl

MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/1/hand_landmarker.task"
)
MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
MODEL_PATH = os.path.join(MODEL_DIR, "hand_landmarker.task")

INDEX_MCP = hl.HandLandmark.INDEX_FINGER_MCP
INDEX_TIP = hl.HandLandmark.INDEX_FINGER_TIP
HAND_CONNECTIONS = hl.HandLandmarksConnections.HAND_CONNECTIONS

THUMB_TIP = hl.HandLandmark.THUMB_TIP
WRIST = hl.HandLandmark.WRIST

FINGER_TIP_PIP_PAIRS = [
    (hl.HandLandmark.INDEX_FINGER_TIP, hl.HandLandmark.INDEX_FINGER_PIP),
    (hl.HandLandmark.MIDDLE_FINGER_TIP, hl.HandLandmark.MIDDLE_FINGER_PIP),
    (hl.HandLandmark.RING_FINGER_TIP, hl.HandLandmark.RING_FINGER_PIP),
    (hl.HandLandmark.PINKY_TIP, hl.HandLandmark.PINKY_PIP),
]
THUMB_TIP_MCP = (hl.HandLandmark.THUMB_TIP, hl.HandLandmark.THUMB_MCP)


PINCH_ON_THRESHOLD = 0.055
PINCH_OFF_THRESHOLD = 0.09  


def _build_ssl_contexts():
   
    contexts = [("system default", ssl.create_default_context())]

    try:
        import certifi
        contexts.append(("certifi bundle", ssl.create_default_context(cafile=certifi.where())))
    except ImportError:
        pass

    unverified = ssl._create_unverified_context()
    contexts.append(("UNVERIFIED (certificate checking disabled)", unverified))

    return contexts


def ensure_model_downloaded():
    if os.path.exists(MODEL_PATH):
        return MODEL_PATH
    os.makedirs(MODEL_DIR, exist_ok=True)

    tmp_path = MODEL_PATH + ".part"
    last_error = None

    for label, ctx in _build_ssl_contexts():
        try:
            print(f"Downloading hand landmark model ({label}) to {MODEL_PATH} ...")
            if "UNVERIFIED" in label:
                print("  WARNING: skipping certificate verification for this download. "
                      "This is a last-resort fallback — see the README for how to fix "
                      "your Python/OS certificate setup properly.")
            with urllib.request.urlopen(MODEL_URL, context=ctx, timeout=30) as resp, \
                    open(tmp_path, "wb") as f:
                shutil.copyfileobj(resp, f)
            os.replace(tmp_path, MODEL_PATH)
            print("Download complete.")
            return MODEL_PATH
        except Exception as e:  
            last_error = e
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            continue

    raise RuntimeError(
        f"error: {last_error}\n\n"
        "Fix options:\n"
        "  1. (macOS python.org installs) Run the 'Install Certificates.command' "
        "file in your Python's Applications folder.\n"
        "  2. Run: pip install --upgrade certifi\n"
        "  3. Manually download the model and place it at:\n"
        f"       {MODEL_PATH}\n"
        f"     from:\n       {MODEL_URL}\n"
    )


class IndexFingerRotationTracker:
    def __init__(self, smoothing=0.35, max_hands=1,
                 detection_conf=0.6, tracking_conf=0.6):
  
        model_path = ensure_model_downloaded()

        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=RunningMode.VIDEO,
            num_hands=max_hands,
            min_hand_detection_confidence=detection_conf,
            min_tracking_confidence=tracking_conf,
        )
        self.landmarker = HandLandmarker.create_from_options(options)
        self._start_time = time.time()

        self.smoothing = smoothing
        self._smoothed_sin = 0.0
        self._smoothed_cos = 1.0

        self.last_hand_landmarks = None 
        self.last_angle = 0.0            
        self.hand_present = False

       
        self.pinch_detected = False      
        self.open_hand_detected = False  
        self._pinch_active = False       

    def _timestamp_ms(self):
        return int((time.time() - self._start_time) * 1000)

    def process(self, frame_bgr):
        rgb = frame_bgr[:, :, ::-1]
        rgb = np.ascontiguousarray(rgb)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        result = self.landmarker.detect_for_video(mp_image, self._timestamp_ms())

        self.hand_present = False
        self.last_hand_landmarks = None

        if result.hand_landmarks:
            landmarks = result.hand_landmarks[0]
            self.last_hand_landmarks = landmarks
            self.hand_present = True

            mcp = landmarks[INDEX_MCP]
            tip = landmarks[INDEX_TIP]

            dx = tip.x - mcp.x
            dy = -(tip.y - mcp.y)

            raw_angle = math.atan2(dy, dx)
            self._integrate_angle(raw_angle)

            self._update_gestures(landmarks)
        else:
            
            self.pinch_detected = False
            self.open_hand_detected = False
            self._pinch_active = False

        return self.last_angle

    def _landmark_dist(self, landmarks, idx_a, idx_b):
        a, b = landmarks[idx_a], landmarks[idx_b]
        return math.hypot(a.x - b.x, a.y - b.y)

    def _update_gestures(self, landmarks):
        """Populate self.pinch_detected and self.open_hand_detected from landmarks."""
        wrist = landmarks[WRIST]

       
        middle_mcp = landmarks[hl.HandLandmark.MIDDLE_FINGER_MCP]
        hand_scale = math.hypot(middle_mcp.x - wrist.x, middle_mcp.y - wrist.y) or 1.0


        pinch_dist = self._landmark_dist(landmarks, THUMB_TIP, INDEX_TIP) / hand_scale
        if not self._pinch_active and pinch_dist < PINCH_ON_THRESHOLD:
            self._pinch_active = True
        elif self._pinch_active and pinch_dist > PINCH_OFF_THRESHOLD:
            self._pinch_active = False
        self.pinch_detected = self._pinch_active

        extended_count = 0
        for tip_idx, pip_idx in FINGER_TIP_PIP_PAIRS:
            tip_to_wrist = self._landmark_dist(landmarks, tip_idx, WRIST)
            pip_to_wrist = self._landmark_dist(landmarks, pip_idx, WRIST)
            if tip_to_wrist > pip_to_wrist * 1.15:
                extended_count += 1

        thumb_tip_idx, thumb_mcp_idx = THUMB_TIP_MCP
        thumb_spread = self._landmark_dist(landmarks, thumb_tip_idx, hl.HandLandmark.INDEX_FINGER_MCP) / hand_scale
        thumb_extended = thumb_spread > 0.6

        self.open_hand_detected = (extended_count == 4) and thumb_extended

    def _integrate_angle(self, raw_angle):
        """Exponential smoothing on the unit circle to avoid -pi/pi wraparound pops."""
        s, c = math.sin(raw_angle), math.cos(raw_angle)
        a = self.smoothing
        self._smoothed_sin = (1 - a) * self._smoothed_sin + a * s
        self._smoothed_cos = (1 - a) * self._smoothed_cos + a * c
        self.last_angle = math.atan2(self._smoothed_sin, self._smoothed_cos)

    def draw_overlay(self, frame_bgr):
        """Draw the hand skeleton + index finger direction line onto the frame in-place."""
        if self.last_hand_landmarks is None:
            return frame_bgr

        from mediapipe.tasks.python.vision import drawing_utils, drawing_styles

        drawing_utils.draw_landmarks(
            frame_bgr,
            self.last_hand_landmarks,
            HAND_CONNECTIONS,
            drawing_styles.get_default_hand_landmarks_style(),
            drawing_styles.get_default_hand_connections_style(),
        )
        return frame_bgr

    def close(self):
        self.landmarker.close()
