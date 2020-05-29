Module edk2toollib.uefi.edk2.parsers.dec_parser
===============================================

??? example "View Source"
        # @file dec_parser.py

        # Code to help parse DEC file

        #

        # Copyright (c) Microsoft Corporation

        #

        # SPDX-License-Identifier: BSD-2-Clause-Patent

        ##

        import os

        from edk2toollib.uefi.edk2.parsers.base_parser import HashFileParser

        from edk2toollib.uefi.edk2.parsers.guid_parser import GuidParser

        

        

        class LibraryClassDeclarationEntry():

        

            def __init__(self, packagename: str, rawtext: str = None):

                """Init a library Class Declaration Entry"""

                self.path = ""

                self.name = ""

                self.package_name = packagename

                if (rawtext is not None):

                    self._parse(rawtext)

        

            def _parse(self, rawtext: str) -> None:

                """Parses the rawtext line to collect the Library Class declaration

                   information (name and package root relative path).

        

                Args:

                  rawtext: str

                  expected format is <library class name> | <package relative path to header file>

        

                Returns:

                  None

        

                """

                t = rawtext.partition("|")

                self.name = t[0].strip()

                self.path = t[2].strip()

        

        

        class GuidedDeclarationEntry():

            """A baseclass for declaration types that have a name and guid."""

            PROTOCOL = 1

            PPI = 2

            GUID = 3

        

            def __init__(self, packagename: str, rawtext: str = None):

                """Init a protocol/Ppi/or Guid declaration entry"""

                self.name = ""

                self.guidstring = ""

                self.guid = None

                self.package_name = packagename

                if(rawtext is not None):

                    self._parse(rawtext)

        

            def _parse(self, rawtext: str) -> None:

                """Parses the name and guid of a declaration

        

                Args:

                  rawtext: str:

        

                Returns:

        

                """

                t = rawtext.partition("=")

                self.name = t[0].strip()

                self.guidstring = t[2].strip()

                self.guid = GuidParser.uuid_from_guidstring(self.guidstring)

                if(self.guid is None):

                    raise ValueError("Could not parse guid")

        

        

        class ProtocolDeclarationEntry(GuidedDeclarationEntry):

        

            def __init__(self, packagename: str, rawtext: str = None):

                """Init a protocol declaration entry"""

                super().__init__(packagename, rawtext)

                self.type = GuidedDeclarationEntry.PROTOCOL

        

        

        class PpiDeclarationEntry(GuidedDeclarationEntry):

        

            def __init__(self, packagename: str, rawtext: str = None):

                """Init a Ppi declaration entry"""

                super().__init__(packagename, rawtext)

                self.type = GuidedDeclarationEntry.PPI

        

        

        class GuidDeclarationEntry(GuidedDeclarationEntry):

        

            def __init__(self, packagename: str, rawtext: str = None):

                """Init a Ppi declaration entry"""

                super().__init__(packagename, rawtext)

                self.type = GuidedDeclarationEntry.GUID

        

        

        class PcdDeclarationEntry():

        

            def __init__(self, packagename: str, rawtext: str = None):

                """Creates a PCD Declaration Entry for one PCD"""

                self.token_space_name = ""

                self.name = ""

                self.default_value = ""

                self.type = ""

                self.id = ""

                self.package_name = packagename

                if (rawtext is not None):

                    self._parse(rawtext)

        

            def _parse(self, rawtext: str):

                """

        

                Args:

                  rawtext: str:

        

                Returns:

        

                """

                sp = rawtext.partition(".")

                self.token_space_name = sp[0].strip()

                op = sp[2].split("|")

                # if it's 2 long, we need to check that it's a structured PCD

                if(len(op) == 2 and op[0].count(".") > 0):

                    pass

                # otherwise it needs at least 4 parts

                elif(len(op) < 4):

                    raise Exception(f"Too few parts: {op}")

                # but also less than 5

                elif(len(op) > 5):

                    raise Exception(f"Too many parts: {rawtext}")

                elif(len(op) == 5 and op[4].strip() != '{'):

                    raise Exception(f"Too many parts: {rawtext}")

        

                self.name = op[0].strip()

                self.default_value = op[1].strip()

                # if we don't know what the type and id, it's because it's structured

                self.type = op[2].strip() if len(op) > 2 else "STRUCTURED_PCD"

                self.id = op[3].strip() if len(op) > 2 else "STRUCTURED_PCD"

        

        

        class DecParser(HashFileParser):

            """Parses an EDK2 DEC file"""

        

            def __init__(self):

                HashFileParser.__init__(self, 'DecParser')

                self.Lines = []

                self.Parsed = False

                self.Dict = {}

                self.LibraryClasses = []

                self.PPIs = []

                self.Protocols = []

                self.Guids = []

                self.Pcds = []

                self.IncludePaths = []

                self.Path = ""

                self.PackageName = None

        

            def _Parse(self) -> None:

        

                InDefinesSection = False

                InLibraryClassSection = False

                InProtocolsSection = False

                InGuidsSection = False

                InPPISection = False

                InPcdSection = False

                InStructuredPcdDeclaration = False

                InIncludesSection = False

        

                for line in self.Lines:

                    sline = self.StripComment(line)

        

                    if(sline is None or len(sline) < 1):

                        continue

        

                    if InDefinesSection:

                        if sline.strip()[0] == '[':

                            InDefinesSection = False

                        else:

                            if sline.count("=") == 1:

                                tokens = sline.split('=', 1)

                                self.Dict[tokens[0].strip()] = tokens[1].strip()

                                if(self.PackageName is None and tokens[0].strip() == "PACKAGE_NAME"):

                                    self.PackageName = self.Dict["PACKAGE_NAME"]

                                continue

        

                    elif InLibraryClassSection:

                        if sline.strip()[0] == '[':

                            InLibraryClassSection = False

                        else:

                            t = LibraryClassDeclarationEntry(self.PackageName, sline)

                            self.LibraryClasses.append(t)

                            continue

        

                    elif InProtocolsSection:

                        if sline.strip()[0] == '[':

                            InProtocolsSection = False

                        else:

                            t = ProtocolDeclarationEntry(self.PackageName, sline)

                            self.Protocols.append(t)

                            continue

        

                    elif InGuidsSection:

                        if sline.strip()[0] == '[':

                            InGuidsSection = False

                        else:

                            t = GuidDeclarationEntry(self.PackageName, sline)

                            self.Guids.append(t)

                            continue

        

                    elif InPcdSection:

                        if sline.strip()[0] == '[':

                            InPcdSection = False

                        elif sline.strip()[0] == '}':

                            InStructuredPcdDeclaration = False

                        else:

                            if InStructuredPcdDeclaration:

                                continue

                            t = PcdDeclarationEntry(self.PackageName, sline)

                            self.Pcds.append(t)

                            if sline.rstrip()[-1] == '{':

                                InStructuredPcdDeclaration = True

                            continue

        

                    elif InIncludesSection:

                        if sline.strip()[0] == '[':

                            InIncludesSection = False

                        else:

                            self.IncludePaths.append(sline.strip())

                            continue

        

                    elif InPPISection:

                        if (sline.strip()[0] == '['):

                            InPPISection = False

                        else:

                            t = PpiDeclarationEntry(self.PackageName, sline)

                            self.PPIs.append(t)

                            continue

        

                    # check for different sections

                    if sline.strip().lower().startswith('[defines'):

                        InDefinesSection = True

        

                    elif sline.strip().lower().startswith('[libraryclasses'):

                        InLibraryClassSection = True

        

                    elif sline.strip().lower().startswith('[protocols'):

                        InProtocolsSection = True

        

                    elif sline.strip().lower().startswith('[guids'):

                        InGuidsSection = True

        

                    elif sline.strip().lower().startswith('[ppis'):

                        InPPISection = True

        

                    elif sline.strip().lower().startswith('[pcd'):

                        InPcdSection = True

        

                    elif sline.strip().lower().startswith('[includes'):

                        InIncludesSection = True

        

                self.Parsed = True

        

            def ParseStream(self, stream) -> None:

                """

                parse the supplied IO as a DEC file

                Args:

                    stream: a file-like/stream object in which DEC file contents can be read

        

                Returns:

                    None - Existing object now contains parsed data

        

                """

                self.Path = "None:stream_given"

                self.Lines = stream.readlines()

                self._Parse()

        

            def ParseFile(self, filepath: str) -> None:

                """

                Parse the supplied file.

                Args:

                  filepath: path to dec file to parse.  Can be either an absolute path or

                  relative to your CWD

        

                Returns:

                  None - Existing object now contains parsed data

        

                """

                self.Logger.debug("Parsing file: %s" % filepath)

                if(not os.path.isabs(filepath)):

                    fp = self.FindPath(filepath)

                else:

                    fp = filepath

                self.Path = fp

        

                f = open(fp, "r")

                self.Lines = f.readlines()

                f.close()

                self._Parse()

Classes
-------

### DecParser

```python3
class DecParser(
    
)
```

Parses an EDK2 DEC file

??? example "View Source"
        class DecParser(HashFileParser):

            """Parses an EDK2 DEC file"""

        

            def __init__(self):

                HashFileParser.__init__(self, 'DecParser')

                self.Lines = []

                self.Parsed = False

                self.Dict = {}

                self.LibraryClasses = []

                self.PPIs = []

                self.Protocols = []

                self.Guids = []

                self.Pcds = []

                self.IncludePaths = []

                self.Path = ""

                self.PackageName = None

        

            def _Parse(self) -> None:

        

                InDefinesSection = False

                InLibraryClassSection = False

                InProtocolsSection = False

                InGuidsSection = False

                InPPISection = False

                InPcdSection = False

                InStructuredPcdDeclaration = False

                InIncludesSection = False

        

                for line in self.Lines:

                    sline = self.StripComment(line)

        

                    if(sline is None or len(sline) < 1):

                        continue

        

                    if InDefinesSection:

                        if sline.strip()[0] == '[':

                            InDefinesSection = False

                        else:

                            if sline.count("=") == 1:

                                tokens = sline.split('=', 1)

                                self.Dict[tokens[0].strip()] = tokens[1].strip()

                                if(self.PackageName is None and tokens[0].strip() == "PACKAGE_NAME"):

                                    self.PackageName = self.Dict["PACKAGE_NAME"]

                                continue

        

                    elif InLibraryClassSection:

                        if sline.strip()[0] == '[':

                            InLibraryClassSection = False

                        else:

                            t = LibraryClassDeclarationEntry(self.PackageName, sline)

                            self.LibraryClasses.append(t)

                            continue

        

                    elif InProtocolsSection:

                        if sline.strip()[0] == '[':

                            InProtocolsSection = False

                        else:

                            t = ProtocolDeclarationEntry(self.PackageName, sline)

                            self.Protocols.append(t)

                            continue

        

                    elif InGuidsSection:

                        if sline.strip()[0] == '[':

                            InGuidsSection = False

                        else:

                            t = GuidDeclarationEntry(self.PackageName, sline)

                            self.Guids.append(t)

                            continue

        

                    elif InPcdSection:

                        if sline.strip()[0] == '[':

                            InPcdSection = False

                        elif sline.strip()[0] == '}':

                            InStructuredPcdDeclaration = False

                        else:

                            if InStructuredPcdDeclaration:

                                continue

                            t = PcdDeclarationEntry(self.PackageName, sline)

                            self.Pcds.append(t)

                            if sline.rstrip()[-1] == '{':

                                InStructuredPcdDeclaration = True

                            continue

        

                    elif InIncludesSection:

                        if sline.strip()[0] == '[':

                            InIncludesSection = False

                        else:

                            self.IncludePaths.append(sline.strip())

                            continue

        

                    elif InPPISection:

                        if (sline.strip()[0] == '['):

                            InPPISection = False

                        else:

                            t = PpiDeclarationEntry(self.PackageName, sline)

                            self.PPIs.append(t)

                            continue

        

                    # check for different sections

                    if sline.strip().lower().startswith('[defines'):

                        InDefinesSection = True

        

                    elif sline.strip().lower().startswith('[libraryclasses'):

                        InLibraryClassSection = True

        

                    elif sline.strip().lower().startswith('[protocols'):

                        InProtocolsSection = True

        

                    elif sline.strip().lower().startswith('[guids'):

                        InGuidsSection = True

        

                    elif sline.strip().lower().startswith('[ppis'):

                        InPPISection = True

        

                    elif sline.strip().lower().startswith('[pcd'):

                        InPcdSection = True

        

                    elif sline.strip().lower().startswith('[includes'):

                        InIncludesSection = True

        

                self.Parsed = True

        

            def ParseStream(self, stream) -> None:

                """

                parse the supplied IO as a DEC file

                Args:

                    stream: a file-like/stream object in which DEC file contents can be read

        

                Returns:

                    None - Existing object now contains parsed data

        

                """

                self.Path = "None:stream_given"

                self.Lines = stream.readlines()

                self._Parse()

        

            def ParseFile(self, filepath: str) -> None:

                """

                Parse the supplied file.

                Args:

                  filepath: path to dec file to parse.  Can be either an absolute path or

                  relative to your CWD

        

                Returns:

                  None - Existing object now contains parsed data

        

                """

                self.Logger.debug("Parsing file: %s" % filepath)

                if(not os.path.isabs(filepath)):

                    fp = self.FindPath(filepath)

                else:

                    fp = filepath

                self.Path = fp

        

                f = open(fp, "r")

                self.Lines = f.readlines()

                f.close()

                self._Parse()

------

#### Ancestors (in MRO)

* edk2toollib.uefi.edk2.parsers.base_parser.HashFileParser
* edk2toollib.uefi.edk2.parsers.base_parser.BaseParser

#### Class variables

```python3
operators
```

#### Methods

    
#### ComputeResult

```python3
def ComputeResult(
    self,
    value,
    cond,
    value2
)
```
Args:
  value:
  cond:
  value2:

Returns:

??? example "View Source"
            def ComputeResult(self, value, cond, value2):

                """

        

                Args:

                  value:

                  cond:

                  value2:

        

                Returns:

        

                """

                ivalue = value

                ivalue2 = value2

                if isinstance(value, str):

                    ivalue = value.strip("\"")

                if isinstance(value2, str):

                    ivalue2 = value2.strip("\"")

        

                # convert it to interpretted value

                if (cond.upper() == "IN"):

                    # strip quotes

                    self.Logger.debug(f"{ivalue} in {ivalue2}")

        

                    return ivalue in ivalue2

        

                try:

                    ivalue = self.ConvertToInt(ivalue)

                except ValueError:

                    pass

                try:

                    if(cond.lower() == "in"):

                        ivalue2 = set(ivalue2.split())

                    else:

                        ivalue2 = self.ConvertToInt(ivalue2)

                except ValueError:

                    pass

        

                # First check our boolean operators

                if (cond.upper() == "OR"):

                    return ivalue or ivalue2

                if (cond.upper() == "AND"):

                    return ivalue and ivalue2

        

                # check our truthyness

                if(cond == "=="):

                    # equal

                    return (ivalue == ivalue2) or (value == value2)

        

                elif (cond == "!="):

                    # not equal

                    return (ivalue != ivalue2) and (value != value2)

        

                # check to make sure we only have digits from here on out

                if not isinstance(value, int) and not str.isdigit(value):

                    self.Logger.error(f"{self.__class__}: Unknown value: {value} {ivalue.__class__}")

                    self.Logger.debug(f"{self.__class__}: Conditional: {value} {cond}{value2}")

                    raise ValueError("Unknown value")

        

                if not isinstance(value2, int) and not str.isdigit(value2):

                    self.Logger.error(f"{self.__class__}: Unknown value: {value2} {ivalue2}")

                    self.Logger.debug(f"{self.__class__}: Conditional: {value} {cond} {value2}")

                    raise ValueError("Unknown value")

        

                if (cond == "<"):

                    return (ivalue < ivalue2)

        

                elif (cond == "<="):

                    return (ivalue <= ivalue2)

        

                elif (cond == ">"):

                    return (ivalue > ivalue2)

        

                elif (cond == ">="):

                    return (ivalue >= ivalue2)

        

                else:

                    self.Logger.error(f"{self.__class__}: Unknown conditional: {cond}")

                    raise RuntimeError("Unknown conditional")

    
#### ConvertToInt

```python3
def ConvertToInt(
    self,
    value
)
```
Args:
  value: must be str or int

Returns:

??? example "View Source"
            def ConvertToInt(self, value):

                """

        

                Args:

                  value: must be str or int

        

                Returns:

        

                """

                if isinstance(value, int):

                    return value

                if isinstance(value, str) and value.upper() == "TRUE":

                    return 1

                elif isinstance(value, str) and value.upper() == "FALSE":

                    return 0

                elif isinstance(value, str) and value.upper().startswith("0X"):

                    return int(value, 16)

                else:

                    return int(value, 10)

    
#### EvaluateConditional

```python3
def EvaluateConditional(
    self,
    text
)
```
Uses a pushdown resolver 

??? example "View Source"
            def EvaluateConditional(self, text):

                ''' Uses a pushdown resolver '''

                text = str(text).strip()

                if not text.lower().startswith("!if "):

                    raise RuntimeError(f"Invalid conditional cannot be validated: {text}")

                text = text[3:].strip()

                logging.debug(f"STAGE 1: {text}")

                text = self.ReplaceVariables(text)

                logging.debug(f"STAGE 2: {text}")

                tokens = self._TokenizeConditional(text)

                logging.debug(f"STAGE 3: {tokens}")

                expression = self._ConvertTokensToPostFix(tokens)

                logging.debug(f"STAGE 4: {expression}")

        

                # Now we evaluate the post fix expression

                if len(expression) == 0:

                    raise RuntimeError(f"Malformed !if conditional expression {text} {expression}")

                while len(expression) != 1:

                    first_operand_index = -1

                    # find the first operator

                    for index, item in enumerate(expression):

                        if self._IsOperator(item):

                            first_operand_index = index

                            break

                    if first_operand_index == -1:

                        raise RuntimeError(f"We didn't find an operator to execute in {expression}: {text}")

                    operand = expression[first_operand_index]

        

                    if operand == "NOT":

                        # Special logic for handling the not

                        if first_operand_index < 1:

                            raise RuntimeError(f"We have a stray operand {operand}")

                        # grab the operand right before the NOT and invert it

                        operator1_raw = expression[first_operand_index - 1]

                        operator1 = self.ConvertToInt(operator1_raw)

                        result = not operator1

                        # grab what was before the operator and the operand, then squish it all together

                        new_expression = expression[:first_operand_index - 1] if first_operand_index > 1 else []

                        new_expression += [result, ] + expression[first_operand_index + 1:]

                        expression = new_expression

                    else:

                        if first_operand_index < 2:

                            raise RuntimeError(f"We have a stray operand {operand}")

                        operator1 = expression[first_operand_index - 2]

                        operator2 = expression[first_operand_index - 1]

        

                        do_invert = False

                        # check if we have a special operator that has a combined not on it

                        if str(operand).startswith("!+"):

                            operand = operand[2:]

                            do_invert = True

                        # compute the result now that we have the three things we need

                        result = self.ComputeResult(operator1, operand, operator2)

        

                        if do_invert:

                            result = not result

                        # grab what was before the operator and the operand, then smoosh it all together

                        new_expression = expression[:first_operand_index - 2] if first_operand_index > 2 else []

                        new_expression += [result, ] + expression[first_operand_index + 1:]

                        expression = new_expression

        

                final = self.ConvertToInt(expression[0])

                logging.debug(f" FINAL {expression} {final}")

        

                return bool(final)

    
#### FindPath

```python3
def FindPath(
    self,
    *p
)
```
Args:
  *p:

Returns:

??? example "View Source"
            def FindPath(self, *p):

                """

        

                Args:

                  *p:

        

                Returns:

        

                """

                # NOTE: Some of this logic should be replaced

                #       with the path resolution from Edk2Module code.

        

                # If the absolute path exists, return it.

                Path = os.path.join(self.RootPath, *p)

                if os.path.exists(Path):

                    return Path

        

                # If that fails, check a path relative to the target file.

                if self.TargetFilePath is not None:

                    Path = os.path.join(self.TargetFilePath, *p)

                    if os.path.exists(Path):

                        return Path

        

                # If that fails, check in every possible Pkg path.

                for Pkg in self.PPs:

                    Path = os.path.join(self.RootPath, Pkg, *p)

                    if os.path.exists(Path):

                        return Path

        

                # log invalid file path

                Path = os.path.join(self.RootPath, *p)

                self.Logger.error("Invalid file path %s" % Path)

                return Path

    
#### InActiveCode

```python3
def InActiveCode(
    self
)
```

??? example "View Source"
            def InActiveCode(self):

                """ """

                ret = True

                for a in self.ConditionalStack:

                    if not a:

                        ret = False

                        break

        

                return ret

    
#### IsGuidString

```python3
def IsGuidString(
    self,
    l
)
```
will return true if the the line has
= { 0xD3B36F2C, 0xD551, 0x11D4, { 0x9A, 0x46, 0x00, 0x90, 0x27, 0x3F, 0xC1, 0x4D }}
Args:
  l:

Returns:

??? example "View Source"
            def IsGuidString(self, l):

                """

                will return true if the the line has

                = { 0xD3B36F2C, 0xD551, 0x11D4, { 0x9A, 0x46, 0x00, 0x90, 0x27, 0x3F, 0xC1, 0x4D }}

                Args:

                  l:

        

                Returns:

        

                """

                if(l.count("{") == 2 and l.count("}") == 2 and l.count(",") == 10 and l.count("=") == 1):

                    return True

                return False

    
#### ParseFile

```python3
def ParseFile(
    self,
    filepath: str
) -> None
```
Parse the supplied file.
Args:
  filepath: path to dec file to parse.  Can be either an absolute path or
  relative to your CWD

Returns:
  None - Existing object now contains parsed data

??? example "View Source"
            def ParseFile(self, filepath: str) -> None:

                """

                Parse the supplied file.

                Args:

                  filepath: path to dec file to parse.  Can be either an absolute path or

                  relative to your CWD

        

                Returns:

                  None - Existing object now contains parsed data

        

                """

                self.Logger.debug("Parsing file: %s" % filepath)

                if(not os.path.isabs(filepath)):

                    fp = self.FindPath(filepath)

                else:

                    fp = filepath

                self.Path = fp

        

                f = open(fp, "r")

                self.Lines = f.readlines()

                f.close()

                self._Parse()

    
#### ParseGuid

```python3
def ParseGuid(
    self,
    l
)
```
parse a guid into a different format
Will throw exception if missing any of the 11 parts of isn't long enough
Args:
  l: the guid to parse ex: { 0xD3B36F2C, 0xD551, 0x11D4, { 0x9A, 0x46, 0x00, 0x90, 0x27, 0x3F, 0xC1, 0x4D }}

Returns: a string of the guid. ex: D3B36F2C-D551-11D4-9A46-0090273FC14D

??? example "View Source"
            def ParseGuid(self, l):

                """

                parse a guid into a different format

                Will throw exception if missing any of the 11 parts of isn't long enough

                Args:

                  l: the guid to parse ex: { 0xD3B36F2C, 0xD551, 0x11D4, { 0x9A, 0x46, 0x00, 0x90, 0x27, 0x3F, 0xC1, 0x4D }}

        

                Returns: a string of the guid. ex: D3B36F2C-D551-11D4-9A46-0090273FC14D

        

                """

                entries = l.lstrip(' {').rstrip(' }').split(',')

                if len(entries) != 11:

                    raise RuntimeError(f"Invalid GUID found {l}. We are missing some parts since we only found: {len(entries)}")

                gu = entries[0].lstrip(' 0').lstrip('x').strip()

                # pad front until 8 chars

                while(len(gu) < 8):

                    gu = "0" + gu

        

                gut = entries[1].lstrip(' 0').lstrip('x').strip()

                while(len(gut) < 4):

                    gut = "0" + gut

                gu = gu + "-" + gut

        

                gut = entries[2].lstrip(' 0').lstrip('x').strip()

                while(len(gut) < 4):

                    gut = "0" + gut

                gu = gu + "-" + gut

        

                # strip off extra {

                gut = entries[3].lstrip(' { 0').lstrip('x').strip()

                while(len(gut) < 2):

                    gut = "0" + gut

                gu = gu + "-" + gut

        

                gut = entries[4].lstrip(' 0').lstrip('x').strip()

                while(len(gut) < 2):

                    gut = "0" + gut

                gu = gu + gut

        

                gut = entries[5].lstrip(' 0').lstrip('x').strip()

                while(len(gut) < 2):

                    gut = "0" + gut

                gu = gu + "-" + gut

        

                gut = entries[6].lstrip(' 0').lstrip('x').strip()

                while(len(gut) < 2):

                    gut = "0" + gut

                gu = gu + gut

        

                gut = entries[7].lstrip(' 0').lstrip('x').strip()

                while(len(gut) < 2):

                    gut = "0" + gut

                gu = gu + gut

        

                gut = entries[8].lstrip(' 0').lstrip('x').strip()

                while(len(gut) < 2):

                    gut = "0" + gut

                gu = gu + gut

        

                gut = entries[9].lstrip(' 0').lstrip('x').strip()

                while(len(gut) < 2):

                    gut = "0" + gut

                gu = gu + gut

        

                gut = entries[10].split()[0].lstrip(' 0').lstrip('x').rstrip(' } ').strip()

                while(len(gut) < 2):

                    gut = "0" + gut

                gu = gu + gut

        

                proper_guid_length = 36

                if len(gu) > proper_guid_length:

                    raise RuntimeError(f"The guid we parsed was too long: {gu}")

                if len(gu) < proper_guid_length:

                    raise RuntimeError(f"The guid we parsed was too short: {gu}")

        

                return gu.upper()

    
#### ParseNewSection

```python3
def ParseNewSection(
    self,
    l
)
```
Args:
  l:

Returns:

??? example "View Source"
            def ParseNewSection(self, l):

                """

        

                Args:

                  l:

        

                Returns:

        

                """

                if(l.count("[") == 1 and l.count("]") == 1):  # new section

                    section = l.strip().lstrip("[").split(".")[0].split(",")[0].rstrip("]").strip()

                    self.CurrentFullSection = l.strip().lstrip("[").split(",")[0].rstrip("]").strip()

                    return (True, section)

                return (False, "")

    
#### ParseStream

```python3
def ParseStream(
    self,
    stream
) -> None
```
parse the supplied IO as a DEC file
Args:
    stream: a file-like/stream object in which DEC file contents can be read

Returns:
    None - Existing object now contains parsed data

??? example "View Source"
            def ParseStream(self, stream) -> None:

                """

                parse the supplied IO as a DEC file

                Args:

                    stream: a file-like/stream object in which DEC file contents can be read

        

                Returns:

                    None - Existing object now contains parsed data

        

                """

                self.Path = "None:stream_given"

                self.Lines = stream.readlines()

                self._Parse()

    
#### PopConditional

```python3
def PopConditional(
    self
)
```

??? example "View Source"
            def PopConditional(self):

                """ """

                if(len(self.ConditionalStack) > 0):

                    return self.ConditionalStack.pop()

                else:

                    self.Logger.critical("Tried to pop an empty conditional stack.  Line Number %d" % self.CurrentLine)

                    return self.ConditionalStack.pop()  # this should cause a crash but will give trace.

    
#### ProcessConditional

```python3
def ProcessConditional(
    self,
    text
)
```
Args:
  text:

Returns:

??? example "View Source"
            def ProcessConditional(self, text):

                """

        

                Args:

                  text:

        

                Returns:

        

                """

                if '"' in text:

                    tokens = text.split('"')

                    tokens = tokens[0].split() + [tokens[1]] + tokens[2].split()

                else:

                    tokens = text.split()

                if(tokens[0].lower() == "!if"):

                    self.PushConditional(self.EvaluateConditional(text))

                    return True

        

                elif(tokens[0].lower() == "!ifdef"):

                    if len(tokens) != 2:

                        self.Logger.error("!ifdef conditionals need to be formatted correctly (spaces between each token)")

                        raise RuntimeError("Invalid conditional", text)

                    self.PushConditional((tokens[1] != self._MacroNotDefinedValue))

                    return True

        

                elif(tokens[0].lower() == "!ifndef"):

                    if len(tokens) != 2:

                        self.Logger.error("!ifdef conditionals need to be formatted correctly (spaces between each token)")

                        raise RuntimeError("Invalid conditional", text)

                    self.PushConditional((tokens[1] == self._MacroNotDefinedValue))

                    return True

        

                elif(tokens[0].lower() == "!else"):

                    if len(tokens) != 1:

                        self.Logger.error("!ifdef conditionals need to be formatted correctly (spaces between each token)")

                        raise RuntimeError("Invalid conditional", text)

                    v = self.PopConditional()

                    # TODO make sure we can't do multiple else statements

                    self.PushConditional(not v)

                    return True

        

                elif(tokens[0].lower() == "!endif"):

                    if len(tokens) != 1:

                        self.Logger.error("!ifdef conditionals need to be formatted correctly (spaces between each token)")

                        raise RuntimeError("Invalid conditional", text)

                    self.PopConditional()

                    return True

        

                return False

    
#### PushConditional

```python3
def PushConditional(
    self,
    v
)
```
Args:
  v:

Returns:

??? example "View Source"
            def PushConditional(self, v):

                """

        

                Args:

                  v:

        

                Returns:

        

                """

                self.ConditionalStack.append(v)

    
#### ReplaceVariables

```python3
def ReplaceVariables(
    self,
    line
)
```
Args:
  line:

Returns:

??? example "View Source"
            def ReplaceVariables(self, line):

                """

        

                Args:

                  line:

        

                Returns:

        

                """

                # first tokenize and look for tokens require special macro

                # handling without $.  This must be done first otherwise

                # both syntax options can not be supported.

                result = line

                tokens = result.split()

                replace = len(tokens) > 1 and tokens[0].lower() in ["!ifdef", "!ifndef", "!if", "!elseif"]

                if len(tokens) > 1 and tokens[0].lower() in ["!ifdef", "!ifndef"]:

                    if not tokens[1].startswith("$("):

                        v = self._FindReplacementForToken(tokens[1], replace)

                        if v is not None:

                            result = result.replace(tokens[1], v, 1)

        

                # use line to avoid change by handling above

                rep = line.count("$")

                index = 0

                while(rep > 0):

                    start = line.find("$(", index)

                    end = line.find(")", start)

        

                    token = line[start + 2:end]

                    replacement_token = line[start:end + 1]

                    self.Logger.debug("Token is %s" % token)

                    v = self._FindReplacementForToken(token, replace)

                    if v is not None:

                        result = result.replace(replacement_token, v, 1)

        

                    index = end + 1

                    rep = rep - 1

        

                return result

    
#### ResetParserState

```python3
def ResetParserState(
    self
)
```

??? example "View Source"
            def ResetParserState(self):

                """ """

                self.ConditionalStack = []

                self.CurrentSection = ''

                self.CurrentFullSection = ''

                self.Parsed = False

    
#### SetBaseAbsPath

```python3
def SetBaseAbsPath(
    self,
    path
)
```
Args:
  path:

Returns:

??? example "View Source"
            def SetBaseAbsPath(self, path):

                """

        

                Args:

                  path:

        

                Returns:

        

                """

                self.RootPath = path

                return self

    
#### SetInputVars

```python3
def SetInputVars(
    self,
    inputdict
)
```
Args:
  inputdict:

Returns:

??? example "View Source"
            def SetInputVars(self, inputdict):

                """

        

                Args:

                  inputdict:

        

                Returns:

        

                """

                self.InputVars = inputdict

                return self

    
#### SetPackagePaths

```python3
def SetPackagePaths(
    self,
    pps=[]
)
```
Args:
  pps:  (Default value = [])

Returns:

??? example "View Source"
            def SetPackagePaths(self, pps=[]):

                """

        

                Args:

                  pps:  (Default value = [])

        

                Returns:

        

                """

                self.PPs = pps

                return self

    
#### StripComment

```python3
def StripComment(
    self,
    l
)
```
Args:
  l:

Returns:

??? example "View Source"
            def StripComment(self, l):

                """

        

                Args:

                  l:

        

                Returns:

        

                """

                return l.split('#')[0].strip()

    
#### WriteLinesToFile

```python3
def WriteLinesToFile(
    self,
    filepath
)
```
Args:
  filepath:

Returns:

??? example "View Source"
            def WriteLinesToFile(self, filepath):

                """

        

                Args:

                  filepath:

        

                Returns:

        

                """

                self.Logger.debug("Writing all lines to file: %s" % filepath)

                f = open(filepath, "w")

                for l in self.Lines:

                    f.write(l + "\n")

                f.close()

### GuidDeclarationEntry

```python3
class GuidDeclarationEntry(
    packagename: str,
    rawtext: str = None
)
```

A baseclass for declaration types that have a name and guid.

??? example "View Source"
        class GuidDeclarationEntry(GuidedDeclarationEntry):

        

            def __init__(self, packagename: str, rawtext: str = None):

                """Init a Ppi declaration entry"""

                super().__init__(packagename, rawtext)

                self.type = GuidedDeclarationEntry.GUID

------

#### Ancestors (in MRO)

* edk2toollib.uefi.edk2.parsers.dec_parser.GuidedDeclarationEntry

#### Class variables

```python3
GUID
```

```python3
PPI
```

```python3
PROTOCOL
```

### GuidedDeclarationEntry

```python3
class GuidedDeclarationEntry(
    packagename: str,
    rawtext: str = None
)
```

A baseclass for declaration types that have a name and guid.

??? example "View Source"
        class GuidedDeclarationEntry():

            """A baseclass for declaration types that have a name and guid."""

            PROTOCOL = 1

            PPI = 2

            GUID = 3

        

            def __init__(self, packagename: str, rawtext: str = None):

                """Init a protocol/Ppi/or Guid declaration entry"""

                self.name = ""

                self.guidstring = ""

                self.guid = None

                self.package_name = packagename

                if(rawtext is not None):

                    self._parse(rawtext)

        

            def _parse(self, rawtext: str) -> None:

                """Parses the name and guid of a declaration

        

                Args:

                  rawtext: str:

        

                Returns:

        

                """

                t = rawtext.partition("=")

                self.name = t[0].strip()

                self.guidstring = t[2].strip()

                self.guid = GuidParser.uuid_from_guidstring(self.guidstring)

                if(self.guid is None):

                    raise ValueError("Could not parse guid")

------

#### Descendants

* edk2toollib.uefi.edk2.parsers.dec_parser.ProtocolDeclarationEntry
* edk2toollib.uefi.edk2.parsers.dec_parser.PpiDeclarationEntry
* edk2toollib.uefi.edk2.parsers.dec_parser.GuidDeclarationEntry

#### Class variables

```python3
GUID
```

```python3
PPI
```

```python3
PROTOCOL
```

### LibraryClassDeclarationEntry

```python3
class LibraryClassDeclarationEntry(
    packagename: str,
    rawtext: str = None
)
```

??? example "View Source"
        class LibraryClassDeclarationEntry():

        

            def __init__(self, packagename: str, rawtext: str = None):

                """Init a library Class Declaration Entry"""

                self.path = ""

                self.name = ""

                self.package_name = packagename

                if (rawtext is not None):

                    self._parse(rawtext)

        

            def _parse(self, rawtext: str) -> None:

                """Parses the rawtext line to collect the Library Class declaration

                   information (name and package root relative path).

        

                Args:

                  rawtext: str

                  expected format is <library class name> | <package relative path to header file>

        

                Returns:

                  None

        

                """

                t = rawtext.partition("|")

                self.name = t[0].strip()

                self.path = t[2].strip()

------

### PcdDeclarationEntry

```python3
class PcdDeclarationEntry(
    packagename: str,
    rawtext: str = None
)
```

??? example "View Source"
        class PcdDeclarationEntry():

        

            def __init__(self, packagename: str, rawtext: str = None):

                """Creates a PCD Declaration Entry for one PCD"""

                self.token_space_name = ""

                self.name = ""

                self.default_value = ""

                self.type = ""

                self.id = ""

                self.package_name = packagename

                if (rawtext is not None):

                    self._parse(rawtext)

        

            def _parse(self, rawtext: str):

                """

        

                Args:

                  rawtext: str:

        

                Returns:

        

                """

                sp = rawtext.partition(".")

                self.token_space_name = sp[0].strip()

                op = sp[2].split("|")

                # if it's 2 long, we need to check that it's a structured PCD

                if(len(op) == 2 and op[0].count(".") > 0):

                    pass

                # otherwise it needs at least 4 parts

                elif(len(op) < 4):

                    raise Exception(f"Too few parts: {op}")

                # but also less than 5

                elif(len(op) > 5):

                    raise Exception(f"Too many parts: {rawtext}")

                elif(len(op) == 5 and op[4].strip() != '{'):

                    raise Exception(f"Too many parts: {rawtext}")

        

                self.name = op[0].strip()

                self.default_value = op[1].strip()

                # if we don't know what the type and id, it's because it's structured

                self.type = op[2].strip() if len(op) > 2 else "STRUCTURED_PCD"

                self.id = op[3].strip() if len(op) > 2 else "STRUCTURED_PCD"

------

### PpiDeclarationEntry

```python3
class PpiDeclarationEntry(
    packagename: str,
    rawtext: str = None
)
```

A baseclass for declaration types that have a name and guid.

??? example "View Source"
        class PpiDeclarationEntry(GuidedDeclarationEntry):

        

            def __init__(self, packagename: str, rawtext: str = None):

                """Init a Ppi declaration entry"""

                super().__init__(packagename, rawtext)

                self.type = GuidedDeclarationEntry.PPI

------

#### Ancestors (in MRO)

* edk2toollib.uefi.edk2.parsers.dec_parser.GuidedDeclarationEntry

#### Class variables

```python3
GUID
```

```python3
PPI
```

```python3
PROTOCOL
```

### ProtocolDeclarationEntry

```python3
class ProtocolDeclarationEntry(
    packagename: str,
    rawtext: str = None
)
```

A baseclass for declaration types that have a name and guid.

??? example "View Source"
        class ProtocolDeclarationEntry(GuidedDeclarationEntry):

        

            def __init__(self, packagename: str, rawtext: str = None):

                """Init a protocol declaration entry"""

                super().__init__(packagename, rawtext)

                self.type = GuidedDeclarationEntry.PROTOCOL

------

#### Ancestors (in MRO)

* edk2toollib.uefi.edk2.parsers.dec_parser.GuidedDeclarationEntry

#### Class variables

```python3
GUID
```

```python3
PPI
```

```python3
PROTOCOL
```