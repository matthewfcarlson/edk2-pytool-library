Module edk2toollib.uefi.edk2.parsers.fdf_parser
===============================================

??? example "View Source"
        # @file fdf_parser.py

        # Code to help parse EDK2 Fdf files

        #

        # Copyright (c) Microsoft Corporation

        #

        # SPDX-License-Identifier: BSD-2-Clause-Patent

        ##

        from edk2toollib.uefi.edk2.parsers.base_parser import HashFileParser

        import os

        

        

        class FdfParser(HashFileParser):

        

            def __init__(self):

                HashFileParser.__init__(self, 'ModuleFdfParser')

                self.Lines = []

                self.Parsed = False

                self.Dict = {}  # defines dictionary

                self.FVs = {}

                self.FDs = {}

                self.CurrentSection = []

                self.Path = ""

        

            def GetNextLine(self):

                if len(self.Lines) == 0:

                    return None

        

                line = self.Lines.pop()

                self.CurrentLine += 1

                sline = self.StripComment(line)

        

                if(sline is None or len(sline) < 1):

                    return self.GetNextLine()

        

                sline = self.ReplaceVariables(sline)

                if self.ProcessConditional(sline):

                    # was a conditional so skip

                    return self.GetNextLine()

                if not self.InActiveCode():

                    return self.GetNextLine()

        

                self._BracketCount += sline.count("{")

                self._BracketCount -= sline.count("}")

        

                return sline

        

            def ParseFile(self, filepath):

                self.Logger.debug("Parsing file: %s" % filepath)

                if(not os.path.isabs(filepath)):

                    fp = self.FindPath(filepath)

                else:

                    fp = filepath

                self.Path = fp

                self.CurrentLine = 0

                self._f = open(fp, "r")

                self.Lines = self._f.readlines()

                self.Lines.reverse()

                self._f.close()

                self._BracketCount = 0

                InDefinesSection = False

                InFdSection = False

                InFvSection = False

                InCapsuleSection = False

                InFmpPayloadSection = False

                InRuleSection = False

        

                sline = ""

                while sline is not None:

                    sline = self.GetNextLine()

        

                    if sline is None:

                        break

        

                    if sline.strip().startswith("[") and sline.strip().endswith("]"):  # if we're starting a new section

                        # this basically gets what's after the . or if it doesn't have a period

                        # the whole thing for every comma separated item in sline

                        self.CurrentSection = [

                            x.split(".", 1)[1] if "." in x else x for x in sline.strip("[] ").strip().split(",")]

                        InDefinesSection = False

                        InFdSection = False

                        InFvSection = False

                        InCapsuleSection = False

                        InFmpPayloadSection = False

                        InRuleSection = False

                        self.LocalVars = {}

                        self.LocalVars.update(self.Dict)

        

                    if InDefinesSection:

                        if sline.count("=") == 1:

                            tokens = sline.replace("DEFINE", "").split('=', 1)

                            self.Dict[tokens[0].strip()] = tokens[1].strip()

                            self.Logger.info("Key,values found:  %s = %s" % (tokens[0].strip(), tokens[1].strip()))

                            continue

        

                    elif InFdSection:

                        for section in self.CurrentSection:

                            if section not in self.FVs:

                                self.FDs[section] = {"Dict": {}}

                                # TODO finish the FD section

                        continue

        

                    elif InFvSection:

                        for section in self.CurrentSection:

                            if section not in self.FVs:

                                self.FVs[section] = {"Dict": {}, "Infs": [], "Files": {}}

                            # ex: INF  MdeModulePkg/Core/RuntimeDxe/RuntimeDxe.inf

                            if sline.upper().startswith("INF "):

                                InfValue = sline[3:].strip()

                                self.FVs[section]["Infs"].append(InfValue)

                            # ex: FILE FREEFORM = 7E175642-F3AD-490A-9F8A-2E9FC6933DDD {

                            elif sline.upper().startswith("FILE"):

                                sline = sline.strip("}").strip("{").strip()  # make sure we take off the { and }

                                file_def = sline[4:].strip().split("=", 1)  # split by =

                                if len(file_def) != 2:  # check to make sure we can parse this file

                                    raise RuntimeError("Unable to properly parse " + sline)

        

                                currentType = file_def[0].strip()  # get the type FILE

                                currentName = file_def[1].strip()  # get the name (guid or otherwise)

                                if currentType not in self.FVs[section]:

                                    self.FVs[section]["Files"][currentName] = {}

                                self.FVs[section]["Files"][currentName]["type"] = currentType

        

                                while self._BracketCount > 0:  # go until we get our bracket back

                                    sline = self.GetNextLine().strip("}{ ")

                                    # SECTION GUIDED EE4E5898-3914-4259-9D6E-DC7BD79403CF PROCESSING_REQUIRED = TRUE

                                    if sline.upper().startswith("SECTION GUIDED"):  # get the guided section

                                        section_def = sline[14:].strip().split("=", 1)

                                        sectionType = section_def[0].strip()  # UI in this example

                                        sectionValue = section_def[1].strip()

                                        if sectionType not in self.FVs[section]["Files"][currentName]:

                                            self.FVs[section]["Files"][currentName][sectionType] = {}

                                        # TODO support guided sections

                                    # ex: SECTION UI = "GenericGopDriver"

                                    elif sline.upper().startswith("SECTION"):  # get the section

                                        section_def = sline[7:].strip().split("=", 1)

                                        sectionType = section_def[0].strip()  # UI in this example

                                        sectionValue = section_def[1].strip()

        

                                        if sectionType not in self.FVs[section]["Files"][currentName]:

                                            self.FVs[section]["Files"][currentName][sectionType] = []

                                        self.FVs[section]["Files"][currentName][sectionType].append(sectionValue)

                                    else:

                                        self.Logger.info("Unknown line: {}".format(sline))

        

                        continue

        

                    elif InCapsuleSection:

                        # TODO: finish capsule section

                        continue

        

                    elif InFmpPayloadSection:

                        # TODO finish FMP payload section

                        continue

        

                    elif InRuleSection:

                        # TODO finish rule section

                        continue

        

                    # check for different sections

                    if sline.strip().lower().startswith('[defines'):

                        InDefinesSection = True

        

                    elif sline.strip().lower().startswith('[fd.'):

                        InFdSection = True

        

                    elif sline.strip().lower().startswith('[fv.'):

                        InFvSection = True

        

                    elif sline.strip().lower().startswith('[capsule.'):

                        InCapsuleSection = True

        

                    elif sline.strip().lower().startswith('[fmpPayload.'):

                        InFmpPayloadSection = True

        

                    elif sline.strip().lower().startswith('[rule.'):

                        InRuleSection = True

        

                self.Parsed = True

Classes
-------

### FdfParser

```python3
class FdfParser(
    
)
```

??? example "View Source"
        class FdfParser(HashFileParser):

        

            def __init__(self):

                HashFileParser.__init__(self, 'ModuleFdfParser')

                self.Lines = []

                self.Parsed = False

                self.Dict = {}  # defines dictionary

                self.FVs = {}

                self.FDs = {}

                self.CurrentSection = []

                self.Path = ""

        

            def GetNextLine(self):

                if len(self.Lines) == 0:

                    return None

        

                line = self.Lines.pop()

                self.CurrentLine += 1

                sline = self.StripComment(line)

        

                if(sline is None or len(sline) < 1):

                    return self.GetNextLine()

        

                sline = self.ReplaceVariables(sline)

                if self.ProcessConditional(sline):

                    # was a conditional so skip

                    return self.GetNextLine()

                if not self.InActiveCode():

                    return self.GetNextLine()

        

                self._BracketCount += sline.count("{")

                self._BracketCount -= sline.count("}")

        

                return sline

        

            def ParseFile(self, filepath):

                self.Logger.debug("Parsing file: %s" % filepath)

                if(not os.path.isabs(filepath)):

                    fp = self.FindPath(filepath)

                else:

                    fp = filepath

                self.Path = fp

                self.CurrentLine = 0

                self._f = open(fp, "r")

                self.Lines = self._f.readlines()

                self.Lines.reverse()

                self._f.close()

                self._BracketCount = 0

                InDefinesSection = False

                InFdSection = False

                InFvSection = False

                InCapsuleSection = False

                InFmpPayloadSection = False

                InRuleSection = False

        

                sline = ""

                while sline is not None:

                    sline = self.GetNextLine()

        

                    if sline is None:

                        break

        

                    if sline.strip().startswith("[") and sline.strip().endswith("]"):  # if we're starting a new section

                        # this basically gets what's after the . or if it doesn't have a period

                        # the whole thing for every comma separated item in sline

                        self.CurrentSection = [

                            x.split(".", 1)[1] if "." in x else x for x in sline.strip("[] ").strip().split(",")]

                        InDefinesSection = False

                        InFdSection = False

                        InFvSection = False

                        InCapsuleSection = False

                        InFmpPayloadSection = False

                        InRuleSection = False

                        self.LocalVars = {}

                        self.LocalVars.update(self.Dict)

        

                    if InDefinesSection:

                        if sline.count("=") == 1:

                            tokens = sline.replace("DEFINE", "").split('=', 1)

                            self.Dict[tokens[0].strip()] = tokens[1].strip()

                            self.Logger.info("Key,values found:  %s = %s" % (tokens[0].strip(), tokens[1].strip()))

                            continue

        

                    elif InFdSection:

                        for section in self.CurrentSection:

                            if section not in self.FVs:

                                self.FDs[section] = {"Dict": {}}

                                # TODO finish the FD section

                        continue

        

                    elif InFvSection:

                        for section in self.CurrentSection:

                            if section not in self.FVs:

                                self.FVs[section] = {"Dict": {}, "Infs": [], "Files": {}}

                            # ex: INF  MdeModulePkg/Core/RuntimeDxe/RuntimeDxe.inf

                            if sline.upper().startswith("INF "):

                                InfValue = sline[3:].strip()

                                self.FVs[section]["Infs"].append(InfValue)

                            # ex: FILE FREEFORM = 7E175642-F3AD-490A-9F8A-2E9FC6933DDD {

                            elif sline.upper().startswith("FILE"):

                                sline = sline.strip("}").strip("{").strip()  # make sure we take off the { and }

                                file_def = sline[4:].strip().split("=", 1)  # split by =

                                if len(file_def) != 2:  # check to make sure we can parse this file

                                    raise RuntimeError("Unable to properly parse " + sline)

        

                                currentType = file_def[0].strip()  # get the type FILE

                                currentName = file_def[1].strip()  # get the name (guid or otherwise)

                                if currentType not in self.FVs[section]:

                                    self.FVs[section]["Files"][currentName] = {}

                                self.FVs[section]["Files"][currentName]["type"] = currentType

        

                                while self._BracketCount > 0:  # go until we get our bracket back

                                    sline = self.GetNextLine().strip("}{ ")

                                    # SECTION GUIDED EE4E5898-3914-4259-9D6E-DC7BD79403CF PROCESSING_REQUIRED = TRUE

                                    if sline.upper().startswith("SECTION GUIDED"):  # get the guided section

                                        section_def = sline[14:].strip().split("=", 1)

                                        sectionType = section_def[0].strip()  # UI in this example

                                        sectionValue = section_def[1].strip()

                                        if sectionType not in self.FVs[section]["Files"][currentName]:

                                            self.FVs[section]["Files"][currentName][sectionType] = {}

                                        # TODO support guided sections

                                    # ex: SECTION UI = "GenericGopDriver"

                                    elif sline.upper().startswith("SECTION"):  # get the section

                                        section_def = sline[7:].strip().split("=", 1)

                                        sectionType = section_def[0].strip()  # UI in this example

                                        sectionValue = section_def[1].strip()

        

                                        if sectionType not in self.FVs[section]["Files"][currentName]:

                                            self.FVs[section]["Files"][currentName][sectionType] = []

                                        self.FVs[section]["Files"][currentName][sectionType].append(sectionValue)

                                    else:

                                        self.Logger.info("Unknown line: {}".format(sline))

        

                        continue

        

                    elif InCapsuleSection:

                        # TODO: finish capsule section

                        continue

        

                    elif InFmpPayloadSection:

                        # TODO finish FMP payload section

                        continue

        

                    elif InRuleSection:

                        # TODO finish rule section

                        continue

        

                    # check for different sections

                    if sline.strip().lower().startswith('[defines'):

                        InDefinesSection = True

        

                    elif sline.strip().lower().startswith('[fd.'):

                        InFdSection = True

        

                    elif sline.strip().lower().startswith('[fv.'):

                        InFvSection = True

        

                    elif sline.strip().lower().startswith('[capsule.'):

                        InCapsuleSection = True

        

                    elif sline.strip().lower().startswith('[fmpPayload.'):

                        InFmpPayloadSection = True

        

                    elif sline.strip().lower().startswith('[rule.'):

                        InRuleSection = True

        

                self.Parsed = True

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

    
#### GetNextLine

```python3
def GetNextLine(
    self
)
```

??? example "View Source"
            def GetNextLine(self):

                if len(self.Lines) == 0:

                    return None

        

                line = self.Lines.pop()

                self.CurrentLine += 1

                sline = self.StripComment(line)

        

                if(sline is None or len(sline) < 1):

                    return self.GetNextLine()

        

                sline = self.ReplaceVariables(sline)

                if self.ProcessConditional(sline):

                    # was a conditional so skip

                    return self.GetNextLine()

                if not self.InActiveCode():

                    return self.GetNextLine()

        

                self._BracketCount += sline.count("{")

                self._BracketCount -= sline.count("}")

        

                return sline

    
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
    filepath
)
```

??? example "View Source"
            def ParseFile(self, filepath):

                self.Logger.debug("Parsing file: %s" % filepath)

                if(not os.path.isabs(filepath)):

                    fp = self.FindPath(filepath)

                else:

                    fp = filepath

                self.Path = fp

                self.CurrentLine = 0

                self._f = open(fp, "r")

                self.Lines = self._f.readlines()

                self.Lines.reverse()

                self._f.close()

                self._BracketCount = 0

                InDefinesSection = False

                InFdSection = False

                InFvSection = False

                InCapsuleSection = False

                InFmpPayloadSection = False

                InRuleSection = False

        

                sline = ""

                while sline is not None:

                    sline = self.GetNextLine()

        

                    if sline is None:

                        break

        

                    if sline.strip().startswith("[") and sline.strip().endswith("]"):  # if we're starting a new section

                        # this basically gets what's after the . or if it doesn't have a period

                        # the whole thing for every comma separated item in sline

                        self.CurrentSection = [

                            x.split(".", 1)[1] if "." in x else x for x in sline.strip("[] ").strip().split(",")]

                        InDefinesSection = False

                        InFdSection = False

                        InFvSection = False

                        InCapsuleSection = False

                        InFmpPayloadSection = False

                        InRuleSection = False

                        self.LocalVars = {}

                        self.LocalVars.update(self.Dict)

        

                    if InDefinesSection:

                        if sline.count("=") == 1:

                            tokens = sline.replace("DEFINE", "").split('=', 1)

                            self.Dict[tokens[0].strip()] = tokens[1].strip()

                            self.Logger.info("Key,values found:  %s = %s" % (tokens[0].strip(), tokens[1].strip()))

                            continue

        

                    elif InFdSection:

                        for section in self.CurrentSection:

                            if section not in self.FVs:

                                self.FDs[section] = {"Dict": {}}

                                # TODO finish the FD section

                        continue

        

                    elif InFvSection:

                        for section in self.CurrentSection:

                            if section not in self.FVs:

                                self.FVs[section] = {"Dict": {}, "Infs": [], "Files": {}}

                            # ex: INF  MdeModulePkg/Core/RuntimeDxe/RuntimeDxe.inf

                            if sline.upper().startswith("INF "):

                                InfValue = sline[3:].strip()

                                self.FVs[section]["Infs"].append(InfValue)

                            # ex: FILE FREEFORM = 7E175642-F3AD-490A-9F8A-2E9FC6933DDD {

                            elif sline.upper().startswith("FILE"):

                                sline = sline.strip("}").strip("{").strip()  # make sure we take off the { and }

                                file_def = sline[4:].strip().split("=", 1)  # split by =

                                if len(file_def) != 2:  # check to make sure we can parse this file

                                    raise RuntimeError("Unable to properly parse " + sline)

        

                                currentType = file_def[0].strip()  # get the type FILE

                                currentName = file_def[1].strip()  # get the name (guid or otherwise)

                                if currentType not in self.FVs[section]:

                                    self.FVs[section]["Files"][currentName] = {}

                                self.FVs[section]["Files"][currentName]["type"] = currentType

        

                                while self._BracketCount > 0:  # go until we get our bracket back

                                    sline = self.GetNextLine().strip("}{ ")

                                    # SECTION GUIDED EE4E5898-3914-4259-9D6E-DC7BD79403CF PROCESSING_REQUIRED = TRUE

                                    if sline.upper().startswith("SECTION GUIDED"):  # get the guided section

                                        section_def = sline[14:].strip().split("=", 1)

                                        sectionType = section_def[0].strip()  # UI in this example

                                        sectionValue = section_def[1].strip()

                                        if sectionType not in self.FVs[section]["Files"][currentName]:

                                            self.FVs[section]["Files"][currentName][sectionType] = {}

                                        # TODO support guided sections

                                    # ex: SECTION UI = "GenericGopDriver"

                                    elif sline.upper().startswith("SECTION"):  # get the section

                                        section_def = sline[7:].strip().split("=", 1)

                                        sectionType = section_def[0].strip()  # UI in this example

                                        sectionValue = section_def[1].strip()

        

                                        if sectionType not in self.FVs[section]["Files"][currentName]:

                                            self.FVs[section]["Files"][currentName][sectionType] = []

                                        self.FVs[section]["Files"][currentName][sectionType].append(sectionValue)

                                    else:

                                        self.Logger.info("Unknown line: {}".format(sline))

        

                        continue

        

                    elif InCapsuleSection:

                        # TODO: finish capsule section

                        continue

        

                    elif InFmpPayloadSection:

                        # TODO finish FMP payload section

                        continue

        

                    elif InRuleSection:

                        # TODO finish rule section

                        continue

        

                    # check for different sections

                    if sline.strip().lower().startswith('[defines'):

                        InDefinesSection = True

        

                    elif sline.strip().lower().startswith('[fd.'):

                        InFdSection = True

        

                    elif sline.strip().lower().startswith('[fv.'):

                        InFvSection = True

        

                    elif sline.strip().lower().startswith('[capsule.'):

                        InCapsuleSection = True

        

                    elif sline.strip().lower().startswith('[fmpPayload.'):

                        InFmpPayloadSection = True

        

                    elif sline.strip().lower().startswith('[rule.'):

                        InRuleSection = True

        

                self.Parsed = True

    
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