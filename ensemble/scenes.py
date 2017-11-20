import numpy as np

from glue import gl, wgl
from glue.gl import GL
from glue.wgl import WGL

from .mathematics import matrices, vectors


class Scene(object):
    def __init__(self):
        super().__init__()
    
    def create(self, context):
        pass
    
    def update(self, context):
        pass
    
    def render(self, context):
        pass
    
    def delete(self, context):
        pass


class ShaderToyScene(Scene):
    def __init__(self):
        super().__init__()
        
        self._background = np.array([0,0,0,1], np.float32)
        self._foreground = np.array([1,1,1,1], np.float32)
    
    def create(self, context):
        from . import applications
        from glue.gl import utilities
        
        self._program = utilities.load_program([
            applications.data_path("shaders/noop.vs"),
            applications.data_path("shaders/quad.gs"),
            applications.data_path("shaders/quad.fs"),
        ], uniforms={
            "iChannel0": gl.Sampler2DType,
            "iChannel1": gl.Sampler2DType,
            "iResolution": gl.Vec3Type,
            "iTime": gl.ScalarType,
            "model": gl.Mat4Type,
            "view": gl.Mat4Type,
            "projection": gl.Mat4Type,
            "tex_coord_transform": gl.Mat4Type,
        })
        
        self._texture = utilities.load_texture(applications.data_path("images/smile.png"))
        
        self._vao = gl.VertexArray().create()
        
        self._tex_coord_transform = np.dot(matrices.translate(context.video.index), matrices.scale(1.0/context.video.global_.shape))
    
    def render(self, context):
        t = context.timer.elapsed
        
        #model = transforms.identity()
        #view = transforms.identity()
        #projection = transforms.identity()
        #tex_coord_transform = transforms.identity()
        
        gl.clear_color(self._background)
        gl.clear()
        
        with gl.bound(self._program), gl.bound(self._vao):
            self._program.uniforms["iResolution"] = context.video.global_.resolution
            self._program.uniforms["iTime"] = t
            '''
            self._program.uniforms["model"] = model
            self._program.uniforms["view"] = view
            self._program.uniforms["projection"] = projection
            '''
            self._program.uniforms["tex_coord_transform"] = self._tex_coord_transform
            
            gl.depth_mask(False)
            GL.glDrawArrays(GL.GL_POINTS, 0, 1)
            gl.depth_mask(True)
