Module edk2toollib.log.junit_report_format
==========================================

??? example "View Source"
        ##

        # junit_report_format

        # This module contains support for Outputting Junit test results xml.

        #

        # Used to support CI/CD and exporting test results for other tools.

        # This does test report generation without being a test runner.

        #

        # Copyright (c) Microsoft Corporation

        #

        # SPDX-License-Identifier: BSD-2-Clause-Patent

        ##

        import time

        from xml.sax.saxutils import escape

        

        

        class JunitReportError(object):

            def __init__(self, type, msg):

                self.Message = escape(msg.strip(), {'"': "&quot;"})

                self.Type = escape(type.strip(), {'"': "&quot;"})

        

        

        class JunitReportFailure(object):

            def __init__(self, type, msg):

                self.Message = escape(msg.strip(), {'"': "&quot;"})

                self.Type = escape(type.strip(), {'"': "&quot;"})

        

        ##

        # Test Case class

        #

        ##

        

        

        class JunitReportTestCase(object):

            NEW = 1

            SKIPPED = 2

            FAILED = 3

            ERROR = 4

            SUCCESS = 5

        

            def __init__(self, Name, ClassName):

                self.Name = escape(Name.strip(), {'"': "&quot;"})

                self.ClassName = escape(ClassName.strip(), {'"': "&quot;"})

                self.Time = 0

                self.Status = JunitReportTestCase.NEW

        

                self.FailureMsg = None

                self.ErrorMsg = None

                self._TestSuite = None

                self.StdErr = ""

                self.StdOut = ""

                self._StartTime = time.time()

        

            def SetFailed(self, Msg, Type):

                if(self.Status != JunitReportTestCase.NEW):

                    raise Exception("Can't Set to failed.  State must be in NEW")

                self.Time = time.time() - self._StartTime

                self.Status = JunitReportTestCase.FAILED

                self.FailureMsg = JunitReportFailure(Type, Msg)

        

            def SetError(self, Msg, Type):

                if(self.Status != JunitReportTestCase.NEW):

                    raise Exception("Can't Set to error.  State must be in NEW")

                self.Time = time.time() - self._StartTime

                self.Status = JunitReportTestCase.ERROR

                self.ErrorMsg = JunitReportError(Type, Msg)

        

            def SetSuccess(self):

                if(self.Status != JunitReportTestCase.NEW):

                    raise Exception("Can't Set to success.  State must be in NEW")

                self.Status = JunitReportTestCase.SUCCESS

                self.Time = time.time() - self._StartTime

        

            def SetSkipped(self):

                if(self.Status != JunitReportTestCase.NEW):

                    raise Exception("Can't Set to skipped.  State must be in NEW")

                self.Status = JunitReportTestCase.SKIPPED

                self.Time = time.time() - self._StartTime

        

            def LogStdOut(self, msg):

                self.StdOut += escape(msg.strip()) + "\n "

        

            def LogStdError(self, msg):

                self.StdErr += escape(msg.strip()) + "\n "

        

            def Output(self, outstream):

                outstream.write('<testcase classname="{0}" name="{1}" time="{2}">'.format(self.ClassName, self.Name, self.Time))

                if self.Status == JunitReportTestCase.SKIPPED:

                    outstream.write('<skipped type="skipped">')

                    outstream.write(self.StdOut)

                    outstream.write('</skipped>')

                elif self.Status == JunitReportTestCase.FAILED:

                    outstream.write('<failure message="{0}" type="{1}" />'.format(self.FailureMsg.Message,

                                                                                  self.FailureMsg.Type))

                elif self.Status == JunitReportTestCase.ERROR:

                    outstream.write('<error message="{0}" type="{1}" />'.format(self.ErrorMsg.Message, self.ErrorMsg.Type))

                elif self.Status != JunitReportTestCase.SUCCESS:

                    raise Exception("Can't output a testcase {0}.{1} in invalid state {2}".format(self.ClassName,

                                                                                                  self.Name, self.Status))

        

                outstream.write('<system-out>' + self.StdOut + '</system-out>')

                outstream.write('<system-err>' + self.StdErr + '</system-err>')

                outstream.write('</testcase>')

        

        

        ##

        # Test Suite class.  Create new suites by using the JunitTestReport Object

        #

        #

        ##

        class JunitReportTestSuite(object):

            def __init__(self, Name, Package, Id):

                self.Name = escape(Name.strip(), {'"': "&quot;"})

                self.Package = escape(Package.strip(), {'"': "&quot;"})

                self.TestId = Id

                self.TestCases = []

        

            def create_new_testcase(self, name, classname):

                tc = JunitReportTestCase(name, classname)

                self.TestCases.append(tc)

                tc._TestSuite = self

                return tc

        

            def Output(self, outstream):

                Errors = 0

                Failures = 0

                Skipped = 0

                Tests = len(self.TestCases)

        

                for a in self.TestCases:

                    if(a.Status == JunitReportTestCase.FAILED):

                        Failures += 1

                    elif(a.Status == JunitReportTestCase.ERROR):

                        Errors += 1

                    elif(a.Status == JunitReportTestCase.SKIPPED):

                        Skipped += 1

        

                outstream.write('<testsuite id="{0}" name="{1}" package="{2}" errors="{3}" tests="{4}" '

                                'failures="{5}" skipped="{6}">'.format(self.TestId, self.Name, self.Package,

                                                                       Errors, Tests, Failures, Skipped))

        

                for a in self.TestCases:

                    a.Output(outstream)

        

                outstream.write('</testsuite>')

        

        ##

        # Test Report.  Top level object test reporting.

        #

        #

        ##

        

        

        class JunitTestReport(object):

            def __init__(self):

                self.TestSuites = []

        

            def create_new_testsuite(self, name, package):

                id = len(self.TestSuites)

                ts = JunitReportTestSuite(name, package, id)

                self.TestSuites.append(ts)

                return ts

        

            def Output(self, filepath):

                f = open(filepath, "w")

                f.write('')

                f.write('<?xml version="1.0" encoding="UTF-8"?>')

                f.write('<testsuites>')

                for a in self.TestSuites:

                    a.Output(f)

                f.write('</testsuites>')

                f.close()

Classes
-------

### JunitReportError

```python3
class JunitReportError(
    type,
    msg
)
```

??? example "View Source"
        class JunitReportError(object):

            def __init__(self, type, msg):

                self.Message = escape(msg.strip(), {'"': "&quot;"})

                self.Type = escape(type.strip(), {'"': "&quot;"})

------

### JunitReportFailure

```python3
class JunitReportFailure(
    type,
    msg
)
```

??? example "View Source"
        class JunitReportFailure(object):

            def __init__(self, type, msg):

                self.Message = escape(msg.strip(), {'"': "&quot;"})

                self.Type = escape(type.strip(), {'"': "&quot;"})

------

### JunitReportTestCase

```python3
class JunitReportTestCase(
    Name,
    ClassName
)
```

??? example "View Source"
        class JunitReportTestCase(object):

            NEW = 1

            SKIPPED = 2

            FAILED = 3

            ERROR = 4

            SUCCESS = 5

        

            def __init__(self, Name, ClassName):

                self.Name = escape(Name.strip(), {'"': "&quot;"})

                self.ClassName = escape(ClassName.strip(), {'"': "&quot;"})

                self.Time = 0

                self.Status = JunitReportTestCase.NEW

        

                self.FailureMsg = None

                self.ErrorMsg = None

                self._TestSuite = None

                self.StdErr = ""

                self.StdOut = ""

                self._StartTime = time.time()

        

            def SetFailed(self, Msg, Type):

                if(self.Status != JunitReportTestCase.NEW):

                    raise Exception("Can't Set to failed.  State must be in NEW")

                self.Time = time.time() - self._StartTime

                self.Status = JunitReportTestCase.FAILED

                self.FailureMsg = JunitReportFailure(Type, Msg)

        

            def SetError(self, Msg, Type):

                if(self.Status != JunitReportTestCase.NEW):

                    raise Exception("Can't Set to error.  State must be in NEW")

                self.Time = time.time() - self._StartTime

                self.Status = JunitReportTestCase.ERROR

                self.ErrorMsg = JunitReportError(Type, Msg)

        

            def SetSuccess(self):

                if(self.Status != JunitReportTestCase.NEW):

                    raise Exception("Can't Set to success.  State must be in NEW")

                self.Status = JunitReportTestCase.SUCCESS

                self.Time = time.time() - self._StartTime

        

            def SetSkipped(self):

                if(self.Status != JunitReportTestCase.NEW):

                    raise Exception("Can't Set to skipped.  State must be in NEW")

                self.Status = JunitReportTestCase.SKIPPED

                self.Time = time.time() - self._StartTime

        

            def LogStdOut(self, msg):

                self.StdOut += escape(msg.strip()) + "\n "

        

            def LogStdError(self, msg):

                self.StdErr += escape(msg.strip()) + "\n "

        

            def Output(self, outstream):

                outstream.write('<testcase classname="{0}" name="{1}" time="{2}">'.format(self.ClassName, self.Name, self.Time))

                if self.Status == JunitReportTestCase.SKIPPED:

                    outstream.write('<skipped type="skipped">')

                    outstream.write(self.StdOut)

                    outstream.write('</skipped>')

                elif self.Status == JunitReportTestCase.FAILED:

                    outstream.write('<failure message="{0}" type="{1}" />'.format(self.FailureMsg.Message,

                                                                                  self.FailureMsg.Type))

                elif self.Status == JunitReportTestCase.ERROR:

                    outstream.write('<error message="{0}" type="{1}" />'.format(self.ErrorMsg.Message, self.ErrorMsg.Type))

                elif self.Status != JunitReportTestCase.SUCCESS:

                    raise Exception("Can't output a testcase {0}.{1} in invalid state {2}".format(self.ClassName,

                                                                                                  self.Name, self.Status))

        

                outstream.write('<system-out>' + self.StdOut + '</system-out>')

                outstream.write('<system-err>' + self.StdErr + '</system-err>')

                outstream.write('</testcase>')

------

#### Class variables

```python3
ERROR
```

```python3
FAILED
```

```python3
NEW
```

```python3
SKIPPED
```

```python3
SUCCESS
```

#### Methods

    
#### LogStdError

```python3
def LogStdError(
    self,
    msg
)
```

??? example "View Source"
            def LogStdError(self, msg):

                self.StdErr += escape(msg.strip()) + "\n "

    
#### LogStdOut

```python3
def LogStdOut(
    self,
    msg
)
```

??? example "View Source"
            def LogStdOut(self, msg):

                self.StdOut += escape(msg.strip()) + "\n "

    
#### Output

```python3
def Output(
    self,
    outstream
)
```

??? example "View Source"
            def Output(self, outstream):

                outstream.write('<testcase classname="{0}" name="{1}" time="{2}">'.format(self.ClassName, self.Name, self.Time))

                if self.Status == JunitReportTestCase.SKIPPED:

                    outstream.write('<skipped type="skipped">')

                    outstream.write(self.StdOut)

                    outstream.write('</skipped>')

                elif self.Status == JunitReportTestCase.FAILED:

                    outstream.write('<failure message="{0}" type="{1}" />'.format(self.FailureMsg.Message,

                                                                                  self.FailureMsg.Type))

                elif self.Status == JunitReportTestCase.ERROR:

                    outstream.write('<error message="{0}" type="{1}" />'.format(self.ErrorMsg.Message, self.ErrorMsg.Type))

                elif self.Status != JunitReportTestCase.SUCCESS:

                    raise Exception("Can't output a testcase {0}.{1} in invalid state {2}".format(self.ClassName,

                                                                                                  self.Name, self.Status))

        

                outstream.write('<system-out>' + self.StdOut + '</system-out>')

                outstream.write('<system-err>' + self.StdErr + '</system-err>')

                outstream.write('</testcase>')

    
#### SetError

```python3
def SetError(
    self,
    Msg,
    Type
)
```

??? example "View Source"
            def SetError(self, Msg, Type):

                if(self.Status != JunitReportTestCase.NEW):

                    raise Exception("Can't Set to error.  State must be in NEW")

                self.Time = time.time() - self._StartTime

                self.Status = JunitReportTestCase.ERROR

                self.ErrorMsg = JunitReportError(Type, Msg)

    
#### SetFailed

```python3
def SetFailed(
    self,
    Msg,
    Type
)
```

??? example "View Source"
            def SetFailed(self, Msg, Type):

                if(self.Status != JunitReportTestCase.NEW):

                    raise Exception("Can't Set to failed.  State must be in NEW")

                self.Time = time.time() - self._StartTime

                self.Status = JunitReportTestCase.FAILED

                self.FailureMsg = JunitReportFailure(Type, Msg)

    
#### SetSkipped

```python3
def SetSkipped(
    self
)
```

??? example "View Source"
            def SetSkipped(self):

                if(self.Status != JunitReportTestCase.NEW):

                    raise Exception("Can't Set to skipped.  State must be in NEW")

                self.Status = JunitReportTestCase.SKIPPED

                self.Time = time.time() - self._StartTime

    
#### SetSuccess

```python3
def SetSuccess(
    self
)
```

??? example "View Source"
            def SetSuccess(self):

                if(self.Status != JunitReportTestCase.NEW):

                    raise Exception("Can't Set to success.  State must be in NEW")

                self.Status = JunitReportTestCase.SUCCESS

                self.Time = time.time() - self._StartTime

### JunitReportTestSuite

```python3
class JunitReportTestSuite(
    Name,
    Package,
    Id
)
```

??? example "View Source"
        class JunitReportTestSuite(object):

            def __init__(self, Name, Package, Id):

                self.Name = escape(Name.strip(), {'"': "&quot;"})

                self.Package = escape(Package.strip(), {'"': "&quot;"})

                self.TestId = Id

                self.TestCases = []

        

            def create_new_testcase(self, name, classname):

                tc = JunitReportTestCase(name, classname)

                self.TestCases.append(tc)

                tc._TestSuite = self

                return tc

        

            def Output(self, outstream):

                Errors = 0

                Failures = 0

                Skipped = 0

                Tests = len(self.TestCases)

        

                for a in self.TestCases:

                    if(a.Status == JunitReportTestCase.FAILED):

                        Failures += 1

                    elif(a.Status == JunitReportTestCase.ERROR):

                        Errors += 1

                    elif(a.Status == JunitReportTestCase.SKIPPED):

                        Skipped += 1

        

                outstream.write('<testsuite id="{0}" name="{1}" package="{2}" errors="{3}" tests="{4}" '

                                'failures="{5}" skipped="{6}">'.format(self.TestId, self.Name, self.Package,

                                                                       Errors, Tests, Failures, Skipped))

        

                for a in self.TestCases:

                    a.Output(outstream)

        

                outstream.write('</testsuite>')

------

#### Methods

    
#### Output

```python3
def Output(
    self,
    outstream
)
```

??? example "View Source"
            def Output(self, outstream):

                Errors = 0

                Failures = 0

                Skipped = 0

                Tests = len(self.TestCases)

        

                for a in self.TestCases:

                    if(a.Status == JunitReportTestCase.FAILED):

                        Failures += 1

                    elif(a.Status == JunitReportTestCase.ERROR):

                        Errors += 1

                    elif(a.Status == JunitReportTestCase.SKIPPED):

                        Skipped += 1

        

                outstream.write('<testsuite id="{0}" name="{1}" package="{2}" errors="{3}" tests="{4}" '

                                'failures="{5}" skipped="{6}">'.format(self.TestId, self.Name, self.Package,

                                                                       Errors, Tests, Failures, Skipped))

        

                for a in self.TestCases:

                    a.Output(outstream)

        

                outstream.write('</testsuite>')

    
#### create_new_testcase

```python3
def create_new_testcase(
    self,
    name,
    classname
)
```

??? example "View Source"
            def create_new_testcase(self, name, classname):

                tc = JunitReportTestCase(name, classname)

                self.TestCases.append(tc)

                tc._TestSuite = self

                return tc

### JunitTestReport

```python3
class JunitTestReport(
    
)
```

??? example "View Source"
        class JunitTestReport(object):

            def __init__(self):

                self.TestSuites = []

        

            def create_new_testsuite(self, name, package):

                id = len(self.TestSuites)

                ts = JunitReportTestSuite(name, package, id)

                self.TestSuites.append(ts)

                return ts

        

            def Output(self, filepath):

                f = open(filepath, "w")

                f.write('')

                f.write('<?xml version="1.0" encoding="UTF-8"?>')

                f.write('<testsuites>')

                for a in self.TestSuites:

                    a.Output(f)

                f.write('</testsuites>')

                f.close()

------

#### Methods

    
#### Output

```python3
def Output(
    self,
    filepath
)
```

??? example "View Source"
            def Output(self, filepath):

                f = open(filepath, "w")

                f.write('')

                f.write('<?xml version="1.0" encoding="UTF-8"?>')

                f.write('<testsuites>')

                for a in self.TestSuites:

                    a.Output(f)

                f.write('</testsuites>')

                f.close()

    
#### create_new_testsuite

```python3
def create_new_testsuite(
    self,
    name,
    package
)
```

??? example "View Source"
            def create_new_testsuite(self, name, package):

                id = len(self.TestSuites)

                ts = JunitReportTestSuite(name, package, id)

                self.TestSuites.append(ts)

                return ts