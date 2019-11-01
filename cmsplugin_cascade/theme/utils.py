from django.conf import settings
from dynamic_preferences.registries import global_preferences_registry
# We instantiate a manager for our global preferences
global_preferences = global_preferences_registry.manager()

def get_color_primary():
    return global_preferences['primary__color']
    
def get_color_secondary():
    return global_preferences['secondary__color']

def get_color_success():
    return global_preferences['success__color']

def get_color_warning():
    return global_preferences['warning__color']

def get_color_danger():
    return global_preferences['danger__color']

def get_color_info():
    return global_preferences['info__color']

def get_color_light():
    return global_preferences['light__color']

def get_color_dark():
    return global_preferences['dark__color']

def get_path_file_variables_scss():
    if getattr(settings, 'CASCADE_SCSS_VARIABLES', None):
        path_variables_scss = '"../{}"'.format( settings.CASCADE_SCSS_VARIABLES)
    else:
        project_name =  settings.ROOT_URLCONF.split('.')[0]
        path_variables_scss  = '"../{0}/static/{0}/css/variables.scss"'.format(project_name)
    return path_variables_scss 
