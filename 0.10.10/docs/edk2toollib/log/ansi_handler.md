Module edk2toollib.log.ansi_handler
===================================

??? example "View Source"
        ##

        # Handle basic logging with color via ANSI commands

        # Will call into win32 commands as needed when needed

        #

        # Copyright (c) Microsoft Corporation

        #

        # SPDX-License-Identifier: BSD-2-Clause-Patent

        ##

        import logging

        import re

        from edk2toollib.utility_functions import GetHostInfo

        try:

            # try to import windows types from winDLL

            import ctypes

            from ctypes import LibraryLoader

            windll = LibraryLoader(ctypes.WinDLL)

            from ctypes import wintypes

        except (AttributeError, ImportError):

            # if we run into an exception (ie on unix or linux)

            windll = None

        

            # create blank lambda

            def SetConsoleTextAttribute():

                None

        

            # create blank lambda

            def winapi_test():

                None

        

        else:

            # if we don't raise an exception when we import windows types

            # then execute this but don't catch an exception if raised

            from ctypes import byref, Structure

        

            # inspired by https://github.com/tartley/colorama/

            class CONSOLE_SCREEN_BUFFER_INFO(Structure):

                COORD = wintypes._COORD

                """struct in wincon.h."""

                _fields_ = [

                    ("dwSize", COORD),

                    ("dwCursorPosition", COORD),

                    ("wAttributes", wintypes.WORD),

                    ("srWindow", wintypes.SMALL_RECT),

                    ("dwMaximumWindowSize", COORD),

                ]

        

                def __str__(self):

                    return '(%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d)' % (

                        self.dwSize.Y, self.dwSize.X,

                        self.dwCursorPosition.Y, self.dwCursorPosition.X,

                        self.wAttributes,

                        self.srWindow.Top, self.srWindow.Left,

                        self.srWindow.Bottom, self.srWindow.Right,

                        self.dwMaximumWindowSize.Y, self.dwMaximumWindowSize.X

                    )

        

            # a simple wrapper around the few methods calls to windows

            class Win32Console(object):

                _GetConsoleScreenBufferInfo = windll.kernel32.GetConsoleScreenBufferInfo

                _SetConsoleTextAttribute = windll.kernel32.SetConsoleTextAttribute

                _SetConsoleTextAttribute.argtypes = [

                    wintypes.HANDLE,

                    wintypes.WORD,

                ]

                _SetConsoleTextAttribute.restype = wintypes.BOOL

                _GetStdHandle = windll.kernel32.GetStdHandle

                _GetStdHandle.argtypes = [

                    wintypes.DWORD,

                ]

                _GetStdHandle.restype = wintypes.HANDLE

        

                # from winbase.h

                STDOUT = -11

                STDERR = -12

        

                @staticmethod

                def _winapi_test(handle):

                    csbi = CONSOLE_SCREEN_BUFFER_INFO()

                    success = Win32Console._GetConsoleScreenBufferInfo(

                        handle, byref(csbi))

                    return bool(success)

        

                @staticmethod

                def winapi_test():

                    return any(Win32Console._winapi_test(h) for h in

                               (Win32Console._GetStdHandle(Win32Console.STDOUT),

                                Win32Console._GetStdHandle(Win32Console.STDERR)))

        

                @staticmethod

                def GetConsoleScreenBufferInfo(stream_id=STDOUT):

                    handle = Win32Console._GetStdHandle(stream_id)

                    csbi = CONSOLE_SCREEN_BUFFER_INFO()

                    Win32Console._GetConsoleScreenBufferInfo(

                        handle, byref(csbi))

                    return csbi

        

                @staticmethod

                def SetConsoleTextAttribute(stream_id, attrs):

                    handle = Win32Console._GetStdHandle(stream_id)

                    return Win32Console._SetConsoleTextAttribute(handle, attrs)

        

        

        # from wincon.h

        class WinColor(object):

            BLACK = 0

            BLUE = 1

            GREEN = 2

            CYAN = 3

            RED = 4

            MAGENTA = 5

            YELLOW = 6

            GREY = 7

            NORMAL = 0x00  # dim text, dim background

            BRIGHT = 0x08  # bright text, dim background

            BRIGHT_BACKGROUND = 0x80  # dim text, bright background

        

        

        # defines the different codes for the ansi colors

        class AnsiColor(object):

            BLACK = 30

            RED = 31

            GREEN = 32

            YELLOW = 33

            BLUE = 34

            MAGENTA = 35

            CYAN = 36

            WHITE = 37

            RESET = 39

            LIGHTBLACK_EX = 90

            LIGHTRED_EX = 91

            LIGHTGREEN_EX = 92

            LIGHTYELLOW_EX = 93

            LIGHTBLUE_EX = 94

            LIGHTMAGENTA_EX = 95

            LIGHTCYAN_EX = 96

            LIGHTWHITE_EX = 97

            BG_BLACK = 40

            BG_RED = 41

            BG_GREEN = 42

            BG_YELLOW = 43

            BG_BLUE = 44

            BG_MAGENTA = 45

            BG_CYAN = 46

            BG_WHITE = 47

            BG_RESET = 49

            # These are fairly well supported, but not part of the standard.

            BG_LIGHTBLACK_EX = 100

            BG_LIGHTRED_EX = 101

            BG_LIGHTGREEN_EX = 102

            BG_LIGHTYELLOW_EX = 103

            BG_LIGHTBLUE_EX = 104

            BG_LIGHTMAGENTA_EX = 105

            BG_LIGHTCYAN_EX = 106

            BG_LIGHTWHITE_EX = 107

        

            @classmethod

            def __contains__(self, item):

        

                if type(item) is str and hasattr(self, item):

                    return True

                # check if we contain the color number

                for attr_name in dir(self):

                    if getattr(self, attr_name) is item:

                        return True

                return False

        

        

        # the formatter that outputs ANSI codes as needed

        class ColoredFormatter(logging.Formatter):

            AZURE_COLORS = {

                'CRITICAL': "section",

                'ERROR': "error"

            }

        

            COLORS = {

                'WARNING': AnsiColor.YELLOW,

                'INFO': AnsiColor.CYAN,

                'DEBUG': AnsiColor.BLUE,

                'CRITICAL': AnsiColor.LIGHTWHITE_EX,

                'ERROR': AnsiColor.RED,

                "STATUS": AnsiColor.GREEN,

                "PROGRESS": AnsiColor.GREEN,

                "SECTION": AnsiColor.CYAN

            }

        

            def __init__(self, msg="", use_azure=False):

                logging.Formatter.__init__(self, msg)

                self.use_azure = use_azure

        

            def format(self, record):

                levelname = record.levelname

                org_message = record.msg

        

                if not self.use_azure and levelname in ColoredFormatter.COLORS:

                    # just color the level name

                    if record.levelno < logging.WARNING:

                        levelname_color = get_ansi_string(ColoredFormatter.COLORS[levelname]) + levelname + get_ansi_string()

                    # otherwise color the wholes message

                    else:

                        levelname_color = get_ansi_string(ColoredFormatter.COLORS[levelname]) + levelname

                        record.msg += get_ansi_string()

                    record.levelname = levelname_color

        

                if self.use_azure and levelname in ColoredFormatter.AZURE_COLORS:

                    levelname_color = "##[" + \

                        ColoredFormatter.AZURE_COLORS[levelname] + "]"

                    record.levelname = levelname_color

        

                result = logging.Formatter.format(self, record)

        

                record.levelname = levelname

                record.msg = org_message

                return result

        

        

        # returns the string formatted ANSI command for the specific color

        def get_ansi_string(color=AnsiColor.RESET):

            CSI = '\033['

            colors = AnsiColor()

            if color not in colors:

                color = AnsiColor.RESET

            return CSI + str(color) + 'm'

        

        

        class ColoredStreamHandler(logging.StreamHandler):

        

            # Control Sequence Introducer

            ANSI_CSI_RE = re.compile('\001?\033\\[((?:\\d|;)*)([a-zA-Z])\002?')

        

            def __init__(self, stream=None, strip=None, convert=None):

                logging.StreamHandler.__init__(self, stream)

                self.on_windows = GetHostInfo().os == "Windows"

                # We test if the WinAPI works, because even if we are on Windows

                # we may be using a terminal that doesn't support the WinAPI

                # (e.g. Cygwin Terminal). In this case it's up to the terminal

                # to support the ANSI codes.

                self.conversion_supported = (self.on_windows and Win32Console.winapi_test())

                self.strip = False

                # should we strip ANSI sequences from our output?

                if strip is None:

                    strip = self.conversion_supported or (

                        not self.stream.closed and not self.stream.isatty())

                self.strip = strip

        

                # should we should convert ANSI sequences into win32 calls?

                if convert is None:

                    convert = (self.conversion_supported and not self.stream.closed and self.stream.isatty())

                self.convert = convert

                self.win32_calls = None

        

                if stream is not None:

                    self.stream = stream

        

                if self.on_windows:

                    self.win32_calls = self.get_win32_calls()

                    self._light = 0

                    self._default = Win32Console.GetConsoleScreenBufferInfo(

                        Win32Console.STDOUT).wAttributes

                    self.set_attrs(self._default)

                    self._default_fore = self._fore

                    self._default_back = self._back

                    self._default_style = self._style

        

            def handle(self, record):

                """

                Conditionally emit the specified logging record.

                Emission depends on filters which may have been added to the handler.

                Wrap the actual emission of the record with acquisition/release of

                the I/O thread lock. Returns whether the filter passed the record for

                emission.

                """

        

                rv = self.filter(record)

                if rv and record.levelno >= self.level:

                    self.acquire()

                    try:

                        self.emit(record)

                    finally:

                        self.release()

                return rv

        

            def get_win32_calls(self):

                if self.convert:

                    return {

                        AnsiColor.BLACK: (self.set_foreground, WinColor.BLACK),

                        AnsiColor.RED: (self.set_foreground, WinColor.RED),

                        AnsiColor.GREEN: (self.set_foreground, WinColor.GREEN),

                        AnsiColor.YELLOW: (self.set_foreground, WinColor.YELLOW),

                        AnsiColor.BLUE: (self.set_foreground, WinColor.BLUE),

                        AnsiColor.MAGENTA: (self.set_foreground, WinColor.MAGENTA),

                        AnsiColor.CYAN: (self.set_foreground, WinColor.CYAN),

                        AnsiColor.WHITE: (self.set_foreground, WinColor.GREY),

                        AnsiColor.RESET: (self.set_foreground, None),

                        AnsiColor.LIGHTBLACK_EX: (self.set_foreground, WinColor.BLACK, True),

                        AnsiColor.LIGHTRED_EX: (self.set_foreground, WinColor.RED, True),

                        AnsiColor.LIGHTGREEN_EX: (self.set_foreground, WinColor.GREEN, True),

                        AnsiColor.LIGHTYELLOW_EX: (self.set_foreground, WinColor.YELLOW, True),

                        AnsiColor.LIGHTBLUE_EX: (self.set_foreground, WinColor.BLUE, True),

                        AnsiColor.LIGHTMAGENTA_EX: (self.set_foreground, WinColor.MAGENTA, True),

                        AnsiColor.LIGHTCYAN_EX: (self.set_foreground, WinColor.CYAN, True),

                        AnsiColor.LIGHTWHITE_EX: (self.set_foreground, WinColor.GREY, True),

                        AnsiColor.BG_BLACK: (self.set_background, WinColor.BLACK),

                        AnsiColor.BG_RED: (self.set_background, WinColor.RED),

                        AnsiColor.BG_GREEN: (self.set_background, WinColor.GREEN),

                        AnsiColor.BG_YELLOW: (self.set_background, WinColor.YELLOW),

                        AnsiColor.BG_BLUE: (self.set_background, WinColor.BLUE),

                        AnsiColor.BG_MAGENTA: (self.set_background, WinColor.MAGENTA),

                        AnsiColor.BG_CYAN: (self.set_background, WinColor.CYAN),

                        AnsiColor.BG_WHITE: (self.set_background, WinColor.GREY),

                        AnsiColor.BG_RESET: (self.set_background, None),

                        AnsiColor.BG_LIGHTBLACK_EX: (self.set_background, WinColor.BLACK, True),

                        AnsiColor.BG_LIGHTRED_EX: (self.set_background, WinColor.RED, True),

                        AnsiColor.BG_LIGHTGREEN_EX: (self.set_background, WinColor.GREEN, True),

                        AnsiColor.BG_LIGHTYELLOW_EX: (self.set_background, WinColor.YELLOW, True),

                        AnsiColor.BG_LIGHTBLUE_EX: (self.set_background, WinColor.BLUE, True),

                        AnsiColor.BG_LIGHTMAGENTA_EX: (self.set_background, WinColor.MAGENTA, True),

                        AnsiColor.BG_LIGHTCYAN_EX: (self.set_background, WinColor.CYAN, True),

                        AnsiColor.BG_LIGHTWHITE_EX: (self.set_background, WinColor.GREY, True),

                    }

                return dict()

        

            # does the win32 call to set the foreground

            def set_foreground(self, fore=None, light=False, on_stderr=False):

                if fore is None:

                    fore = self._default_fore

                self._fore = fore

                # Emulate LIGHT_EX with BRIGHT Style

                if light:

                    self._light |= WinColor.BRIGHT

                else:

                    self._light &= ~WinColor.BRIGHT

                self.set_console(on_stderr=on_stderr)

        

            # does the win32 call to see the background

            def set_background(self, back=None, light=False, on_stderr=False):

                if back is None:

                    back = self._default_back

                self._back = back

                # Emulate LIGHT_EX with BRIGHT_BACKGROUND Style

                if light:

                    self._light |= WinColor.BRIGHT_BACKGROUND

                else:

                    self._light &= ~WinColor.BRIGHT_BACKGROUND

                self.set_console(on_stderr=on_stderr)

        

            # the win32 call to set the console text attribute

            def set_console(self, attrs=None, on_stderr=False):

                if attrs is None:

                    attrs = self.get_attrs()

                handle = Win32Console.STDOUT

                if on_stderr:

                    handle = Win32Console.STDERR

                Win32Console.SetConsoleTextAttribute(handle, attrs)

        

            # gets the current settings for the style and colors selected

            def get_attrs(self):

                return self._fore + self._back * 16 + (self._style | self._light)

        

            # sets the attributes for the style and colors selected

            def set_attrs(self, value):

                self._fore = value & 7

                self._back = (value >> 4) & 7

                self._style = value & (WinColor.BRIGHT | WinColor.BRIGHT_BACKGROUND)

        

            # writes to stream, stripping ANSI if specified

            def write(self, text):

                if self.strip or self.convert:

                    self.write_and_convert(text)

                else:

                    self.write_plain_text(text)

        

            # write the given text to the strip stripping and converting ANSI

            def write_and_convert(self, text):

                cursor = 0

                for match in self.ANSI_CSI_RE.finditer(text):

                    start, end = match.span()

                    if (cursor < start):

                        self.write_plain_text(text, cursor, start)

                    self.convert_ansi(*match.groups())

                    cursor = end

        

                self.write_plain_text(text, cursor, len(text))

        

            # writes plain text to our stream

            def write_plain_text(self, text, start=None, end=None):

                if start is None:

                    self.stream.write(text)

                elif start < end:

                    self.stream.write(text[start:end])

                self.flush()

        

            # converts an ANSI command to a win32 command

            def convert_ansi(self, paramstring, command):

                if self.convert:

                    params = self.extract_params(command, paramstring)

                    self.call_win32(command, params)

            # extracts the parameters in the ANSI command

        

            def extract_params(self, command, paramstring):

                params = tuple(int(p) for p in paramstring.split(';') if len(p) != 0)

                if len(params) == 0:

                    params = (0,)

        

                return params

        

            # calls the win32 apis set_foreground and set_background

            def call_win32(self, command, params):

                if command == 'm':

                    for param in params:

                        if param in self.win32_calls:

                            func_args = self.win32_calls[param]

                            func = func_args[0]

                            args = func_args[1:]

                            kwargs = dict()

                            func(*args, **kwargs)

        

            # logging.handler method we are overriding to emit a record

            def emit(self, record):

                try:

                    if record is None:

                        return

                    msg = self.format(record)

                    if msg is None:

                        return

                    self.write(str(msg))

                    self.write(self.terminator)

                    self.flush()

                except Exception:

                    self.handleError(record)

Functions
---------

    
#### get_ansi_string

```python3
def get_ansi_string(
    color=39
)
```

??? example "View Source"
        def get_ansi_string(color=AnsiColor.RESET):

            CSI = '\033['

            colors = AnsiColor()

            if color not in colors:

                color = AnsiColor.RESET

            return CSI + str(color) + 'm'

Classes
-------

### AnsiColor

```python3
class AnsiColor(
    /,
    *args,
    **kwargs
)
```

??? example "View Source"
        class AnsiColor(object):

            BLACK = 30

            RED = 31

            GREEN = 32

            YELLOW = 33

            BLUE = 34

            MAGENTA = 35

            CYAN = 36

            WHITE = 37

            RESET = 39

            LIGHTBLACK_EX = 90

            LIGHTRED_EX = 91

            LIGHTGREEN_EX = 92

            LIGHTYELLOW_EX = 93

            LIGHTBLUE_EX = 94

            LIGHTMAGENTA_EX = 95

            LIGHTCYAN_EX = 96

            LIGHTWHITE_EX = 97

            BG_BLACK = 40

            BG_RED = 41

            BG_GREEN = 42

            BG_YELLOW = 43

            BG_BLUE = 44

            BG_MAGENTA = 45

            BG_CYAN = 46

            BG_WHITE = 47

            BG_RESET = 49

            # These are fairly well supported, but not part of the standard.

            BG_LIGHTBLACK_EX = 100

            BG_LIGHTRED_EX = 101

            BG_LIGHTGREEN_EX = 102

            BG_LIGHTYELLOW_EX = 103

            BG_LIGHTBLUE_EX = 104

            BG_LIGHTMAGENTA_EX = 105

            BG_LIGHTCYAN_EX = 106

            BG_LIGHTWHITE_EX = 107

        

            @classmethod

            def __contains__(self, item):

        

                if type(item) is str and hasattr(self, item):

                    return True

                # check if we contain the color number

                for attr_name in dir(self):

                    if getattr(self, attr_name) is item:

                        return True

                return False

------

#### Class variables

```python3
BG_BLACK
```

```python3
BG_BLUE
```

```python3
BG_CYAN
```

```python3
BG_GREEN
```

```python3
BG_LIGHTBLACK_EX
```

```python3
BG_LIGHTBLUE_EX
```

```python3
BG_LIGHTCYAN_EX
```

```python3
BG_LIGHTGREEN_EX
```

```python3
BG_LIGHTMAGENTA_EX
```

```python3
BG_LIGHTRED_EX
```

```python3
BG_LIGHTWHITE_EX
```

```python3
BG_LIGHTYELLOW_EX
```

```python3
BG_MAGENTA
```

```python3
BG_RED
```

```python3
BG_RESET
```

```python3
BG_WHITE
```

```python3
BG_YELLOW
```

```python3
BLACK
```

```python3
BLUE
```

```python3
CYAN
```

```python3
GREEN
```

```python3
LIGHTBLACK_EX
```

```python3
LIGHTBLUE_EX
```

```python3
LIGHTCYAN_EX
```

```python3
LIGHTGREEN_EX
```

```python3
LIGHTMAGENTA_EX
```

```python3
LIGHTRED_EX
```

```python3
LIGHTWHITE_EX
```

```python3
LIGHTYELLOW_EX
```

```python3
MAGENTA
```

```python3
RED
```

```python3
RESET
```

```python3
WHITE
```

```python3
YELLOW
```

### CONSOLE_SCREEN_BUFFER_INFO

```python3
class CONSOLE_SCREEN_BUFFER_INFO(
    /,
    *args,
    **kwargs
)
```

Structure base class

??? example "View Source"
            class CONSOLE_SCREEN_BUFFER_INFO(Structure):

                COORD = wintypes._COORD

                """struct in wincon.h."""

                _fields_ = [

                    ("dwSize", COORD),

                    ("dwCursorPosition", COORD),

                    ("wAttributes", wintypes.WORD),

                    ("srWindow", wintypes.SMALL_RECT),

                    ("dwMaximumWindowSize", COORD),

                ]

        

                def __str__(self):

                    return '(%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d)' % (

                        self.dwSize.Y, self.dwSize.X,

                        self.dwCursorPosition.Y, self.dwCursorPosition.X,

                        self.wAttributes,

                        self.srWindow.Top, self.srWindow.Left,

                        self.srWindow.Bottom, self.srWindow.Right,

                        self.dwMaximumWindowSize.Y, self.dwMaximumWindowSize.X

                    )

------

#### Ancestors (in MRO)

* _ctypes.Structure
* _ctypes._CData

#### Class variables

```python3
COORD
```

```python3
dwCursorPosition
```

```python3
dwMaximumWindowSize
```

```python3
dwSize
```

```python3
srWindow
```

```python3
wAttributes
```

### ColoredFormatter

```python3
class ColoredFormatter(
    msg='',
    use_azure=False
)
```

Formatter instances are used to convert a LogRecord to text.

Formatters need to know how a LogRecord is constructed. They are
responsible for converting a LogRecord to (usually) a string which can
be interpreted by either a human or an external system. The base Formatter
allows a formatting string to be specified. If none is supplied, the
the style-dependent default value, "%(message)s", "{message}", or
"${message}", is used.

The Formatter can be initialized with a format string which makes use of
knowledge of the LogRecord attributes - e.g. the default value mentioned
above makes use of the fact that the user's message and arguments are pre-
formatted into a LogRecord's message attribute. Currently, the useful
attributes in a LogRecord are described by:

%(name)s            Name of the logger (logging channel)
%(levelno)s         Numeric logging level for the message (DEBUG, INFO,
                    WARNING, ERROR, CRITICAL)
%(levelname)s       Text logging level for the message ("DEBUG", "INFO",
                    "WARNING", "ERROR", "CRITICAL")
%(pathname)s        Full pathname of the source file where the logging
                    call was issued (if available)
%(filename)s        Filename portion of pathname
%(module)s          Module (name portion of filename)
%(lineno)d          Source line number where the logging call was issued
                    (if available)
%(funcName)s        Function name
%(created)f         Time when the LogRecord was created (time.time()
                    return value)
%(asctime)s         Textual time when the LogRecord was created
%(msecs)d           Millisecond portion of the creation time
%(relativeCreated)d Time in milliseconds when the LogRecord was created,
                    relative to the time the logging module was loaded
                    (typically at application startup time)
%(thread)d          Thread ID (if available)
%(threadName)s      Thread name (if available)
%(process)d         Process ID (if available)
%(message)s         The result of record.getMessage(), computed just as
                    the record is emitted

??? example "View Source"
        class ColoredFormatter(logging.Formatter):

            AZURE_COLORS = {

                'CRITICAL': "section",

                'ERROR': "error"

            }

        

            COLORS = {

                'WARNING': AnsiColor.YELLOW,

                'INFO': AnsiColor.CYAN,

                'DEBUG': AnsiColor.BLUE,

                'CRITICAL': AnsiColor.LIGHTWHITE_EX,

                'ERROR': AnsiColor.RED,

                "STATUS": AnsiColor.GREEN,

                "PROGRESS": AnsiColor.GREEN,

                "SECTION": AnsiColor.CYAN

            }

        

            def __init__(self, msg="", use_azure=False):

                logging.Formatter.__init__(self, msg)

                self.use_azure = use_azure

        

            def format(self, record):

                levelname = record.levelname

                org_message = record.msg

        

                if not self.use_azure and levelname in ColoredFormatter.COLORS:

                    # just color the level name

                    if record.levelno < logging.WARNING:

                        levelname_color = get_ansi_string(ColoredFormatter.COLORS[levelname]) + levelname + get_ansi_string()

                    # otherwise color the wholes message

                    else:

                        levelname_color = get_ansi_string(ColoredFormatter.COLORS[levelname]) + levelname

                        record.msg += get_ansi_string()

                    record.levelname = levelname_color

        

                if self.use_azure and levelname in ColoredFormatter.AZURE_COLORS:

                    levelname_color = "##[" + \

                        ColoredFormatter.AZURE_COLORS[levelname] + "]"

                    record.levelname = levelname_color

        

                result = logging.Formatter.format(self, record)

        

                record.levelname = levelname

                record.msg = org_message

                return result

------

#### Ancestors (in MRO)

* logging.Formatter

#### Class variables

```python3
AZURE_COLORS
```

```python3
COLORS
```

```python3
default_msec_format
```

```python3
default_time_format
```

#### Methods

    
#### converter

```python3
def converter(
    ...
)
```
localtime([seconds]) -> (tm_year,tm_mon,tm_mday,tm_hour,tm_min,
                          tm_sec,tm_wday,tm_yday,tm_isdst)

Convert seconds since the Epoch to a time tuple expressing local time.
When 'seconds' is not passed in, convert the current time instead.

    
#### format

```python3
def format(
    self,
    record
)
```
Format the specified record as text.

The record's attribute dictionary is used as the operand to a
string formatting operation which yields the returned string.
Before formatting the dictionary, a couple of preparatory steps
are carried out. The message attribute of the record is computed
using LogRecord.getMessage(). If the formatting string uses the
time (as determined by a call to usesTime(), formatTime() is
called to format the event time. If there is exception information,
it is formatted using formatException() and appended to the message.

??? example "View Source"
            def format(self, record):

                levelname = record.levelname

                org_message = record.msg

        

                if not self.use_azure and levelname in ColoredFormatter.COLORS:

                    # just color the level name

                    if record.levelno < logging.WARNING:

                        levelname_color = get_ansi_string(ColoredFormatter.COLORS[levelname]) + levelname + get_ansi_string()

                    # otherwise color the wholes message

                    else:

                        levelname_color = get_ansi_string(ColoredFormatter.COLORS[levelname]) + levelname

                        record.msg += get_ansi_string()

                    record.levelname = levelname_color

        

                if self.use_azure and levelname in ColoredFormatter.AZURE_COLORS:

                    levelname_color = "##[" + \

                        ColoredFormatter.AZURE_COLORS[levelname] + "]"

                    record.levelname = levelname_color

        

                result = logging.Formatter.format(self, record)

        

                record.levelname = levelname

                record.msg = org_message

                return result

    
#### formatException

```python3
def formatException(
    self,
    ei
)
```
Format and return the specified exception information as a string.

This default implementation just uses
traceback.print_exception()

??? example "View Source"
            def formatException(self, ei):

                """

                Format and return the specified exception information as a string.

        

                This default implementation just uses

                traceback.print_exception()

                """

                sio = io.StringIO()

                tb = ei[2]

                # See issues #9427, #1553375. Commented out for now.

                #if getattr(self, 'fullstack', False):

                #    traceback.print_stack(tb.tb_frame.f_back, file=sio)

                traceback.print_exception(ei[0], ei[1], tb, None, sio)

                s = sio.getvalue()

                sio.close()

                if s[-1:] == "\n":

                    s = s[:-1]

                return s

    
#### formatMessage

```python3
def formatMessage(
    self,
    record
)
```

??? example "View Source"
            def formatMessage(self, record):

                return self._style.format(record)

    
#### formatStack

```python3
def formatStack(
    self,
    stack_info
)
```
This method is provided as an extension point for specialized
formatting of stack information.

The input data is a string as returned from a call to
:func:`traceback.print_stack`, but with the last trailing newline
removed.

The base implementation just returns the value passed in.

??? example "View Source"
            def formatStack(self, stack_info):

                """

                This method is provided as an extension point for specialized

                formatting of stack information.

        

                The input data is a string as returned from a call to

                :func:`traceback.print_stack`, but with the last trailing newline

                removed.

        

                The base implementation just returns the value passed in.

                """

                return stack_info

    
#### formatTime

```python3
def formatTime(
    self,
    record,
    datefmt=None
)
```
Return the creation time of the specified LogRecord as formatted text.

This method should be called from format() by a formatter which
wants to make use of a formatted time. This method can be overridden
in formatters to provide for any specific requirement, but the
basic behaviour is as follows: if datefmt (a string) is specified,
it is used with time.strftime() to format the creation time of the
record. Otherwise, an ISO8601-like (or RFC 3339-like) format is used.
The resulting string is returned. This function uses a user-configurable
function to convert the creation time to a tuple. By default,
time.localtime() is used; to change this for a particular formatter
instance, set the 'converter' attribute to a function with the same
signature as time.localtime() or time.gmtime(). To change it for all
formatters, for example if you want all logging times to be shown in GMT,
set the 'converter' attribute in the Formatter class.

??? example "View Source"
            def formatTime(self, record, datefmt=None):

                """

                Return the creation time of the specified LogRecord as formatted text.

        

                This method should be called from format() by a formatter which

                wants to make use of a formatted time. This method can be overridden

                in formatters to provide for any specific requirement, but the

                basic behaviour is as follows: if datefmt (a string) is specified,

                it is used with time.strftime() to format the creation time of the

                record. Otherwise, an ISO8601-like (or RFC 3339-like) format is used.

                The resulting string is returned. This function uses a user-configurable

                function to convert the creation time to a tuple. By default,

                time.localtime() is used; to change this for a particular formatter

                instance, set the 'converter' attribute to a function with the same

                signature as time.localtime() or time.gmtime(). To change it for all

                formatters, for example if you want all logging times to be shown in GMT,

                set the 'converter' attribute in the Formatter class.

                """

                ct = self.converter(record.created)

                if datefmt:

                    s = time.strftime(datefmt, ct)

                else:

                    t = time.strftime(self.default_time_format, ct)

                    s = self.default_msec_format % (t, record.msecs)

                return s

    
#### usesTime

```python3
def usesTime(
    self
)
```
Check if the format uses the creation time of the record.

??? example "View Source"
            def usesTime(self):

                """

                Check if the format uses the creation time of the record.

                """

                return self._style.usesTime()

### ColoredStreamHandler

```python3
class ColoredStreamHandler(
    stream=None,
    strip=None,
    convert=None
)
```

A handler class which writes logging records, appropriately formatted,
to a stream. Note that this class does not close the stream, as
sys.stdout or sys.stderr may be used.

??? example "View Source"
        class ColoredStreamHandler(logging.StreamHandler):

        

            # Control Sequence Introducer

            ANSI_CSI_RE = re.compile('\001?\033\\[((?:\\d|;)*)([a-zA-Z])\002?')

        

            def __init__(self, stream=None, strip=None, convert=None):

                logging.StreamHandler.__init__(self, stream)

                self.on_windows = GetHostInfo().os == "Windows"

                # We test if the WinAPI works, because even if we are on Windows

                # we may be using a terminal that doesn't support the WinAPI

                # (e.g. Cygwin Terminal). In this case it's up to the terminal

                # to support the ANSI codes.

                self.conversion_supported = (self.on_windows and Win32Console.winapi_test())

                self.strip = False

                # should we strip ANSI sequences from our output?

                if strip is None:

                    strip = self.conversion_supported or (

                        not self.stream.closed and not self.stream.isatty())

                self.strip = strip

        

                # should we should convert ANSI sequences into win32 calls?

                if convert is None:

                    convert = (self.conversion_supported and not self.stream.closed and self.stream.isatty())

                self.convert = convert

                self.win32_calls = None

        

                if stream is not None:

                    self.stream = stream

        

                if self.on_windows:

                    self.win32_calls = self.get_win32_calls()

                    self._light = 0

                    self._default = Win32Console.GetConsoleScreenBufferInfo(

                        Win32Console.STDOUT).wAttributes

                    self.set_attrs(self._default)

                    self._default_fore = self._fore

                    self._default_back = self._back

                    self._default_style = self._style

        

            def handle(self, record):

                """

                Conditionally emit the specified logging record.

                Emission depends on filters which may have been added to the handler.

                Wrap the actual emission of the record with acquisition/release of

                the I/O thread lock. Returns whether the filter passed the record for

                emission.

                """

        

                rv = self.filter(record)

                if rv and record.levelno >= self.level:

                    self.acquire()

                    try:

                        self.emit(record)

                    finally:

                        self.release()

                return rv

        

            def get_win32_calls(self):

                if self.convert:

                    return {

                        AnsiColor.BLACK: (self.set_foreground, WinColor.BLACK),

                        AnsiColor.RED: (self.set_foreground, WinColor.RED),

                        AnsiColor.GREEN: (self.set_foreground, WinColor.GREEN),

                        AnsiColor.YELLOW: (self.set_foreground, WinColor.YELLOW),

                        AnsiColor.BLUE: (self.set_foreground, WinColor.BLUE),

                        AnsiColor.MAGENTA: (self.set_foreground, WinColor.MAGENTA),

                        AnsiColor.CYAN: (self.set_foreground, WinColor.CYAN),

                        AnsiColor.WHITE: (self.set_foreground, WinColor.GREY),

                        AnsiColor.RESET: (self.set_foreground, None),

                        AnsiColor.LIGHTBLACK_EX: (self.set_foreground, WinColor.BLACK, True),

                        AnsiColor.LIGHTRED_EX: (self.set_foreground, WinColor.RED, True),

                        AnsiColor.LIGHTGREEN_EX: (self.set_foreground, WinColor.GREEN, True),

                        AnsiColor.LIGHTYELLOW_EX: (self.set_foreground, WinColor.YELLOW, True),

                        AnsiColor.LIGHTBLUE_EX: (self.set_foreground, WinColor.BLUE, True),

                        AnsiColor.LIGHTMAGENTA_EX: (self.set_foreground, WinColor.MAGENTA, True),

                        AnsiColor.LIGHTCYAN_EX: (self.set_foreground, WinColor.CYAN, True),

                        AnsiColor.LIGHTWHITE_EX: (self.set_foreground, WinColor.GREY, True),

                        AnsiColor.BG_BLACK: (self.set_background, WinColor.BLACK),

                        AnsiColor.BG_RED: (self.set_background, WinColor.RED),

                        AnsiColor.BG_GREEN: (self.set_background, WinColor.GREEN),

                        AnsiColor.BG_YELLOW: (self.set_background, WinColor.YELLOW),

                        AnsiColor.BG_BLUE: (self.set_background, WinColor.BLUE),

                        AnsiColor.BG_MAGENTA: (self.set_background, WinColor.MAGENTA),

                        AnsiColor.BG_CYAN: (self.set_background, WinColor.CYAN),

                        AnsiColor.BG_WHITE: (self.set_background, WinColor.GREY),

                        AnsiColor.BG_RESET: (self.set_background, None),

                        AnsiColor.BG_LIGHTBLACK_EX: (self.set_background, WinColor.BLACK, True),

                        AnsiColor.BG_LIGHTRED_EX: (self.set_background, WinColor.RED, True),

                        AnsiColor.BG_LIGHTGREEN_EX: (self.set_background, WinColor.GREEN, True),

                        AnsiColor.BG_LIGHTYELLOW_EX: (self.set_background, WinColor.YELLOW, True),

                        AnsiColor.BG_LIGHTBLUE_EX: (self.set_background, WinColor.BLUE, True),

                        AnsiColor.BG_LIGHTMAGENTA_EX: (self.set_background, WinColor.MAGENTA, True),

                        AnsiColor.BG_LIGHTCYAN_EX: (self.set_background, WinColor.CYAN, True),

                        AnsiColor.BG_LIGHTWHITE_EX: (self.set_background, WinColor.GREY, True),

                    }

                return dict()

        

            # does the win32 call to set the foreground

            def set_foreground(self, fore=None, light=False, on_stderr=False):

                if fore is None:

                    fore = self._default_fore

                self._fore = fore

                # Emulate LIGHT_EX with BRIGHT Style

                if light:

                    self._light |= WinColor.BRIGHT

                else:

                    self._light &= ~WinColor.BRIGHT

                self.set_console(on_stderr=on_stderr)

        

            # does the win32 call to see the background

            def set_background(self, back=None, light=False, on_stderr=False):

                if back is None:

                    back = self._default_back

                self._back = back

                # Emulate LIGHT_EX with BRIGHT_BACKGROUND Style

                if light:

                    self._light |= WinColor.BRIGHT_BACKGROUND

                else:

                    self._light &= ~WinColor.BRIGHT_BACKGROUND

                self.set_console(on_stderr=on_stderr)

        

            # the win32 call to set the console text attribute

            def set_console(self, attrs=None, on_stderr=False):

                if attrs is None:

                    attrs = self.get_attrs()

                handle = Win32Console.STDOUT

                if on_stderr:

                    handle = Win32Console.STDERR

                Win32Console.SetConsoleTextAttribute(handle, attrs)

        

            # gets the current settings for the style and colors selected

            def get_attrs(self):

                return self._fore + self._back * 16 + (self._style | self._light)

        

            # sets the attributes for the style and colors selected

            def set_attrs(self, value):

                self._fore = value & 7

                self._back = (value >> 4) & 7

                self._style = value & (WinColor.BRIGHT | WinColor.BRIGHT_BACKGROUND)

        

            # writes to stream, stripping ANSI if specified

            def write(self, text):

                if self.strip or self.convert:

                    self.write_and_convert(text)

                else:

                    self.write_plain_text(text)

        

            # write the given text to the strip stripping and converting ANSI

            def write_and_convert(self, text):

                cursor = 0

                for match in self.ANSI_CSI_RE.finditer(text):

                    start, end = match.span()

                    if (cursor < start):

                        self.write_plain_text(text, cursor, start)

                    self.convert_ansi(*match.groups())

                    cursor = end

        

                self.write_plain_text(text, cursor, len(text))

        

            # writes plain text to our stream

            def write_plain_text(self, text, start=None, end=None):

                if start is None:

                    self.stream.write(text)

                elif start < end:

                    self.stream.write(text[start:end])

                self.flush()

        

            # converts an ANSI command to a win32 command

            def convert_ansi(self, paramstring, command):

                if self.convert:

                    params = self.extract_params(command, paramstring)

                    self.call_win32(command, params)

            # extracts the parameters in the ANSI command

        

            def extract_params(self, command, paramstring):

                params = tuple(int(p) for p in paramstring.split(';') if len(p) != 0)

                if len(params) == 0:

                    params = (0,)

        

                return params

        

            # calls the win32 apis set_foreground and set_background

            def call_win32(self, command, params):

                if command == 'm':

                    for param in params:

                        if param in self.win32_calls:

                            func_args = self.win32_calls[param]

                            func = func_args[0]

                            args = func_args[1:]

                            kwargs = dict()

                            func(*args, **kwargs)

        

            # logging.handler method we are overriding to emit a record

            def emit(self, record):

                try:

                    if record is None:

                        return

                    msg = self.format(record)

                    if msg is None:

                        return

                    self.write(str(msg))

                    self.write(self.terminator)

                    self.flush()

                except Exception:

                    self.handleError(record)

------

#### Ancestors (in MRO)

* logging.StreamHandler
* logging.Handler
* logging.Filterer

#### Class variables

```python3
ANSI_CSI_RE
```

```python3
terminator
```

#### Instance variables

```python3
name
```

#### Methods

    
#### acquire

```python3
def acquire(
    self
)
```
Acquire the I/O thread lock.

??? example "View Source"
            def acquire(self):

                """

                Acquire the I/O thread lock.

                """

                if self.lock:

                    self.lock.acquire()

    
#### addFilter

```python3
def addFilter(
    self,
    filter
)
```
Add the specified filter to this handler.

??? example "View Source"
            def addFilter(self, filter):

                """

                Add the specified filter to this handler.

                """

                if not (filter in self.filters):

                    self.filters.append(filter)

    
#### call_win32

```python3
def call_win32(
    self,
    command,
    params
)
```

??? example "View Source"
            def call_win32(self, command, params):

                if command == 'm':

                    for param in params:

                        if param in self.win32_calls:

                            func_args = self.win32_calls[param]

                            func = func_args[0]

                            args = func_args[1:]

                            kwargs = dict()

                            func(*args, **kwargs)

    
#### close

```python3
def close(
    self
)
```
Tidy up any resources used by the handler.

This version removes the handler from an internal map of handlers,
_handlers, which is used for handler lookup by name. Subclasses
should ensure that this gets called from overridden close()
methods.

??? example "View Source"
            def close(self):

                """

                Tidy up any resources used by the handler.

        

                This version removes the handler from an internal map of handlers,

                _handlers, which is used for handler lookup by name. Subclasses

                should ensure that this gets called from overridden close()

                methods.

                """

                #get the module data lock, as we're updating a shared structure.

                _acquireLock()

                try:    #unlikely to raise an exception, but you never know...

                    if self._name and self._name in _handlers:

                        del _handlers[self._name]

                finally:

                    _releaseLock()

    
#### convert_ansi

```python3
def convert_ansi(
    self,
    paramstring,
    command
)
```

??? example "View Source"
            def convert_ansi(self, paramstring, command):

                if self.convert:

                    params = self.extract_params(command, paramstring)

                    self.call_win32(command, params)

    
#### createLock

```python3
def createLock(
    self
)
```
Acquire a thread lock for serializing access to the underlying I/O.

??? example "View Source"
            def createLock(self):

                """

                Acquire a thread lock for serializing access to the underlying I/O.

                """

                self.lock = threading.RLock()

                _register_at_fork_reinit_lock(self)

    
#### emit

```python3
def emit(
    self,
    record
)
```
Emit a record.

If a formatter is specified, it is used to format the record.
The record is then written to the stream with a trailing newline.  If
exception information is present, it is formatted using
traceback.print_exception and appended to the stream.  If the stream
has an 'encoding' attribute, it is used to determine how to do the
output to the stream.

??? example "View Source"
            def emit(self, record):

                try:

                    if record is None:

                        return

                    msg = self.format(record)

                    if msg is None:

                        return

                    self.write(str(msg))

                    self.write(self.terminator)

                    self.flush()

                except Exception:

                    self.handleError(record)

    
#### extract_params

```python3
def extract_params(
    self,
    command,
    paramstring
)
```

??? example "View Source"
            def extract_params(self, command, paramstring):

                params = tuple(int(p) for p in paramstring.split(';') if len(p) != 0)

                if len(params) == 0:

                    params = (0,)

        

                return params

    
#### filter

```python3
def filter(
    self,
    record
)
```
Determine if a record is loggable by consulting all the filters.

The default is to allow the record to be logged; any filter can veto
this and the record is then dropped. Returns a zero value if a record
is to be dropped, else non-zero.

.. versionchanged:: 3.2

   Allow filters to be just callables.

??? example "View Source"
            def filter(self, record):

                """

                Determine if a record is loggable by consulting all the filters.

        

                The default is to allow the record to be logged; any filter can veto

                this and the record is then dropped. Returns a zero value if a record

                is to be dropped, else non-zero.

        

                .. versionchanged:: 3.2

        

                   Allow filters to be just callables.

                """

                rv = True

                for f in self.filters:

                    if hasattr(f, 'filter'):

                        result = f.filter(record)

                    else:

                        result = f(record) # assume callable - will raise if not

                    if not result:

                        rv = False

                        break

                return rv

    
#### flush

```python3
def flush(
    self
)
```
Flushes the stream.

??? example "View Source"
            def flush(self):

                """

                Flushes the stream.

                """

                self.acquire()

                try:

                    if self.stream and hasattr(self.stream, "flush"):

                        self.stream.flush()

                finally:

                    self.release()

    
#### format

```python3
def format(
    self,
    record
)
```
Format the specified record.

If a formatter is set, use it. Otherwise, use the default formatter
for the module.

??? example "View Source"
            def format(self, record):

                """

                Format the specified record.

        

                If a formatter is set, use it. Otherwise, use the default formatter

                for the module.

                """

                if self.formatter:

                    fmt = self.formatter

                else:

                    fmt = _defaultFormatter

                return fmt.format(record)

    
#### get_attrs

```python3
def get_attrs(
    self
)
```

??? example "View Source"
            def get_attrs(self):

                return self._fore + self._back * 16 + (self._style | self._light)

    
#### get_name

```python3
def get_name(
    self
)
```

??? example "View Source"
            def get_name(self):

                return self._name

    
#### get_win32_calls

```python3
def get_win32_calls(
    self
)
```

??? example "View Source"
            def get_win32_calls(self):

                if self.convert:

                    return {

                        AnsiColor.BLACK: (self.set_foreground, WinColor.BLACK),

                        AnsiColor.RED: (self.set_foreground, WinColor.RED),

                        AnsiColor.GREEN: (self.set_foreground, WinColor.GREEN),

                        AnsiColor.YELLOW: (self.set_foreground, WinColor.YELLOW),

                        AnsiColor.BLUE: (self.set_foreground, WinColor.BLUE),

                        AnsiColor.MAGENTA: (self.set_foreground, WinColor.MAGENTA),

                        AnsiColor.CYAN: (self.set_foreground, WinColor.CYAN),

                        AnsiColor.WHITE: (self.set_foreground, WinColor.GREY),

                        AnsiColor.RESET: (self.set_foreground, None),

                        AnsiColor.LIGHTBLACK_EX: (self.set_foreground, WinColor.BLACK, True),

                        AnsiColor.LIGHTRED_EX: (self.set_foreground, WinColor.RED, True),

                        AnsiColor.LIGHTGREEN_EX: (self.set_foreground, WinColor.GREEN, True),

                        AnsiColor.LIGHTYELLOW_EX: (self.set_foreground, WinColor.YELLOW, True),

                        AnsiColor.LIGHTBLUE_EX: (self.set_foreground, WinColor.BLUE, True),

                        AnsiColor.LIGHTMAGENTA_EX: (self.set_foreground, WinColor.MAGENTA, True),

                        AnsiColor.LIGHTCYAN_EX: (self.set_foreground, WinColor.CYAN, True),

                        AnsiColor.LIGHTWHITE_EX: (self.set_foreground, WinColor.GREY, True),

                        AnsiColor.BG_BLACK: (self.set_background, WinColor.BLACK),

                        AnsiColor.BG_RED: (self.set_background, WinColor.RED),

                        AnsiColor.BG_GREEN: (self.set_background, WinColor.GREEN),

                        AnsiColor.BG_YELLOW: (self.set_background, WinColor.YELLOW),

                        AnsiColor.BG_BLUE: (self.set_background, WinColor.BLUE),

                        AnsiColor.BG_MAGENTA: (self.set_background, WinColor.MAGENTA),

                        AnsiColor.BG_CYAN: (self.set_background, WinColor.CYAN),

                        AnsiColor.BG_WHITE: (self.set_background, WinColor.GREY),

                        AnsiColor.BG_RESET: (self.set_background, None),

                        AnsiColor.BG_LIGHTBLACK_EX: (self.set_background, WinColor.BLACK, True),

                        AnsiColor.BG_LIGHTRED_EX: (self.set_background, WinColor.RED, True),

                        AnsiColor.BG_LIGHTGREEN_EX: (self.set_background, WinColor.GREEN, True),

                        AnsiColor.BG_LIGHTYELLOW_EX: (self.set_background, WinColor.YELLOW, True),

                        AnsiColor.BG_LIGHTBLUE_EX: (self.set_background, WinColor.BLUE, True),

                        AnsiColor.BG_LIGHTMAGENTA_EX: (self.set_background, WinColor.MAGENTA, True),

                        AnsiColor.BG_LIGHTCYAN_EX: (self.set_background, WinColor.CYAN, True),

                        AnsiColor.BG_LIGHTWHITE_EX: (self.set_background, WinColor.GREY, True),

                    }

                return dict()

    
#### handle

```python3
def handle(
    self,
    record
)
```
Conditionally emit the specified logging record.
Emission depends on filters which may have been added to the handler.
Wrap the actual emission of the record with acquisition/release of
the I/O thread lock. Returns whether the filter passed the record for
emission.

??? example "View Source"
            def handle(self, record):

                """

                Conditionally emit the specified logging record.

                Emission depends on filters which may have been added to the handler.

                Wrap the actual emission of the record with acquisition/release of

                the I/O thread lock. Returns whether the filter passed the record for

                emission.

                """

        

                rv = self.filter(record)

                if rv and record.levelno >= self.level:

                    self.acquire()

                    try:

                        self.emit(record)

                    finally:

                        self.release()

                return rv

    
#### handleError

```python3
def handleError(
    self,
    record
)
```
Handle errors which occur during an emit() call.

This method should be called from handlers when an exception is
encountered during an emit() call. If raiseExceptions is false,
exceptions get silently ignored. This is what is mostly wanted
for a logging system - most users will not care about errors in
the logging system, they are more interested in application errors.
You could, however, replace this with a custom handler if you wish.
The record which was being processed is passed in to this method.

??? example "View Source"
            def handleError(self, record):

                """

                Handle errors which occur during an emit() call.

        

                This method should be called from handlers when an exception is

                encountered during an emit() call. If raiseExceptions is false,

                exceptions get silently ignored. This is what is mostly wanted

                for a logging system - most users will not care about errors in

                the logging system, they are more interested in application errors.

                You could, however, replace this with a custom handler if you wish.

                The record which was being processed is passed in to this method.

                """

                if raiseExceptions and sys.stderr:  # see issue 13807

                    t, v, tb = sys.exc_info()

                    try:

                        sys.stderr.write('--- Logging error ---\n')

                        traceback.print_exception(t, v, tb, None, sys.stderr)

                        sys.stderr.write('Call stack:\n')

                        # Walk the stack frame up until we're out of logging,

                        # so as to print the calling context.

                        frame = tb.tb_frame

                        while (frame and os.path.dirname(frame.f_code.co_filename) ==

                               __path__[0]):

                            frame = frame.f_back

                        if frame:

                            traceback.print_stack(frame, file=sys.stderr)

                        else:

                            # couldn't find the right stack frame, for some reason

                            sys.stderr.write('Logged from file %s, line %s\n' % (

                                             record.filename, record.lineno))

                        # Issue 18671: output logging message and arguments

                        try:

                            sys.stderr.write('Message: %r\n'

                                             'Arguments: %s\n' % (record.msg,

                                                                  record.args))

                        except RecursionError:  # See issue 36272

                            raise

                        except Exception:

                            sys.stderr.write('Unable to print the message and arguments'

                                             ' - possible formatting error.\nUse the'

                                             ' traceback above to help find the error.\n'

                                            )

                    except OSError: #pragma: no cover

                        pass    # see issue 5971

                    finally:

                        del t, v, tb

    
#### release

```python3
def release(
    self
)
```
Release the I/O thread lock.

??? example "View Source"
            def release(self):

                """

                Release the I/O thread lock.

                """

                if self.lock:

                    self.lock.release()

    
#### removeFilter

```python3
def removeFilter(
    self,
    filter
)
```
Remove the specified filter from this handler.

??? example "View Source"
            def removeFilter(self, filter):

                """

                Remove the specified filter from this handler.

                """

                if filter in self.filters:

                    self.filters.remove(filter)

    
#### setFormatter

```python3
def setFormatter(
    self,
    fmt
)
```
Set the formatter for this handler.

??? example "View Source"
            def setFormatter(self, fmt):

                """

                Set the formatter for this handler.

                """

                self.formatter = fmt

    
#### setLevel

```python3
def setLevel(
    self,
    level
)
```
Set the logging level of this handler.  level must be an int or a str.

??? example "View Source"
            def setLevel(self, level):

                """

                Set the logging level of this handler.  level must be an int or a str.

                """

                self.level = _checkLevel(level)

    
#### setStream

```python3
def setStream(
    self,
    stream
)
```
Sets the StreamHandler's stream to the specified value,
if it is different.

Returns the old stream, if the stream was changed, or None
if it wasn't.

??? example "View Source"
            def setStream(self, stream):

                """

                Sets the StreamHandler's stream to the specified value,

                if it is different.

        

                Returns the old stream, if the stream was changed, or None

                if it wasn't.

                """

                if stream is self.stream:

                    result = None

                else:

                    result = self.stream

                    self.acquire()

                    try:

                        self.flush()

                        self.stream = stream

                    finally:

                        self.release()

                return result

    
#### set_attrs

```python3
def set_attrs(
    self,
    value
)
```

??? example "View Source"
            def set_attrs(self, value):

                self._fore = value & 7

                self._back = (value >> 4) & 7

                self._style = value & (WinColor.BRIGHT | WinColor.BRIGHT_BACKGROUND)

    
#### set_background

```python3
def set_background(
    self,
    back=None,
    light=False,
    on_stderr=False
)
```

??? example "View Source"
            def set_background(self, back=None, light=False, on_stderr=False):

                if back is None:

                    back = self._default_back

                self._back = back

                # Emulate LIGHT_EX with BRIGHT_BACKGROUND Style

                if light:

                    self._light |= WinColor.BRIGHT_BACKGROUND

                else:

                    self._light &= ~WinColor.BRIGHT_BACKGROUND

                self.set_console(on_stderr=on_stderr)

    
#### set_console

```python3
def set_console(
    self,
    attrs=None,
    on_stderr=False
)
```

??? example "View Source"
            def set_console(self, attrs=None, on_stderr=False):

                if attrs is None:

                    attrs = self.get_attrs()

                handle = Win32Console.STDOUT

                if on_stderr:

                    handle = Win32Console.STDERR

                Win32Console.SetConsoleTextAttribute(handle, attrs)

    
#### set_foreground

```python3
def set_foreground(
    self,
    fore=None,
    light=False,
    on_stderr=False
)
```

??? example "View Source"
            def set_foreground(self, fore=None, light=False, on_stderr=False):

                if fore is None:

                    fore = self._default_fore

                self._fore = fore

                # Emulate LIGHT_EX with BRIGHT Style

                if light:

                    self._light |= WinColor.BRIGHT

                else:

                    self._light &= ~WinColor.BRIGHT

                self.set_console(on_stderr=on_stderr)

    
#### set_name

```python3
def set_name(
    self,
    name
)
```

??? example "View Source"
            def set_name(self, name):

                _acquireLock()

                try:

                    if self._name in _handlers:

                        del _handlers[self._name]

                    self._name = name

                    if name:

                        _handlers[name] = self

                finally:

                    _releaseLock()

    
#### write

```python3
def write(
    self,
    text
)
```

??? example "View Source"
            def write(self, text):

                if self.strip or self.convert:

                    self.write_and_convert(text)

                else:

                    self.write_plain_text(text)

    
#### write_and_convert

```python3
def write_and_convert(
    self,
    text
)
```

??? example "View Source"
            def write_and_convert(self, text):

                cursor = 0

                for match in self.ANSI_CSI_RE.finditer(text):

                    start, end = match.span()

                    if (cursor < start):

                        self.write_plain_text(text, cursor, start)

                    self.convert_ansi(*match.groups())

                    cursor = end

        

                self.write_plain_text(text, cursor, len(text))

    
#### write_plain_text

```python3
def write_plain_text(
    self,
    text,
    start=None,
    end=None
)
```

??? example "View Source"
            def write_plain_text(self, text, start=None, end=None):

                if start is None:

                    self.stream.write(text)

                elif start < end:

                    self.stream.write(text[start:end])

                self.flush()

### Win32Console

```python3
class Win32Console(
    /,
    *args,
    **kwargs
)
```

??? example "View Source"
            class Win32Console(object):

                _GetConsoleScreenBufferInfo = windll.kernel32.GetConsoleScreenBufferInfo

                _SetConsoleTextAttribute = windll.kernel32.SetConsoleTextAttribute

                _SetConsoleTextAttribute.argtypes = [

                    wintypes.HANDLE,

                    wintypes.WORD,

                ]

                _SetConsoleTextAttribute.restype = wintypes.BOOL

                _GetStdHandle = windll.kernel32.GetStdHandle

                _GetStdHandle.argtypes = [

                    wintypes.DWORD,

                ]

                _GetStdHandle.restype = wintypes.HANDLE

        

                # from winbase.h

                STDOUT = -11

                STDERR = -12

        

                @staticmethod

                def _winapi_test(handle):

                    csbi = CONSOLE_SCREEN_BUFFER_INFO()

                    success = Win32Console._GetConsoleScreenBufferInfo(

                        handle, byref(csbi))

                    return bool(success)

        

                @staticmethod

                def winapi_test():

                    return any(Win32Console._winapi_test(h) for h in

                               (Win32Console._GetStdHandle(Win32Console.STDOUT),

                                Win32Console._GetStdHandle(Win32Console.STDERR)))

        

                @staticmethod

                def GetConsoleScreenBufferInfo(stream_id=STDOUT):

                    handle = Win32Console._GetStdHandle(stream_id)

                    csbi = CONSOLE_SCREEN_BUFFER_INFO()

                    Win32Console._GetConsoleScreenBufferInfo(

                        handle, byref(csbi))

                    return csbi

        

                @staticmethod

                def SetConsoleTextAttribute(stream_id, attrs):

                    handle = Win32Console._GetStdHandle(stream_id)

                    return Win32Console._SetConsoleTextAttribute(handle, attrs)

------

#### Class variables

```python3
STDERR
```

```python3
STDOUT
```

#### Static methods

    
#### GetConsoleScreenBufferInfo

```python3
def GetConsoleScreenBufferInfo(
    stream_id=-11
)
```

??? example "View Source"
                @staticmethod

                def GetConsoleScreenBufferInfo(stream_id=STDOUT):

                    handle = Win32Console._GetStdHandle(stream_id)

                    csbi = CONSOLE_SCREEN_BUFFER_INFO()

                    Win32Console._GetConsoleScreenBufferInfo(

                        handle, byref(csbi))

                    return csbi

    
#### SetConsoleTextAttribute

```python3
def SetConsoleTextAttribute(
    stream_id,
    attrs
)
```

??? example "View Source"
                @staticmethod

                def SetConsoleTextAttribute(stream_id, attrs):

                    handle = Win32Console._GetStdHandle(stream_id)

                    return Win32Console._SetConsoleTextAttribute(handle, attrs)

    
#### winapi_test

```python3
def winapi_test(
    
)
```

??? example "View Source"
                @staticmethod

                def winapi_test():

                    return any(Win32Console._winapi_test(h) for h in

                               (Win32Console._GetStdHandle(Win32Console.STDOUT),

                                Win32Console._GetStdHandle(Win32Console.STDERR)))

### WinColor

```python3
class WinColor(
    /,
    *args,
    **kwargs
)
```

??? example "View Source"
        class WinColor(object):

            BLACK = 0

            BLUE = 1

            GREEN = 2

            CYAN = 3

            RED = 4

            MAGENTA = 5

            YELLOW = 6

            GREY = 7

            NORMAL = 0x00  # dim text, dim background

            BRIGHT = 0x08  # bright text, dim background

            BRIGHT_BACKGROUND = 0x80  # dim text, bright background

------

#### Class variables

```python3
BLACK
```

```python3
BLUE
```

```python3
BRIGHT
```

```python3
BRIGHT_BACKGROUND
```

```python3
CYAN
```

```python3
GREEN
```

```python3
GREY
```

```python3
MAGENTA
```

```python3
NORMAL
```

```python3
RED
```

```python3
YELLOW
```