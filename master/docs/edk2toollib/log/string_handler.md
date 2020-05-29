Module edk2toollib.log.string_handler
=====================================

??? example "View Source"
        ##

        # Handle basic logging by streaming into stringIO

        #

        # Copyright (c) Microsoft Corporation

        #

        # SPDX-License-Identifier: BSD-2-Clause-Patent

        ##

        import logging

        import io

        

        

        class StringStreamHandler(logging.StreamHandler):

            terminator = '\n'

        

            def __init__(self):

                logging.Handler.__init__(self)

                self.stream = io.StringIO()

        

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

        

            def readlines(self, hint=-1):

                return self.stream.readlines(hint)

        

            def seek_start(self):

                self.stream.seek(0, 0)

        

            def seek_end(self):

                self.stream.seek(0, io.SEEK_END)

        

            def seek(self, offset, whence):

                return self.stream.seek(offset, whence)

Classes
-------

### StringStreamHandler

```python3
class StringStreamHandler(
    
)
```

A handler class which writes logging records, appropriately formatted,
to a stream. Note that this class does not close the stream, as
sys.stdout or sys.stderr may be used.

??? example "View Source"
        class StringStreamHandler(logging.StreamHandler):

            terminator = '\n'

        

            def __init__(self):

                logging.Handler.__init__(self)

                self.stream = io.StringIO()

        

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

        

            def readlines(self, hint=-1):

                return self.stream.readlines(hint)

        

            def seek_start(self):

                self.stream.seek(0, 0)

        

            def seek_end(self):

                self.stream.seek(0, io.SEEK_END)

        

            def seek(self, offset, whence):

                return self.stream.seek(offset, whence)

------

#### Ancestors (in MRO)

* logging.StreamHandler
* logging.Handler
* logging.Filterer

#### Class variables

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

                """

                Emit a record.

        

                If a formatter is specified, it is used to format the record.

                The record is then written to the stream with a trailing newline.  If

                exception information is present, it is formatted using

                traceback.print_exception and appended to the stream.  If the stream

                has an 'encoding' attribute, it is used to determine how to do the

                output to the stream.

                """

                try:

                    msg = self.format(record)

                    stream = self.stream

                    # issue 35046: merged two stream.writes into one.

                    stream.write(msg + self.terminator)

                    self.flush()

                except RecursionError:  # See issue 36272

                    raise

                except Exception:

                    self.handleError(record)

    
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

    
#### get_name

```python3
def get_name(
    self
)
```

??? example "View Source"
            def get_name(self):

                return self._name

    
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

    
#### readlines

```python3
def readlines(
    self,
    hint=-1
)
```

??? example "View Source"
            def readlines(self, hint=-1):

                return self.stream.readlines(hint)

    
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

    
#### seek

```python3
def seek(
    self,
    offset,
    whence
)
```

??? example "View Source"
            def seek(self, offset, whence):

                return self.stream.seek(offset, whence)

    
#### seek_end

```python3
def seek_end(
    self
)
```

??? example "View Source"
            def seek_end(self):

                self.stream.seek(0, io.SEEK_END)

    
#### seek_start

```python3
def seek_start(
    self
)
```

??? example "View Source"
            def seek_start(self):

                self.stream.seek(0, 0)

    
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