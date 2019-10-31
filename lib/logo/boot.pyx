
"""Logo Messenger package configuration."""

# Location of the Kivy data, defaults to <kivy path>/data
# os.environ['KIVY_DATA_DIR'] = ''

# Location of the Kivy modules, defaults to <kivy path>/modules
# os.environ['KIVY_MODULES_DIR'] = ''

# Location of the Kivy home. This directory is used for local configuration,
# and must be in a writable location.
# os.environ['KIVY_HOME'] = ''

# If set, the SDL2 libraries and headers from this path are used when compiling
# kivy instead of the ones installed system-wide. To use the same libraries
# while running a kivy app, this path must be added at the start of the PATH
# environment variable.
# os.environ['KIVY_SDL2_PATH'] = ''

# If this name is found in environ, Kivy will not read the user config file.
# os.environ['KIVY_USE_DEFAULTCONFIG'] = ''

# If set, no configuration file will be read or written to. This also applies
# to the user configuration directory.
# os.environ['KIVY_NO_CONFIG'] = ''

# If set, logs will be not print to a file
# os.environ['KIVY_NO_FILELOG'] = ''

# If set, logs will be not print to the console
# os.environ['KIVY_NO_CONSOLELOG'] = ''

# If set, the argument passed in command line will not be parsed and used by
# Kivy. Ie, you can safely make a script or an app with your own arguments
# without requiring the – delimiter:
# os.environ['KIVY_NO_ARGS'] = ''

# If a such format environment name is detected, it will be mapped to the
# Config object. They are loaded only once when kivy is imported. The behavior
# can be disabled using KIVY_NO_ENV_CONFIG.
# os.environ['KCFG_section_key'] = ''

# If set, no environment key will be mapped to configuration object. If unset,
# any KCFG_section_key=value will be mapped to Config.
# os.environ['KIVY_NO_ENV_CONFIG'] = ''

# Implementation to use for creating the Window
# Values: sdl2, pygame, x11, egl_rpi
# os.environ['KIVY_WINDOW'] = 'sdl2'

# Implementation to use for rendering text
# Values: sdl2, pil, pygame, sdlttf
# os.environ['KIVY_TEXT'] = 'sdl2'


# Implementation to use for rendering video
# Values: gstplayer, ffpyplayer, ffmpeg, null
# os.environ['KIVY_VIDEO'] = ''

# Implementation to use for playing audio
# Values: sdl2, gstplayer, ffpyplayer, pygame, avplayer
# os.environ['KIVY_AUDIO'] = 'sdl2'

# Implementation to use for reading image
# Values: sdl2, pil, pygame, imageio, tex, dds, gif
# os.environ['KIVY_IMAGE'] = 'sdl2'

# Implementation to use for reading camera
# Values: avfoundation, android, opencv
# os.environ['KIVY_CAMERA'] = ''

# Implementation to use for spelling
# Values: enchant, osxappkit
# os.environ['KIVY_SPELLING'] = ''

# Implementation to use for clipboard management
# Values: sdl2, pygame, dummy, android
# os.environ['KIVY_CLIPBOARD'] = 'sdl2'

# If set, the value will be used for Metrics.dpi.
# os.environ['KIVY_DPI'] = 264

# If set, the value will be used for Metrics.density.
# os.environ['KIVY_METRICS_DENSITY'] = ''

# If set, the value will be used for Metrics.fontscale.
# os.environ['KIVY_METRICS_FONTSCALE'] = ''

# The OpenGL backend to use. See cgl.
# os.environ['KIVY_GL_BACKEND'] = ''

# Whether to log OpenGL calls. See cgl.
# os.environ['KIVY_GL_DEBUG'] = ''

# Whether to use OpenGL ES2. See cgl.
# os.environ['KIVY_GRAPHICS'] = ''

# Whether the GLES2 restrictions are enforced (the default, or if set to 1).
# If set to false, Kivy will not be truly GLES2 compatible.
# Following is a list of the potential incompatibilities that result when set
# to true.
# os.environ['KIVY_GLES_LIMITS'] = ''

# Change the default Raspberry Pi display to use. The list of available value
# is accessible in vc_dispmanx_types.h. Default value is 0:
#
# 0: DISPMANX_ID_MAIN_LCD
# 1: DISPMANX_ID_AUX_LCD
# 2: DISPMANX_ID_HDMI
# 3: DISPMANX_ID_SDTV
# 4: DISPMANX_ID_FORCE_LCD
# 5: DISPMANX_ID_FORCE_TV
# 6: DISPMANX_ID_FORCE_OTHER
# os.environ['KIVY_BCM_DISPMANX_ID'] = ''

# Change the default Raspberry Pi dispmanx layer. Default value is 0.
# os.environ['KIVY_BCM_DISPMANX_LAYER'] = ''
