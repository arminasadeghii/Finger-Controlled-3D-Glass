# Finger-Controlled 3D Glass

A small computer vision and 3D graphics project I made just for fun.

The idea is pretty simple: use your hand in front of a webcam to control a 3D glass in real time. You can rotate the glass with your index finger, fill it using a pinch gesture, and pour the liquid by tilting the glass.

This started as a small experiment with hand tracking, OpenGL, and real-time interaction. I mostly wanted to see what I could build by combining these things into one silly but interactive project.

## Features

* Real-time hand tracking using MediaPipe
* Control the glass rotation using the index finger
* Pinch gesture detection for filling the glass
* Tilt-based liquid pouring
* Open-hand gesture for resetting the glass
* Real-time webcam feed with hand landmarks
* 3D glass rendering using OpenGL
* Dynamic liquid level
* Rotation smoothing to make hand movement feel less jittery
* Keyboard controls for adjusting the interaction

## Controls

| Input                      | Action                  |
| -------------------------- | ----------------------- |
| Move index finger          | Rotate the glass        |
| Pinch thumb + index finger | Fill the glass          |
| Tilt the glass             | Pour the liquid         |
| Open hand                  | Reset the glass         |
| `R`                        | Recenter rotation       |
| `↑`                        | Increase responsiveness |
| `↓`                        | Increase smoothing      |
| `ESC`                      | Exit                    |

## Technologies

* Python
* MediaPipe
* OpenCV
* PyOpenGL
* Pygame
* NumPy

## How It Works

The webcam captures the user's hand and MediaPipe detects its landmarks in real time.

The project uses the position of the index finger to calculate its angle. That angle is then converted into the rotation of the 3D glass.

Since hand tracking can be a little noisy, the detected rotation is smoothed before it is applied to the 3D scene. This makes the glass movement feel more natural.

The project also detects a few simple gestures to control the liquid.

### Pinch Detection

When the thumb and index finger get close to each other, the project detects a pinch gesture.

The pinch is used to start filling the glass.

```text
Thumb + Index
      ↓
   Pinch detected
      ↓
    Fill glass
```

### Pouring

When the glass is tilted beyond a certain angle, the liquid starts pouring out.

The liquid level decreases based on the amount of tilt, so tilting the glass further makes the liquid pour faster.

```text
Upright
   |
   |
   |       Tilt
   |        /
   |       /
   |      /   → Liquid pours
```

### Reset

Opening the hand triggers the reset behavior and brings the glass back toward its initial state.

## Project Structure

```text
finger-controlled-3d-glass/
│
├── main.py
├── cup_geometry.py
├── hand_tracker.py
├── requirements.txt
├── README.md
│
└── models/
    └── hand_landmarker.task
```

### `main.py`

The main application. It handles the webcam, rendering loop, keyboard input, gesture interaction, glass rotation, and liquid simulation.

### `hand_tracker.py`

Contains the hand-tracking logic using MediaPipe. It detects the hand landmarks and calculates the information needed for the gestures and rotation.

### `cup_geometry.py`

Contains the geometry of the 3D glass and the logic related to the liquid inside it.

### `requirements.txt`

Contains the Python packages required to run the project.



## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/finger-controlled-3d-glass.git
cd finger-controlled-3d-glass
```

Create a virtual environment:

```bash
python -m venv venv
```

On Windows:

```bash
venv\Scripts\activate
```

On macOS/Linux:

```bash
source venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

## Running the Project

Make sure your webcam is connected and run:

```bash
python main.py
```

The application will open a window containing the webcam feed and the 3D scene.

Put your hand in front of the camera and move your index finger to start controlling the glass.

## Customization

The glass geometry can be customized in the source code.

For example:

```python
cup = PentagonCup(
    height=2.0,
    outer_radius=1.0,
    wall_ratio=0.82,
    base_thickness=0.18
)
```

The rendering parameters can also be changed to adjust the appearance of the glass and liquid.

For example:

```python
BEIGE_DIFFUSE = (0.86, 0.76, 0.58)
GLASS_ALPHA = 0.38

WHISKEY_DIFFUSE = (0.72, 0.40, 0.10)
WHISKEY_ALPHA = 0.78
```

## Smoothing

The hand rotation is smoothed to reduce small movements and tracking noise.

The tracker can be configured with parameters such as:

```python
IndexFingerRotationTracker(
    smoothing=0.35,
    max_hands=1,
    detection_conf=0.6,
    tracking_conf=0.6
)
```

You can also adjust the smoothing while the application is running using the arrow keys.

## Why I Made This

There isn't really a serious reason behind this project.

I was experimenting with hand tracking and 3D graphics and thought it would be funny to control a glass with my hand.

So I built it.

The main goal was simply to have fun and see how far I could take a small idea using a webcam, MediaPipe, and OpenGL.

It is not meant to be a serious simulation or a production-ready application. It is just a little experiment that turned into something more interactive than I initially expected.

## Possible Improvements

There are still plenty of things that could be improved if I decide to continue working on it:

* More realistic glass transparency
* Better lighting and reflections
* More realistic liquid physics
* Improved pouring animation
* More accurate gesture detection
* Two-hand interaction
* Different types of glasses
* Better shaders
* Sound effects
* More interactive objects

## License

This project was made for fun and experimentation.

Feel free to use or modify the code for your own experiments.

## Author

Made for fun with Python, MediaPipe, OpenCV, PyOpenGL, and Pygame.
