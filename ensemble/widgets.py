import os
import sys

import logging

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, pyqtProperty, pyqtSignal, pyqtSlot

import numpy as np

from glue import gl, wgl
from glue.gl import GL
from glue.wgl import WGL

import liblo

from . import applications, renderers

_logger = logging.getLogger(__name__.split(".").pop())


def debugLogInfo():
    _logger.info("PC: %s", applications.hostname())
    _logger.info("Qt: %s", QtCore.QT_VERSION_STR)
    _logger.info("GL: %s", str(GL.glGetString(GL.GL_VERSION), "utf-8"))
    _logger.info("GLSL: %s", str(GL.glGetString(GL.GL_SHADING_LANGUAGE_VERSION), "utf-8"))
    
    screen = QtGui.QGuiApplication.primaryScreen()
    _logger.info("Screen: %.2f Hz", screen.refreshRate())
    
    #debugLogExtensions()


class SceneWidget(QtWidgets.QOpenGLWidget):
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
    
    def __init__(self, configuration, scene=None, parent=None):
        super().__init__(parent)
        
        self._active = True
        self._extensions = None
        
        self._configuration = configuration
        self._scene = scene
        
        self._renderer = renderers.SceneRenderer(configuration)
        
        self.initAudio()
        self.initVideo()
        self.initNetwork()
        
        if self._active:
            self.heartbeat = QtCore.QTimer()
            self.heartbeat.timeout.connect(self.update)
            self.heartbeat.start(60.0/1000)
    
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
    
    def initializeGL(self):
        debugLogInfo()
        
        if self._renderer:
            self._renderer.create(self._scene)
    
    def paintGL(self):
        if self._renderer:
            self._renderer.update(self._scene)
