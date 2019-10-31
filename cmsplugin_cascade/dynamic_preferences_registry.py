# cmsplugin_cascade/dynamic_preferences_registry.py

from dynamic_preferences.types import BooleanPreference, StringPreference, IntPreference,LongStringPreference, ChoicePreference
from dynamic_preferences.preferences import Section
from dynamic_preferences.registries import global_preferences_registry
from dynamic_preferences.users.registries import user_preferences_registry
from django import forms
# we create some section objects to link related preferences together


#general = Section('general')
#discussion = Section('discussion')


@global_preferences_registry.register
class FavouriteColour(StringPreference):
    """
    What's your favourite colour ?
    """
    section = "primary"
    name = "color"
    default = "#007bff"

@global_preferences_registry.register
class FavouriteColour(StringPreference):
    """
    What's your favourite colour ?
    """
    section = "secondary"
    name = "color"
    default = "#6c757d"

@global_preferences_registry.register
class FavouriteColour(StringPreference):
    """
    What's your favourite colour ?
    """
    section = "success"
    name = "color"
    default = "#28a745"


@global_preferences_registry.register
class FavouriteColour(StringPreference):
    """
    What's your favourite colour ?
    """
    section = "warning"
    name = "color"
    default = "#ffc107"

@global_preferences_registry.register
class FavouriteColour(StringPreference):
    """
    What's your favourite colour ?
    """
    section = "danger"
    name = "color"
    default = "#dc3545"


@global_preferences_registry.register
class FavouriteColour(StringPreference):
    """
    What's your favourite colour ?
    """
    section = "info"
    name = "color"
    default = "#17a2b8"

@global_preferences_registry.register
class FavouriteColour(StringPreference):
    """
    What's your favourite colour ?
    """
    section = "light"
    name = "color"
    default = "#f8f9fa"

@global_preferences_registry.register
class FavouriteColour(StringPreference):
    """
    What's your favourite colour ?
    """
    section = "dark"
    name = "color"
    default = "#343a40"

