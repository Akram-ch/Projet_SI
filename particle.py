from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import random

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-0.1, 0.1)
        self.vy = random.uniform(0.1, 0.5)
        self.lifetime = 100