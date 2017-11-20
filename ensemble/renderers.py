import logging

from . import applications, configurations, timers

_logger = logging.getLogger(__name__.split(".").pop())


class SceneRenderer(object):
    def __init__(self, configuration):
        super().__init__()
        
        self._configuration = configuration
        
        self._timer = timers.Timer(timers.SystemClock())
        
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
        return self._timer
        
    def create(self, scene):
        if self._timer:
            self._timer.update()
        
        if scene:
            scene.create(self)
        
        _logger.info(str(self._timer._clock))
    
    def update(self, scene):
        if self._timer:
            self._timer.update()
        
        if scene:
            scene.update(self)
            scene.render(self)
    
    def delete(self, scene):
        if self._timer:
            self._timer.update()
        
        if scene:
            scene.delete(self)
