import logging

import math

from PyQt5 import QtCore, QtGui, QtNetwork
from PyQt5.QtCore import Qt

import numpy as np

from glue import gl, wgl
from glue.gl import GL
from glue.wgl import WGL

import liblo

from . import applications, configurations, observables, renderers, timers

_logger = logging.getLogger(__name__.split(".").pop())

"""
import OpenGL.WGL.ARB.extensions_string
import OpenGL.WGL.EXT.extensions_string
import OpenGL.WGL.NV.swap_group


WGL_EXTS = [
    "GL_ARB_compute_shader",
    "WGL_ARB_create_context",
    "WGL_ARB_extensions_string",
    "WGL_EXT_extensions_string",
    "WGL_EXT_swap_control",
    "WGL_NV_swap_group",
]

def logDebugInfo():
    #from OpenGL import platform
    #print(platform.PLATFORM.getExtensionProcedure('wglGetExtensionsString'))
    print(bool(OpenGL.WGL.ARB.extensions_string.wglGetExtensionsStringARB))
    print(bool(OpenGL.WGL.EXT.extensions_string.wglGetExtensionsStringEXT))
    print(bool(OpenGL.WGL.NV.swap_group.wglJoinSwapGroupNV))
    
    print("GL:", GL.glGetString(GL.GL_VERSION))
    
    #logDebugExtensions()
    #print(dir(OpenGL.WGL.EXT.extensions_string))
    
    from OpenGL import extensions
    print(extensions.hasExtension("WGL_ARB_extensions_string"))
"""

def debugLogExtensions():
    _logger.info("Extensions:")
    for i in range(GL.glGetIntegerv(GL.GL_NUM_EXTENSIONS)):
        _logger.info(str(GL.glGetStringi(GL.GL_EXTENSIONS, i), "utf-8"))
    '''
    hdc = wgl.get_current_dc()
    for name in str(wgl.get_extension_string(hdc), "utf-8").split():
        _logger.info(name)
    '''
    '''
    from OpenGL import extensions
    for name in ["WGL_ARB_extensions_string", "WGL_EXT_swap_control", "WGL_NV_swap_group"]:
        _logger.info("%s: %s", name, extensions.hasExtension(name))
    '''

def debugLogInfo():
    _logger.info("PC: %s", applications.hostname())
    _logger.info("Qt: %s", QtCore.QT_VERSION_STR)
    _logger.info("GL: %s", str(GL.glGetString(GL.GL_VERSION), "utf-8"))
    _logger.info("GLSL: %s", str(GL.glGetString(GL.GL_SHADING_LANGUAGE_VERSION), "utf-8"))
    
    screen = QtGui.QGuiApplication.primaryScreen()
    _logger.info("Screen: %.2f Hz", screen.refreshRate())
    
    #debugLogExtensions()

def queryExtensions(*args):
    from OpenGL import extensions
    
    class Extensions(object):
        pass
    
    result = Extensions()
    
    _logger.info("Extensions:")
    for name in args:
        value = extensions.hasExtension(name)
        setattr(result, name, value)
        _logger.info("%s: %s", name, value)
    
    return result


class SceneWindow(QtGui.QOpenGLWindow):
    @property
    def audio(self):
        return self._configuration.audio
    
    @property
    def video(self):
        return self._configuration.video
    
    @property
    def network(self):
        return self._configuration.network
    
    @property
    def timer(self):
        return self._renderer._timer
    
    @property
    def fullscreen(self):
        return self.video.fullscreen
    
    @fullscreen.setter
    def fullscreen(self, value):
        self.video.fullscreen = value
        (self.enableFullscreen if self.video.fullscreen else self.disableFullscreen)()
    
    def __init__(self, configuration, scene=None):
        super().__init__()
        
        self._active = True
        self._extensions = None
        
        self._configuration = configuration
        self._scene = scene
        
        self._renderer = renderers.SceneRenderer(configuration)
        
        self.onKeyPress = observables.Observable()
        self.onKeyRelease = observables.Observable()
        self.onMousePress = observables.Observable()
        self.onMouseRelease = observables.Observable()
        
        self.initAudio()
        self.initVideo()
        self.initNetwork()
    
    def initAudio(self):
        pass
    
    def initVideo(self):
        format = QtGui.QSurfaceFormat()
        format.setProfile(QtGui.QSurfaceFormat.CoreProfile)
        format.setVersion(4, 4)
        
        format.setRedBufferSize(self.video.format.red)
        format.setBlueBufferSize(self.video.format.green)
        format.setGreenBufferSize(self.video.format.blue)
        format.setAlphaBufferSize(self.video.format.alpha)
        
        format.setDepthBufferSize(self.video.format.depth)
        format.setStencilBufferSize(self.video.format.stencil)
        
        format.setSamples(self.video.samples)
        format.setSwapInterval(self.video.vsync)
        
        format.setStereo(self.video.stereo)
        
        self.setFormat(format)
    
    def initNetwork(self):
        def onPlay(path, args):
            self.timer.start(args[0])
        def onPause(path, args):
            self.timer.pause(args[0])
        def onStop(path, args):
            self.timer.stop(args[0])
        def onSeek(path, args):
            self.timer.seek(args[0], args[1])
        
        self.server = liblo.ServerThread(self.network.port, group="224.0.0.1")
        self.server.add_method("/play", "t", onPlay)
        self.server.add_method("/pause", "t", onPause)
        self.server.add_method("/stop", "t", onStop)
        self.server.add_method("/seek", "tt", onSeek)
        #self.server.add_method(None, None, self.onMessageReceived)
        self.server.start()
        
        self._broadcast = liblo.Address("224.0.0.1", self.network.port, liblo.UDP)
        self._broadcast.ttl = 1
        
        def onTimeout():
            value = self.timer._clock.time
            liblo.send(self._broadcast, "/time", ('t', value))
        
        self._heartbeat = QtCore.QTimer()
        self._heartbeat.timeout.connect(onTimeout)
    
    def enableFullscreen(self):
        QtGui.QGuiApplication.setOverrideCursor(Qt.BlankCursor)
        self.showFullScreen()
    
    def disableFullscreen(self):
        self.showNormal()
        QtGui.QGuiApplication.restoreOverrideCursor()
    
    def enableFramelock(self, group=1, barrier=1):
        if not self._extensions.WGL_NV_swap_group:
            return False
        
        hdc = wgl.get_current_dc()
        
        maxGroups, maxBarriers = wgl.query_max_swap_groups(hdc)
        
        _logger.info("Max Swap Groups/Barriers: %d/%d", maxGroups, maxBarriers)
        
        if group > maxGroups:
            _logger.warn("No swap groups to join.")
            return False
        
        if barrier > maxBarriers:
            _logger.warn("No swap barriers to bind.")
            return False
        
        if not wgl.join_swap_group(hdc, group):
            _logger.warn("Failed to joind swap group.")
            return False
        
        if not wgl.bind_swap_barrier(group, barrier):
            _logger.warn("Failed to bind swap barrier.")
            return False
        
        screen = QtGui.QGuiApplication.primaryScreen()
        
        self.timer._clock = timers.SwapGroupClock(screen.refreshRate())
        self.timer._clock.reset()
        
        return True
    
    def disableFramelock(self):
        if not self._extensions.WGL_NV_swap_group:
            return False
        
        hdc = wgl.get_current_dc()
        
        if not wgl.join_swap_group(hdc, 0):
            return False
        
        self.timer._clock = timers.SystemClock()
        
        return True
    
    def enableTimeserver(self):
        self._heartbeat.start(1000)
    
    def disableTimeserver(self):
        self._heartbeat.stop()
    
    def initializeGL(self):
        debugLogInfo()
        
        self._extensions = queryExtensions("WGL_ARB_extensions_string", "WGL_EXT_swap_control", "WGL_NV_swap_group")
        
        if self.video.fullscreen:
            self.enableFullscreen()
        
        if self.video.framelock:
            self.enableFramelock()
        
        if self.network.timeserver:
            self.enableTimeserver()
        
        if self._renderer:
            self._renderer.create(self._scene)
    
    def paintGL(self):
        if self._renderer:
            self._renderer.update(self._scene)
        
        if self._active:
            self.requestUpdate()
    
    def toggleFullscreen(self):
        self.video.fullscreen = not self.video.fullscreen
        if self.video.fullscreen:
            self.enableFullscreen()
        else:
            self.disableFullscreen()
    
    def keyPressEvent(self, event):
        self.onKeyPress(event)
    
    def keyReleaseEvent(self, event):
        self.onKeyRelease(event)
        
        if event.key() == QtCore.Qt.Key_Escape:
            QtGui.QGuiApplication.instance().quit()
        elif event.key() == Qt.Key_Return:
            if event.modifiers() & Qt.AltModifier:
                self.toggleFullscreen()
            else:
                self.timer.stop()
        elif event.key() == Qt.Key_Space:
            self.timer.toggle()
    
    def mousePressEvent(self, event):
        self.onMousePress(event)
    
    def mouseReleaseEvent(self, event):
        self.onMouseRelease(event)
