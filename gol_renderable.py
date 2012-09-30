import ctypes

from pyglet.gl import *
import numpy

from pygly.render_node import RenderNode
from pygly.shader import Shader

from shader_generated_texture import ShaderGeneratedTexture


class GOL_Renderable( RenderNode ):
    vertex_shader = """
void main()
{
    gl_Position    = gl_ModelViewProjectionMatrix * gl_Vertex;
    gl_FrontColor  = gl_Color;
    gl_TexCoord[0] = gl_MultiTexCoord0;
}
"""
    
    fragment_shader = """
#version 120

// inputs
uniform sampler2D tex0;
uniform vec2 dimensions;

void main()
{
    // retrieve the texture coordinate
    vec2 tc = gl_TexCoord[0].xy;
    
    // convert from 0.0 -> 1.0 to texel
    vec2 texel_frac = tc * dimensions;
    
    // ignore the fractional part
    // convert back to texture coord
    float x = floor( texel_frac.x ) / dimensions.x;
    float y = floor( texel_frac.y ) / dimensions.y;
    
    vec2 texel = vec2( x, y );
    float cell_width = 1.0 / dimensions.x;
    float cell_height = 1.0 / dimensions.y;

    // get the current texel
    float current = texture2D(tex0, vec2( x, y ) ).r;
    
    //gl_FragColor = vec4( texture2D(tex0, vec2( x, y ) ).rgb, 1.0 );
    //return;

    // count the neightbouring pixels with a value greater than zero
    float neighbours = 0.0;
    neighbours += texture2D(tex0, texel + vec2( 0.0,       -cell_height ) ).r;
    neighbours += texture2D(tex0, texel + vec2( cell_width,-cell_height ) ).r;
    neighbours += texture2D(tex0, texel + vec2( cell_width, 0.0 ) ).r;
    neighbours += texture2D(tex0, texel + vec2( cell_width, cell_height ) ).r;
    neighbours += texture2D(tex0, texel + vec2( 0.0,        cell_height ) ).r;
    neighbours += texture2D(tex0, texel + vec2(-cell_width, cell_height ) ).r;
    neighbours += texture2D(tex0, texel + vec2(-cell_width, 0.0 ) ).r;
    neighbours += texture2D(tex0, texel + vec2(-cell_width, -cell_height ) ).r;
    
    // apply the rules    
    
    // 1. Any live cell with fewer than two live neighbours dies, as if caused by under-population.
    if ( neighbours < 2.0 )
    {
        gl_FragColor = vec4( 0.0, 0.0, 0.0, 1.0 );
        return;
    }
    
    // 2. Any live cell with two or three live neighbours lives on to the next generation.
    if ( neighbours >= 2.0 && neighbours <= 3.0 && current == 1.0 )
    {
        gl_FragColor = vec4( 1.0, 0.0, 0.0, 1.0 );
        return;
    }
    
    // 3. Any live cell with more than three live neighbours dies, as if by overcrowding.
    if ( neighbours > 3.0 )
    {
        gl_FragColor = vec4( 0.0, 0.0, 0.0, 1.0 );
        return;
    }
    
    // 4. Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction.
    if ( neighbours == 3.0 && current == 0.0 )
    {
        gl_FragColor = vec4( 1.0, 0.0, 0.0, 1.0 );
        return;
    }
    
    gl_FragColor = vec4( 0.0, 0.0, 0.0, 1.0 );
}
"""

    def __init__( self, dimensions ):
        super( GOL_Renderable, self ).__init__( "GOL_Renderable" )
        
        self.dt = 0.0
        self.shader = Shader(
            vert = GOL_Renderable.vertex_shader,
            frag = GOL_Renderable.fragment_shader
            )
        
        # create an FBO texture
        # convert our image to a texture
        self.texture = ShaderGeneratedTexture(
            self.shader,
            dimensions,
            texture1 = self.create_initial_texture( dimensions ).get_texture()
            )

    def create_initial_texture( self, dimensions ):
        # we need RGBA textures
        # which is 4 bytes
        format_size = 4
        
        # populate our GoL board with some random data
        #numpy.random.seed( 0 )
        data = numpy.random.random_integers(
            low = 0,
            high = 1,
            size = (dimensions[ 0 ] * dimensions[ 1 ], format_size)
            )
        
        # convert any 1's to 255
        data *= 255
        
        # set the GBA (from RGBA) to 0
        data[ :, 1: ] = 0
        data[ :, 3 ] = 255
        
        # we need to flatten the array
        data.shape = -1
        
        # convert to GLubytes
        tex_data = (GLubyte * data.size)( *data.astype('u1') )
        
        # create an image
        return pyglet.image.ImageData(
                dimensions[ 0 ],
                dimensions[ 1 ],
                "RGBA",
                tex_data,
                pitch = dimensions[ 1 ] * format_size
                )
    
    def render_mesh( self ):
        # check if we should iterate
        #while self.dt >= 1.0:
        if True:
            # render our FBO
            self.texture.bind()
            
            # use texture layer 0
            self.texture.shader.uniformi('tex0', 0)
            
            # pass in the texture dimensions
            self.texture.shader.uniformf(
                'dimensions',
                float( self.texture.dimensions[ 0 ] ),
                float( self.texture.dimensions[ 1 ] )
                )
            
            # render to texture
            self.texture.render()

            # reset our opengl state
            self.texture.unbind()
            
            self.dt -= 1.0
        
        # use the result of the FBO as a texture
        glBindTexture( self.texture.texture.target, self.texture.texture.id )
        
        # disable texture filtering
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST )
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST )
        
        # render a quad at 0,0,0
        glBegin( GL_QUADS )
        
        x_size, y_size = 5, 5

        glTexCoord2f( 0.0, 0.0 )        
        glVertex3f(-x_size,-y_size, 0.0 )
        
        glTexCoord2f( 1.0, 0.0 )
        glVertex3f( x_size,-y_size, 0.0 )
        
        glTexCoord2f( 1.0, 1.0 )
        glVertex3f( x_size, y_size, 0.0 )
        
        glTexCoord2f( 0.0, 1.0 )
        glVertex3f(-x_size, y_size, 0.0 )
        
        glEnd()
        
        # unbind our texture
        glBindTexture( self.texture.texture.target, 0 )
        
