"""
The main DebugToolbar class that loads and renders the Toolbar.
"""
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import simplejson
from uuid import uuid4
import os
from datetime import datetime

class DateTimeJSONEncoder(simplejson.JSONEncoder): 
    """ 
    JSONEncoder subclass that knows how to encode date/time types. 
    """ 
    DATE_FORMAT = "%Y-%m-%d" 
    TIME_FORMAT = "%H:%M:%S" 
    
    def default(self, o): 
        try:
            if isinstance(o, datetime): 
                return o.strftime("%s %s" % (self.DATE_FORMAT, self.TIME_FORMAT)) 
            elif isinstance(o, date): 
                return o.strftime(self.DATE_FORMAT) 
            elif isinstance(o, time): 
                return o.strftime(self.TIME_FORMAT)
            else: 
                return super(DateTimeJSONEncoder, self).default(o)
        except:
            return "Could not serialize."

class DebugToolbarConfiguration(object):
    def __init__(self):
        self.config = {
            'INTERCEPT_REDIRECTS': True,
            'LOG_OUTPUT_PATH': '/tmp',
            'LOGGING_ENABLED': True,
            'TOOLBAR_ENABLED': True
        }
        # Override this tuple by copying to settings.py as `DEBUG_TOOLBAR_PANELS`
        self.default_panels = (
            'debug_toolbar.panels.version.VersionDebugPanel',
            'debug_toolbar.panels.timer.TimerDebugPanel',
            'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
            'debug_toolbar.panels.headers.HeaderDebugPanel',
            'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
            'debug_toolbar.panels.template.TemplateDebugPanel',
            'debug_toolbar.panels.sql.SQLDebugPanel',
            'debug_toolbar.panels.cache.CacheDebugPanel',
            'debug_toolbar.panels.logger.LoggingPanel',
        )
        
        # Check if settings has a DEBUG_TOOLBAR_PANELS, otherwise use default
        if hasattr(settings, 'DEBUG_TOOLBAR_PANELS'):
            self.default_panels = settings.DEBUG_TOOLBAR_PANELS
        # Check if settings has a DEBUG_TOOLBAR_CONFIG and updated config
        if hasattr(settings, 'DEBUG_TOOLBAR_CONFIG'):
            self.config.update(settings.DEBUG_TOOLBAR_CONFIG)
        # Check if settings has a DEBUG_TOOLBAR_MEDIA_ROOT, otherwise use default
        self.media_root = None
        if hasattr(settings, 'DEBUG_TOOLBAR_MEDIA_ROOT'):
            self.media_root = settings.DEBUG_TOOLBAR_MEDIA_ROOT
        
    @property
    def intercept_redirects(self):
        return self.config['INTERCEPT_REDIRECTS']
        
    @property
    def log_output_path(self):
        return self.config['LOG_OUTPUT_PATH']
    
    @property
    def logging_enabled(self):
        return self.config['LOGGING_ENABLED']

    @property
    def toolbar_enabled(self):
        return self.config['TOOLBAR_ENABLED']


class DebugToolbar(object):

    def __init__(self, request):
        self.request = request
        self.panels = []
        self.config = DebugToolbarConfiguration()
        self.load_panels()

    def load_panels(self):
        """
        Populate debug panels
        """
        from django.core import exceptions

        for panel_path in self.config.default_panels:
            try:
                dot = panel_path.rindex('.')
            except ValueError:
                raise exceptions.ImproperlyConfigured, '%s isn\'t a debug panel module' % panel_path
            panel_module, panel_classname = panel_path[:dot], panel_path[dot+1:]
            try:
                mod = __import__(panel_module, {}, {}, [''])
            except ImportError, e:
                raise exceptions.ImproperlyConfigured, 'Error importing debug panel %s: "%s"' % (panel_module, e)
            try:
                panel_class = getattr(mod, panel_classname)
            except AttributeError:
                raise exceptions.ImproperlyConfigured, 'Toolbar Panel module "%s" does not define a "%s" class' % (panel_module, panel_classname)

            try:
                panel_instance = panel_class()
            except:
                print panel_class
                raise # Bubble up problem loading panel

            self.panels.append(panel_instance)

    def render_toolbar(self):
        """
        Renders the overall Toolbar with panels inside.
        """
        rendered_template = None
        if self.config.toolbar_enabled:
            rendered_template = render_to_string('debug_toolbar/base.html', {
                'panels': self.panels,
                'BASE_URL': self.request.META.get('SCRIPT_NAME', ''),
            })
        return rendered_template

    def serialize(self):
        """
        Renders all the data from the panels into json.
        """
        uid = None
        if self.config.logging_enabled:
            data = {}
            for panel in self.panels:
                data[panel.name] = {'data':panel.data, 'title':panel.title()}
            json = simplejson.dumps(data, indent=4, sort_keys=True, cls=DateTimeJSONEncoder)
            uid = str(uuid4())
            fp = open(os.path.join(self.config.log_output_path, '%s.json' % uid), 'w')
            fp.write(json)
            fp.close()
        return uid

