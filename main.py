import sys
import math

import cv2
import numpy as np
import pygame
from pygame.locals import DOUBLEBUF, OPENGL, QUIT, KEYDOWN, K_ESCAPE, K_r, K_UP, K_DOWN
from OpenGL.GL import *
from OpenGL.GLU import *

from cup_geometry import PentagonCup, LiquidState
from hand_tracker import IndexFingerRotationTracker


WINDOW_W, WINDOW_H = 1280, 720
CAM_W, CAM_H = 640, 480

BEIGE_DIFFUSE = (0.86, 0.76, 0.58)  
BEIGE_AMBIENT = (0.30, 0.26, 0.20)
GLASS_ALPHA = 0.38                   
RIM_ALPHA = 0.55                      
WHISKEY_DIFFUSE = (0.72, 0.40, 0.10)  
WHISKEY_ALPHA = 0.78                 
STREAM_DIFFUSE = (0.75, 0.43, 0.12)
STREAM_ALPHA = 0.85

BACKGROUND_COLOR = (0.07, 0.07, 0.08, 1.0)



def create_empty_texture(width, height):
    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    blank = np.zeros((height, width, 3), dtype=np.uint8)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, blank)
    glBindTexture(GL_TEXTURE_2D, 0)
    return tex_id


def update_texture(tex_id, rgb_frame):
    """rgb_frame: HxWx3 uint8, already flipped so row 0 = bottom of image (OpenGL convention)."""
    glBindTexture(GL_TEXTURE_2D, tex_id)
    h, w = rgb_frame.shape[:2]
    glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, w, h, GL_RGB, GL_UNSIGNED_BYTE, rgb_frame)
    glBindTexture(GL_TEXTURE_2D, 0)


def draw_textured_quad(tex_id, x0, y0, x1, y1):
    """Draw a textured quad in the current (already-set-up) ortho projection."""
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glColor4f(1, 1, 1, 1)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex2f(x0, y0)
    glTexCoord2f(1, 0); glVertex2f(x1, y0)
    glTexCoord2f(1, 1); glVertex2f(x1, y1)
    glTexCoord2f(0, 1); glVertex2f(x0, y1)
    glEnd()
    glBindTexture(GL_TEXTURE_2D, 0)
    glDisable(GL_TEXTURE_2D)



class TextHUD:
    def __init__(self, font_size=22):
        pygame.font.init()
        self.font = pygame.font.SysFont("Consolas,Menlo,DejaVu Sans Mono", font_size)
        self.tex_id = glGenTextures(1)

    def draw(self, text, x, y, color=(235, 225, 205)):
        surface = self.font.render(text, True, color)
        surface = pygame.transform.flip(surface, False, True)
        w, h = surface.get_size()
        data = pygame.image.tostring(surface, "RGBA", True)

        glBindTexture(GL_TEXTURE_2D, self.tex_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)

        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(1, 1, 1, 1)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2f(x, y)
        glTexCoord2f(1, 0); glVertex2f(x + w, y)
        glTexCoord2f(1, 1); glVertex2f(x + w, y + h)
        glTexCoord2f(0, 1); glVertex2f(x, y + h)
        glEnd()
        glBindTexture(GL_TEXTURE_2D, 0)
        glDisable(GL_TEXTURE_2D)



def draw_cup(cup: PentagonCup, angle_rad: float, fill_fraction: float = 0.0):
    glPushMatrix()
    glRotatef(math.degrees(angle_rad), 0, 0, 1)
    glRotatef(18, 1, 0, 0) 

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 96.0)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDepthMask(GL_FALSE)  
    glDisable(GL_CULL_FACE)


    if fill_fraction > 0.0:
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0.9, 0.7, 0.4, 1.0))
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 48.0)

        liquid_faces = cup.liquid_wall_faces(fill_fraction)
        for face in liquid_faces:
            glNormal3f(0, 0, 1)  
            glColor4f(WHISKEY_DIFFUSE[0], WHISKEY_DIFFUSE[1], WHISKEY_DIFFUSE[2], WHISKEY_ALPHA)
            glBegin(GL_QUADS if len(face) == 4 else GL_TRIANGLES)
            for v in face:
                glVertex3f(*v)
            glEnd()

        
        surface = cup.liquid_surface_polygon(fill_fraction)
        glNormal3f(0, 1, 0)
        glColor4f(WHISKEY_DIFFUSE[0] * 1.1, WHISKEY_DIFFUSE[1] * 1.1, WHISKEY_DIFFUSE[2] * 1.1, WHISKEY_ALPHA)
        glBegin(GL_POLYGON)
        for v in surface:
            glVertex3f(*v)
        glEnd()

        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 96.0)

    for face, normal in cup.iter_faces_with_normals():
        glNormal3f(*normal)
        glColor4f(BEIGE_DIFFUSE[0], BEIGE_DIFFUSE[1], BEIGE_DIFFUSE[2], GLASS_ALPHA)
        if len(face) == 3:
            glBegin(GL_TRIANGLES)
        else:
            glBegin(GL_QUADS)
        for v in face:
            glVertex3f(*v)
        glEnd()


    glDepthMask(GL_TRUE)
    glDisable(GL_LIGHTING)
    glLineWidth(2.0)
    glColor4f(1.0, 0.96, 0.86, RIM_ALPHA)
    glBegin(GL_LINE_LOOP)
    for v in cup.outer_top:
        glVertex3f(*v)
    glEnd()
    glBegin(GL_LINE_LOOP)
    for v in cup.inner_top:
        glVertex3f(*v)
    glEnd()

    glDepthMask(GL_TRUE)
    glDisable(GL_BLEND)
    glPopMatrix()


def draw_pour_stream(cup: PentagonCup, angle_rad: float, fill_fraction: float, tilt_sign: float):
    if fill_fraction <= 0.0:
        return

    glPushMatrix()
    glRotatef(math.degrees(angle_rad), 0, 0, 1)
    glRotatef(18, 1, 0, 0)

    glDisable(GL_LIGHTING)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDepthMask(GL_FALSE)

    
    rim = cup.outer_top
    n = len(rim)
    idx = 0
    best_x = -1e9 if tilt_sign > 0 else 1e9
    for i, (x, y, z) in enumerate(rim):
        if (tilt_sign > 0 and x > best_x) or (tilt_sign < 0 and x < best_x):
            best_x = x
            idx = i
    ex, ey, ez = rim[idx]

    glColor4f(STREAM_DIFFUSE[0], STREAM_DIFFUSE[1], STREAM_DIFFUSE[2], STREAM_ALPHA)
    glLineWidth(4.0)
    glBegin(GL_LINES)
    glVertex3f(ex, ey, ez)
    glVertex3f(ex, ey - 2.3, ez)  
    glEnd()

    glDepthMask(GL_TRUE)
    glDisable(GL_BLEND)
    glPopMatrix()


def draw_ground_grid(size=4.0, step=0.5, y=-1.15):
    glDisable(GL_LIGHTING)
    glColor4f(0.25, 0.24, 0.22, 0.5)
    glLineWidth(1.0)
    glBegin(GL_LINES)
    n = int(size / step)
    for i in range(-n, n + 1):
        glVertex3f(i * step, y, -size)
        glVertex3f(i * step, y, size)
        glVertex3f(-size, y, i * step)
        glVertex3f(size, y, i * step)
    glEnd()


def setup_lighting():
    glLightfv(GL_LIGHT0, GL_POSITION, (2.0, 3.0, 4.0, 1.0))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.35, 0.33, 0.30, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.95, 0.9, 0.8, 1.0))
    glLightfv(GL_LIGHT0, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))



def main():
    pygame.init()
    pygame.display.set_caption("Index Finger -> Rotating Pentagonal Glass Cup")
    pygame.display.set_mode((WINDOW_W, WINDOW_H), DOUBLEBUF | OPENGL)
    clock = pygame.time.Clock()

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_W)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_H)
    if not cap.isOpened():
        print("ERROR: could not open webcam (index 0). Check camera permissions/index.")
        sys.exit(1)

    tracker = IndexFingerRotationTracker(smoothing=0.35)
    cup = PentagonCup(height=2.0, outer_radius=1.0, wall_ratio=0.82, base_thickness=0.18)
    liquid = LiquidState()
    cam_tex = create_empty_texture(CAM_W, CAM_H)
    hud = TextHUD()

    
    display_angle = 0.0
    RESET_LERP_RATE = 4.0 

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_NORMALIZE)

    running = True
    while running:
        dt = clock.tick(60) / 1000.0  

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                elif event.key == K_r:
                    tracker._smoothed_sin, tracker._smoothed_cos = 0.0, 1.0
                elif event.key == K_UP:
                    tracker.smoothing = min(1.0, tracker.smoothing + 0.05)
                elif event.key == K_DOWN:
                    tracker.smoothing = max(0.02, tracker.smoothing - 0.05)

        ok, frame = cap.read()
        if not ok:
            continue
        frame = cv2.flip(frame, 1)  
        frame = cv2.resize(frame, (CAM_W, CAM_H))

        angle = tracker.process(frame)
        tracker.draw_overlay(frame)  

       
        liquid.fill(tracker.pinch_detected, dt)

       
        if tracker.open_hand_detected:
            blend = 1.0 - math.exp(-RESET_LERP_RATE * dt)
            display_angle += (0.0 - display_angle) * blend
        else:
            display_angle = angle

        
        liquid.update_pour(display_angle, dt)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb = np.flipud(rgb)  
        rgb = np.ascontiguousarray(rgb)
        update_texture(cam_tex, rgb)

        glClearColor(*BACKGROUND_COLOR)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        
        glViewport(0, WINDOW_H // 8, WINDOW_W // 2, WINDOW_H - WINDOW_H // 8)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, 1, 0, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)
        draw_textured_quad(cam_tex, 0, 0, 1, 1)
        glEnable(GL_DEPTH_TEST)

        
        glViewport(WINDOW_W // 2, WINDOW_H // 8, WINDOW_W // 2, WINDOW_H - WINDOW_H // 8)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (WINDOW_W / 2) / (WINDOW_H - WINDOW_H // 8), 0.1, 50.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(0, 0.6, 4.2, 0, 0, 0, 0, 1, 0)
        setup_lighting()
        glClear(GL_DEPTH_BUFFER_BIT)
        draw_ground_grid()
        draw_cup(cup, display_angle, liquid.level)
        if liquid.pouring:
            tilt_sign = 1.0 if display_angle >= 0 else -1.0
            draw_pour_stream(cup, display_angle, liquid.level, tilt_sign)

        glViewport(0, 0, WINDOW_W, WINDOW_H)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, WINDOW_W, 0, WINDOW_H)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)

        deg = (math.degrees(display_angle)) % 360
        status = "HAND DETECTED" if tracker.hand_present else "no hand in frame"
        gesture = ""
        if tracker.pinch_detected:
            gesture = "   PINCH: filling"
        elif tracker.open_hand_detected:
            gesture = "   OPEN HAND: resetting"
        elif liquid.pouring:
            gesture = "   POURING"
        hud.draw(f"rotation: {deg:6.1f}°   fill: {liquid.level*100:5.1f}%   {status}{gesture}", 24, 44)
        hud.draw("pinch (thumb+index) to fill  |  tilt to pour  |  open hand to reset  |  "
                 "R: recenter   UP/DOWN: smoothing   ESC: quit", 24, 16)
        glEnable(GL_DEPTH_TEST)

        pygame.display.flip()

    tracker.close()
    cap.release()
    pygame.quit()


if __name__ == "__main__":
    main()
