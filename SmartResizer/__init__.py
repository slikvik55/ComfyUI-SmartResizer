#
# __init__.py
#
# This file makes the 'smartresizer' folder a Python package and tells ComfyUI
# what nodes are available to load from this package.
#

# The '.' before 'SmartResizer' is crucial. It tells Python to import
# from the 'SmartResizer.py' file located in the *same* directory as this __init__.py.
from .SmartResizer import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

# This is a special variable that tells Python what names to export when
# someone does 'from smartresizer import *'. ComfyUI uses this to discover the nodes.
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']