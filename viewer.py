#!/usr/bin/env python3
import sys
from itertools import cycle
import OpenGL.GL as GL              # standard Python OpenGL wrapper
import OpenGL.GLUT as glut
import PIL.Image as Image
import glfw                         # lean window system wrapper for OpenGL
import numpy as np                  # all matrix manipulations & OpenGL args
from core import Shader, Viewer, Mesh, Node, load
from transform import *
from texture import Texture, Textured
from texture import *
from animation import *


# -------------- Example textured plane class ---------------------------------
class TexturedPlane(Textured):
    """ Simple first textured object """
    def __init__(self, shader, tex_file):
        # prepare texture modes cycling variables for interactive toggling
        self.wraps = cycle([GL.GL_REPEAT, GL.GL_MIRRORED_REPEAT,
                            GL.GL_CLAMP_TO_BORDER, GL.GL_CLAMP_TO_EDGE])
        self.filters = cycle([(GL.GL_NEAREST, GL.GL_NEAREST),
                              (GL.GL_LINEAR, GL.GL_LINEAR),
                              (GL.GL_LINEAR, GL.GL_LINEAR_MIPMAP_LINEAR)])
        self.wrap, self.filter = next(self.wraps), next(self.filters)
        self.file = tex_file

        # setup plane mesh to be textured
        base_coords = ((-1, -1, 0), (1, -1, 0), (1, 1, 0), (-1, 1, 0))
        scaled = 100 * np.array(base_coords, np.float32)
        indices = np.array((0, 1, 2, 0, 2, 3), np.uint32)
        mesh = Mesh(shader, attributes=dict(position=scaled), index=indices)

        # setup & upload texture to GPU, bind it to shader name 'diffuse_map'
        texture = Texture(tex_file, self.wrap, *self.filter)
        super().__init__(mesh, diffuse_map=texture)

    def key_handler(self, key):
        # cycle through texture modes on keypress of F6 (wrap) or F7 (filtering)
        self.wrap = next(self.wraps) if key == glfw.KEY_F6 else self.wrap
        self.filter = next(self.filters) if key == glfw.KEY_F7 else self.filter
        if key in (glfw.KEY_F6, glfw.KEY_F7):
            texture = Texture(self.file, self.wrap, *self.filter)
            self.textures.update(diffuse_map=texture)






class Terrain(Node):
    def __init__(self, shader, light_dir):
        super().__init__()
        self.add(*load('terrain/terobj.obj', shader, light_dir=light_dir))

class Volcano(Node):
    def __init__(self, shader, light_dir):
        super().__init__()
        self.add(*load('volcano-3d-model/Volcano.obj', shader, light_dir=light_dir))
        


class Player(Node):
    def __init__(self, shader, light_dir):
        super().__init__()
        self.add(*load('cat.obj', shader, light_dir=light_dir))
    def key_handler(self, key):
        if key==glfw.KEY_D:
            self.transform = self.transform @ translate(.5, 0, 0)
        elif key==glfw.KEY_A :
            self.transform = self.transform @ translate(-.5, 0, 0)
        elif key==glfw.KEY_Z :
            self.transform = self.transform @ translate (0, .5, 0)
        elif key==glfw.KEY_S: 
            self.transform = self.transform @ translate (0, -.5, 0)
        elif key==glfw.KEY_DOWN :
            self.transform = self.transform @ rotate(axis=(1,0,0), angle=5)
        elif key==glfw.KEY_UP :
            self.transform = self.transform @ rotate(axis=(1,0,0), angle=-5)

        else:
            self.transform=self.transform
        

class Cylinder(Node):
    """ Very simple cylinder based on provided load function """
    def __init__(self, shader, light_dir):
        super().__init__()
        self.add(*load('cylinder.obj', shader, light_dir=light_dir))  # just load cylinder from file

class Monkey(Node):
    def __init__(self, shader, light_dir):
        super().__init__()
        self.add(*load('suzanne.obj', shader=shader, light_dir=light_dir))
    
class Skybox(CubeMapTextured):
    """ True skybox that is perceived at infinity """

    def __init__(self, shader, tex_files):
        self.wraps = cycle([GL.GL_REPEAT, GL.GL_MIRRORED_REPEAT,
                            GL.GL_CLAMP_TO_BORDER, GL.GL_CLAMP_TO_EDGE])
        self.filters = cycle([(GL.GL_NEAREST, GL.GL_NEAREST),
                              (GL.GL_LINEAR, GL.GL_LINEAR),
                              (GL.GL_LINEAR, GL.GL_LINEAR_MIPMAP_LINEAR)])
        self.wrap, self.filter = next(self.wraps), next(self.filters)
        self.files = tex_files
        base_coords_face1 = ((-1, 1, -1), (-1, -1, -1), (1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1))
        base_coords_face2 = ((-1, -1, 1), (-1, -1, -1), (-1, 1, -1), (-1, 1, -1), (-1, 1, 1), (-1, -1, 1))
        base_coords_face3 = ((1, -1, -1), (1, -1, 1), (1, 1, 1), (1, 1, 1), (1, 1, -1), (1, -1, -1))
        base_coords_face4 = ((-1, -1, 1), (-1, 1, 1), (1, 1, 1), (1, 1, 1), (1, -1, 1), (-1, -1, 1))
        base_coords_face5 = ((-1, 1, -1), (1, 1, -1), (1, 1, 1), (1, 1, 1), (-1, 1, 1), (-1, 1, -1))
        base_coords_face6 = ((-1, -1, -1), (-1, -1, 1), (1, -1, -1), (1, -1, -1), (-1, -1, 1), (1, -1, 1))
        base_coords = base_coords_face1 + base_coords_face2 + base_coords_face3 + base_coords_face4 + base_coords_face5 + base_coords_face6
        cube_mesh = Mesh(shader, attributes=dict(position=base_coords))
        skybox_textures = CubeMapTexture(tex_files)

        textures = CubeMapTexture(tex_files)
        super().__init__(cube_mesh, diffuse_maps=skybox_textures)

    def key_handler(self, key):
        self.wrap = next(self.wraps) if key == glfw.KEY_F6 else self.wrap
        self.filter = next(self.filters) if key == glfw.KEY_F7 else self.filter
        if key in (glfw.KEY_F6, glfw.KEY_F7):
            texture = Texture(self.file, self.wrap, *self.filter)
            self.textures.update(diffuse_map=texture)


# -------------- main program and scene setup --------------------------------
def main():
    """ create a window, add scene objects, then run rendering loop """
    viewer = Viewer()
    shader = Shader("texture.vert", "texture.frag")

    shader_skybox = Shader("skybox.vert", "skybox.frag")
    viewer.add(Skybox(shader_skybox,["skybox/front.jpg", "skybox/back.jpg", "skybox/top.jpg", 
                                        "skybox/bottom.jpg", "skybox/left.jpg", "skybox/right.jpg"]))
    
    light_dir = (1, 1, -1)
    # viewer.add(*[mesh for file in sys.argv[1:] for mesh in load(file, shader, light_dir=light_dir)])
    # t = Terrain(shader, light_dir)
    # viewer.add(t)

    # Terrain

    ter = Terrain(shader, light_dir)
    ter_transf = Node(transform=translate(.0, .0, -2) @ rotate(axis=(1., 0., 0.), angle=-90.0) @ scale(20,20,20))
    ter_transf.add(ter)

    # Volcano
    volc = Volcano(shader, light_dir)
    volc_transf_1 = Node(transform=scale(.1, .1, .1) @ translate(-8, -9, -2))
    # volc_transf_1 = Node(transform=scale(.2, .2, .2) @ translate(-8, -9, -2))
    volc_transf_1.add(volc)

    # Lava
    lava = Cylinder(shader, light_dir)
    lava_transf = Node(transform=translate(.0, 4.2, -.2) @ scale(.6, .005, .6))
    # lava_transf = Node(transform=translate(-0.8, -0.51, -0.22) @ scale(.08, .005, .08))
    lava_transf.add(lava)

    volc_transf_1.add(lava_transf)

    # Volcano base
    volcano_base = Node(transform=translate(1, 1, .0) @ scale(5,5,5))
    volcano_base.add(volc_transf_1)
    # volcano_base.add(lava_transf)


    translate_keys = {0: vec(0,0,0), 6: vec(0,0,0), 8: vec(0,0.3,0), 
                    10: vec(0, .6, 0), 12: vec(0, .9, 0)}
    rotate_keys = {0: quaternion(), 6: quaternion(), 8: quaternion_from_euler(0, 0,0),
                   10: quaternion_from_euler(0, 0, 0), 12: quaternion()}
    # rotate_keys = {}
    scale_keys = {0: 1, 6: 1, 8: 1, 10: 1, 12: 1}
    # translate_keys = {0: vec(0, -.50, 0), 2: vec(0, 0, 0), 6: vec(0, 1, 0)}
    # rotate_keys = {0: quaternion(), 2: quaternion_from_euler(180, 45, 90),
    #                3: quaternion_from_euler(180, 0, 180), 6: quaternion()}
    # scale_keys = {0: .1, 2: 0.2, 6: .3}
    keynode = KeyFrameControlNode(translate_keys, rotate_keys, scale_keys, transform=scale(.1 , .1, .1))
    
    monkey = Monkey(shader, light_dir)
    monkey_transf = Node(transform=translate(-0.8, -0.7, -0.2) @ scale(.05,.05,.05))
    # monkey_transf = Node()
    monkey_transf.add(monkey)
    keynode.add(monkey_transf)
    # keynode.add(Monkey(shader, light_dir))
    # base.add(keynode)
    volcano_base.add(keynode)
    # 
    base = Node()
    base.add(ter_transf)
    base.add(volcano_base)

    player = Player(shader, light_dir)
    player_transf = Node(transform=translate(.0, -.6, -2) @ scale(.01, .01, .01) @ rotate(axis=(1., 0., 0.) , angle= -90))
    player_transf.add(player)
  
    
    viewer.add(base)
    viewer.add(player_transf)    

    # if len(sys.argv) != 2:
    #     print('Usage:\n\t%s [3dfile]*\n\n3dfile\t\t the filename of a model in'
    #           ' format supported by assimp.' % (sys.argv[0],))
    #     viewer.add(TexturedPlane(shader, "volcano-3d-model/Volcano_texture.png"))

    # start rendering loop
    viewer.run()


if __name__ == '__main__':
    main()                     # main function keeps variables locally scoped
