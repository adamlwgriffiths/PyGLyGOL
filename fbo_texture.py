import ctypes

from pyglet.gl import *


class FBO_Texture( object ):    
    
    def __init__( self, dimensions, texture = None ):
        super( FBO_Texture, self ).__init__()

        self.dimensions = dimensions
        
        # create an FBO texture
        self.fbo = GLuint()
        glGenFramebuffers( 1, ctypes.byref( self.fbo ) )
        
        # create a texture
        self.texture = texture
        if self.texture == None:
            self.texture = pyglet.image.Texture.create_for_size(
                GL_TEXTURE_2D,
                self.width,
                self.height,
                GL_RGBA
                )
        
        # bind the texture to the FBO as our output
        # bind the FBO
        self.bind()
        # bind our texture to the FBO
        glBindTexture( GL_TEXTURE_2D, self.texture.id )
        glFramebufferTexture2D(
            GL_FRAMEBUFFER,
            GL_COLOR_ATTACHMENT0,
            GL_TEXTURE_2D,
            self.texture.id,
            0
            )
        
        # check the FBO created successfully
        status = glCheckFramebufferStatus( GL_FRAMEBUFFER )
        assert status == GL_FRAMEBUFFER_COMPLETE
        
        # unbind the FBO
        # this sets the FBO back to the normal render buffer
        self.unbind()
        
    def __del__( self ):
        glDeleteFramebuffers( 1, ctypes.byref( self.fbo ) )
    
    def bind( self ):
        glBindFramebuffer( GL_FRAMEBUFFER, self.fbo )
        glDrawBuffer( GL_COLOR_ATTACHMENT0 )
    
    def unbind( self ):
        glBindFramebuffer( GL_FRAMEBUFFER, 0 )
    
    def __enter__( self ):
        self.bind()
    
    def __exit__( self, type, value, traceback ):
        self.unbind()

    @property
    def width( self ):
        return self.dimensions[ 0 ]
    
    @property
    def height( self ):
        return self.dimensions[ 1 ]
    