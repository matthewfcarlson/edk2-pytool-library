Module edk2toollib.log.file_handler
===================================

??? example "View Source"
        ##

        # Handle basic logging outputting to files

        #

        # Copyright (c) Microsoft Corporation

        #

        # SPDX-License-Identifier: BSD-2-Clause-Patent

        ##

        

        import logging

        

        

        class FileHandler(logging.FileHandler):

            def __init__(self, filename, mode='w+'):

                logging.FileHandler.__init__(self, filename, mode=mode)

        

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

Classes
-------

### FileHandler

```python3
class FileHandler(
    filename,
    mode='w+'
)
```

A handler class which writes formatted logging records to disk files.

??? example "View Source"
        class FileHandler(logging.FileHandler):

            def __init__(self, filename, mode='w+'):

                logging.FileHandler.__init__(self, filename, mode=mode)

        

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

------

#### Ancestors (in MRO)

* logging.FileHandler
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
Closes the stream.

??? example "View Source"
            def close(self):

                """

                Closes the stream.

                """

                self.acquire()

                try:

                    try:

                        if self.stream:

                            try:

                                self.flush()

                            finally:

                                stream = self.stream

                                self.stream = None

                                if hasattr(stream, "close"):

                                    stream.close()

                    finally:

                        # Issue #19523: call unconditionally to

                        # prevent a handler leak when delay is set

                        StreamHandler.close(self)

                finally:

                    self.release()

    
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

If the stream was not opened because 'delay' was specified in the
constructor, open it before calling the superclass's emit.

??? example "View Source"
            def emit(self, record):

                """

                Emit a record.

        

                If the stream was not opened because 'delay' was specified in the

                constructor, open it before calling the superclass's emit.

                """

                if self.stream is None:

                    self.stream = self._open()

                StreamHandler.emit(self, record)

    
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