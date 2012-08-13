import math
import time
import random
from ctypes import *

from pyglet.gl import *
import pyglet
import numpy

import pygly.gl
import pygly.sorter
from pygly.scene_node import SceneNode
from pygly.camera_node import CameraNode
from pygly.shader import Shader

from common import BaseApplication
from gol_renderable import GOL_Renderable


class Application( BaseApplication ):
    
    def __init__( self ):
        super( Application, self ).__init__()
        
        self.print_opengl_versions()

    def print_opengl_versions( self ):
        # get OpenGL version
        print "OpenGL version", self.window.context.get_info().get_version()        
        
        # get GLSL version
        plain = string_at(glGetString(GL_SHADING_LANGUAGE_VERSION)).split(' ')[0]
        major, minor = map(int, plain.split('.'))
        version = major*100 + minor
        print "GLSL Version", version
        
    def setup_camera( self ):
        super( Application, self ).setup_camera()

        # move the camera so we can see the scene
        self.camera.transform.inertial.translate(
            [ 0.0, 0.0, 10.0 ]
            )

    def setup_ui( self ):
        super( Application, self ).setup_ui()

        self.help_label = pyglet.text.HTMLLabel(
"""
<b>Game of Life</b>
""",
        multiline = True,
        x = 10,
        y = 50,
        width = 500,
        anchor_x = 'left',
        anchor_y = 'bottom',
        )
        self.help_label.color = (255,255,255,255)

    def setup_scene( self ):
        super( Application, self ).setup_scene()
        
        # enable texturing
        glEnable( GL_TEXTURE_2D )

        # set our gl clear colour
        glClearColor( 0.2, 0.2, 0.2, 1.0 )

        self.gol_node = SceneNode( "GOL_Node" )
        self.scene_node.add_child( self.gol_node )
        
        # make the GOL board
        # ensure it is a power of 2 for ou texture
        board_size = (512, 512)
        self.gol = GOL_Renderable( board_size )
        self.gol_node.add_child( self.gol )
        self.renderables.append( self.gol )

    def update_mouse( self, dt ):
        # USE MOUSE VALUES HERE
        pass

        # reset the relative position of the mouse
        super( Application, self ).update_mouse( dt )

    def on_key_event( self, digital, event, key ):
        # HANDLE KEYBOARD INPUT HERE
        pass

    def update_scene( self, dt ):
        # rotate the GOL board
        self.gol_node.transform.object.rotate_y( dt )
        
        # add the delta to the accumulated time
        self.gol.dt += dt

    def render_3d( self ):
        # enable z buffer
        glEnable( GL_DEPTH_TEST )
        
        # disable lighting
        glDisable( GL_LIGHTING )
        
        # enable smooth shading
        glShadeModel( GL_SMOOTH )

        # rescale only normals for lighting
        glEnable( GL_RESCALE_NORMAL )

        # enable scissoring for viewports
        glEnable( GL_SCISSOR_TEST )

        # enable back face culling
        #glEnable( GL_CULL_FACE )
        #glCullFace( GL_BACK )
        glDisable( GL_CULL_FACE )

        # render each object
        for renderable in self.renderables:
            renderable.render()

    def render_2d( self ):
        super( Application, self ).render_2d()

        self.help_label.draw()


def main():
    # create app
    app = Application()
    app.run()
    app.window.close()


if __name__ == "__main__":
    main()

