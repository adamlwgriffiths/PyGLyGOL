from pyglet.gl import *

from fbo_texture import FBO_Texture


class ShaderGeneratedTexture( object ):
    
    def __init__( self, shader, dimensions, texture1 = None, texture2 = None ):
        super( ShaderGeneratedTexture, self ).__init__()
        
        self.dimensions = dimensions
        self.shader = shader
        
        self.fbo1 = FBO_Texture( dimensions, texture1 )
        self.fbo2 = FBO_Texture( dimensions, texture2 )
        
        #self.fbo1, self.fbo2 = self.fbo2, self.fbo1
    
    def bind( self ):    
        # switch FBOs around
        self.fbo1, self.fbo2 = self.fbo2, self.fbo1
        
        # set the viewport to be the size of the texture
        glPushAttrib( GL_VIEWPORT_BIT )
        glViewport( 0, 0, self.dimensions[ 0 ], self.dimensions[ 1 ] )

        # set our viewport to an orthogonal viewmatrix
        glMatrixMode( GL_PROJECTION )
        glPushMatrix()
        glLoadIdentity()
        
        # set our modelview to identity
        glMatrixMode( GL_MODELVIEW )
        glPushMatrix()
        glLoadIdentity()

        # bind fbo2's texture to our shader
        # this is the input for fbo1's shader
        glActiveTexture( GL_TEXTURE0 )
        glBindTexture( self.fbo2.texture.target, self.fbo2.texture.id )
        
        # disable texture filtering
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST )
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST )
        
        # render fbo1 to fbo2
        self.fbo1.bind()
        
        # bind our shader
        self.shader.bind()

    def render( self ):
        # render a quad at 0,0,0
        left, bottom, right, top = -1.0, -1.0, 1.0, 1.0
        
        glBegin( GL_QUADS )
        
        glTexCoord2f( 0.0, 0.0 )
        glVertex2f( left, bottom )
        
        glTexCoord2f( 1.0, 0.0 )
        #glTexCoord2f( self.dimensions[ 0 ], 0.0 )
        glVertex2f( right, bottom )
        
        glTexCoord2f( 1.0, 1.0 )
        #glTexCoord2f( self.dimensions[ 0 ], self.dimensions[ 1 ] )
        glVertex2f( right, top )
        
        glTexCoord2f( 0.0, 1.0 )
        #glTexCoord2f( 0.0, self.dimensions[ 1 ] )
        glVertex2f( left, top )
        
        glEnd()            
        
    def unbind( self ):
        self.shader.unbind()
        
        self.fbo1.unbind()

        # reset state
        glPopMatrix()
        glMatrixMode( GL_PROJECTION )
        glPopMatrix()
        glMatrixMode( GL_MODELVIEW )
        glPopAttrib()

    @property
    def texture( self ):
        return self.fbo1.texture
    
    @property
    def width( self ):
        return self.dimensions[ 0 ]
    
    @property
    def height( self ):
        return sef.dimensions[ 1 ]
    