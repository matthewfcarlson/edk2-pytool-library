Module edk2toollib.uefi.edk2.parsers.dsc_parser
===============================================

??? example "View Source"
        # @file dsc_parser.py

        # Code to help parse DSC files

        #

        # Copyright (c) Microsoft Corporation

        #

        # SPDX-License-Identifier: BSD-2-Clause-Patent

        ##

        from edk2toollib.uefi.edk2.parsers.base_parser import HashFileParser

        import os

        

        

        class DscParser(HashFileParser):

        

            def __init__(self):

                super(DscParser, self).__init__('DscParser')

                self.SixMods = []

                self.SixModsEnhanced = []

                self.ThreeMods = []

                self.ThreeModsEnhanced = []

                self.OtherMods = []

                self.Libs = []

                self.LibsEnhanced = []

                self.ParsingInBuildOption = 0

                self.LibraryClassToInstanceDict = {}

                self.Pcds = []

                self._dsc_file_paths = set()  # This includes the full paths for every DSC that makes up the file

        

            def __ParseLine(self, Line, file_name=None, lineno=None):

                line_stripped = self.StripComment(Line).strip()

                if(len(line_stripped) < 1):

                    return ("", [], None)

        

                line_resolved = self.ReplaceVariables(line_stripped)

                if(self.ProcessConditional(line_resolved)):

                    # was a conditional

                    # Other parser returns line_resolved, [].  Need to figure out which is right

                    return ("", [], None)

        

                # not conditional keep procesing

        

                # check if conditional is active

                if(not self.InActiveCode()):

                    return ("", [], None)

        

                # check for include file and import lines from file

                if(line_resolved.strip().lower().startswith("!include")):

                    # include line.

                    tokens = line_resolved.split()

                    self.Logger.debug("Opening Include File %s" % os.path.join(self.RootPath, tokens[1]))

                    sp = self.FindPath(tokens[1])

                    self._dsc_file_paths.add(sp)

                    lf = open(sp, "r")

                    loc = lf.readlines()

                    lf.close()

                    return ("", loc, sp)

        

                # check for new section

                (IsNew, Section) = self.ParseNewSection(line_resolved)

                if(IsNew):

                    self.CurrentSection = Section.upper()

                    self.Logger.debug("New Section: %s" % self.CurrentSection)

                    self.Logger.debug("FullSection: %s" % self.CurrentFullSection)

                    return (line_resolved, [], None)

        

                # process line in x64 components

                if(self.CurrentFullSection.upper() == "COMPONENTS.X64"):

                    if(self.ParsingInBuildOption > 0):

                        if(".inf" in line_resolved.lower()):

                            p = self.ParseInfPathLib(line_resolved)

                            self.Libs.append(p)

                            self.Logger.debug("Found Library in a 64bit BuildOptions Section: %s" % p)

                        elif "tokenspaceguid" in line_resolved.lower() and \

                                line_resolved.count('|') > 0 and line_resolved.count('.') > 0:

                            # should be a pcd statement

                            p = line_resolved.partition('|')

                            self.Pcds.append(p[0].strip())

                            self.Logger.debug("Found a Pcd in a 64bit Module Override section: %s" % p[0].strip())

                    else:

                        if(".inf" in line_resolved.lower()):

                            p = self.ParseInfPathMod(line_resolved)

                            self.SixMods.append(p)

                            if file_name is not None and lineno is not None:

                                self.SixModsEnhanced.append({'file': os.path.normpath(file_name), 'lineno': lineno, 'data': p})

                            self.Logger.debug("Found 64bit Module: %s" % p)

        

                    self.ParsingInBuildOption = self.ParsingInBuildOption + line_resolved.count("{")

                    self.ParsingInBuildOption = self.ParsingInBuildOption - line_resolved.count("}")

                    return (line_resolved, [], None)

        

                # process line in ia32 components

                elif(self.CurrentFullSection.upper() == "COMPONENTS.IA32"):

                    if(self.ParsingInBuildOption > 0):

                        if(".inf" in line_resolved.lower()):

                            p = self.ParseInfPathLib(line_resolved)

                            self.Libs.append(p)

                            if file_name is not None and lineno is not None:

                                self.LibsEnhanced.append({'file': os.path.normpath(file_name), 'lineno': lineno, 'data': p})

                            self.Logger.debug("Found Library in a 32bit BuildOptions Section: %s" % p)

                        elif "tokenspaceguid" in line_resolved.lower() and \

                                line_resolved.count('|') > 0 and line_resolved.count('.') > 0:

                            # should be a pcd statement

                            p = line_resolved.partition('|')

                            self.Pcds.append(p[0].strip())

                            self.Logger.debug("Found a Pcd in a 32bit Module Override section: %s" % p[0].strip())

        

                    else:

                        if(".inf" in line_resolved.lower()):

                            p = self.ParseInfPathMod(line_resolved)

                            self.ThreeMods.append(p)

                            if file_name is not None and lineno is not None:

                                self.ThreeModsEnhanced.append({'file': os.path.normpath(file_name),

                                                               'lineno': lineno, 'data': p})

                            self.Logger.debug("Found 32bit Module: %s" % p)

        

                    self.ParsingInBuildOption = self.ParsingInBuildOption + line_resolved.count("{")

                    self.ParsingInBuildOption = self.ParsingInBuildOption - line_resolved.count("}")

                    return (line_resolved, [], None)

        

                # process line in other components

                elif("COMPONENTS" in self.CurrentFullSection.upper()):

                    if(self.ParsingInBuildOption > 0):

                        if(".inf" in line_resolved.lower()):

                            p = self.ParseInfPathLib(line_resolved)

                            self.Libs.append(p)

                            self.Logger.debug("Found Library in a BuildOptions Section: %s" % p)

                        elif "tokenspaceguid" in line_resolved.lower() and \

                                line_resolved.count('|') > 0 and line_resolved.count('.') > 0:

                            # should be a pcd statement

                            p = line_resolved.partition('|')

                            self.Pcds.append(p[0].strip())

                            self.Logger.debug("Found a Pcd in a Module Override section: %s" % p[0].strip())

        

                    else:

                        if(".inf" in line_resolved.lower()):

                            p = self.ParseInfPathMod(line_resolved)

                            self.OtherMods.append(p)

                            self.Logger.debug("Found Module: %s" % p)

        

                    self.ParsingInBuildOption = self.ParsingInBuildOption + line_resolved.count("{")

                    self.ParsingInBuildOption = self.ParsingInBuildOption - line_resolved.count("}")

                    return (line_resolved, [], None)

        

                # process line in library class section (don't use full name)

                elif(self.CurrentSection.upper() == "LIBRARYCLASSES"):

                    if(".inf" in line_resolved.lower()):

                        p = self.ParseInfPathLib(line_resolved)

                        self.Libs.append(p)

                        self.Logger.debug("Found Library in Library Class Section: %s" % p)

                    return (line_resolved, [], None)

                # process line in PCD section

                elif(self.CurrentSection.upper().startswith("PCDS")):

                    if "tokenspaceguid" in line_resolved.lower() and \

                            line_resolved.count('|') > 0 and line_resolved.count('.') > 0:

                        # should be a pcd statement

                        p = line_resolved.partition('|')

                        self.Pcds.append(p[0].strip())

                        self.Logger.debug("Found a Pcd in a PCD section: %s" % p[0].strip())

                    return (line_resolved, [], None)

                else:

                    return (line_resolved, [], None)

        

            def __ParseDefineLine(self, Line):

                line_stripped = self.StripComment(Line).strip()

                if(len(line_stripped) < 1):

                    return ("", [])

        

                # this line needs to be here to resolve any symbols inside the !include lines, if any

                line_resolved = self.ReplaceVariables(line_stripped)

                if(self.ProcessConditional(line_resolved)):

                    # was a conditional

                    # Other parser returns line_resolved, [].  Need to figure out which is right

                    return ("", [])

        

                # not conditional keep procesing

        

                # check if conditional is active

                if(not self.InActiveCode()):

                    return ("", [])

        

                # check for include file and import lines from file

                if(line_resolved.strip().lower().startswith("!include")):

                    # include line.

                    tokens = line_resolved.split()

                    self.Logger.debug("Opening Include File %s" % os.path.join(self.RootPath, tokens[1]))

                    sp = self.FindPath(tokens[1])

                    lf = open(sp, "r")

                    loc = lf.readlines()

                    lf.close()

                    return ("", loc)

        

                # check for new section

                (IsNew, Section) = self.ParseNewSection(line_resolved)

                if(IsNew):

                    self.CurrentSection = Section.upper()

                    self.Logger.debug("New Section: %s" % self.CurrentSection)

                    self.Logger.debug("FullSection: %s" % self.CurrentFullSection)

                    return (line_resolved, [])

        

                # process line based on section we are in

                if(self.CurrentSection == "DEFINES") or (self.CurrentSection == "BUILDOPTIONS"):

                    if line_resolved.count("=") >= 1:

                        tokens = line_resolved.split("=", 1)

                        leftside = tokens[0].split()

                        if(len(leftside) == 2):

                            left = leftside[1]

                        else:

                            left = leftside[0]

                        right = tokens[1].strip()

        

                        self.LocalVars[left] = right

                        self.Logger.debug("Key,values found:  %s = %s" % (left, right))

        

                        # iterate through the existed LocalVars and try to resolve the symbols

                        for var in self.LocalVars:

                            self.LocalVars[var] = self.ReplaceVariables(self.LocalVars[var])

                        return (line_resolved, [])

                else:

                    return (line_resolved, [])

        

            def ParseInfPathLib(self, line):

                if(line.count("|") > 0):

                    line_parts = []

                    c = line.split("|")[0].strip()

                    i = line.split("|")[1].strip()

                    if(c in self.LibraryClassToInstanceDict):

                        line_parts = self.LibraryClassToInstanceDict.get(c)

                    sp = self.FindPath(i)

                    line_parts.append(sp)

                    self.LibraryClassToInstanceDict[c] = line_parts

                    return line.split("|")[1].strip()

                else:

                    return line.strip().split()[0]

        

            def ParseInfPathMod(self, line):

                return line.strip().split()[0].rstrip("{")

        

            def __ProcessMore(self, lines, file_name=None):

                if(len(lines) > 0):

                    for index in range(0, len(lines)):

                        (line, add, new_file) = self.__ParseLine(lines[index], file_name=file_name, lineno=index + 1)

                        if(len(line) > 0):

                            self.Lines.append(line)

                        self.__ProcessMore(add, file_name=new_file)

        

            def __ProcessDefines(self, lines):

                if(len(lines) > 0):

                    for l in lines:

                        (line, add) = self.__ParseDefineLine(l)

                        self.__ProcessDefines(add)

        

            def ResetParserState(self):

                #

                # add more DSC parser based state reset here, if necessary

                #

                super(DscParser, self).ResetParserState()

        

            def ParseFile(self, filepath):

                self.Logger.debug("Parsing file: %s" % filepath)

                self.TargetFile = os.path.abspath(filepath)

                self.TargetFilePath = os.path.dirname(self.TargetFile)

                sp = os.path.join(filepath)

                self._dsc_file_paths.add(sp)

                f = open(sp, "r")

                # expand all the lines and include other files

                file_lines = f.readlines()

                self.__ProcessDefines(file_lines)

                # reset the parser state before processing more

                self.ResetParserState()

                self.__ProcessMore(file_lines, file_name=sp)

                f.close()

                self.Parsed = True

        

            def GetMods(self):

                return self.ThreeMods + self.SixMods

        

            def GetModsEnhanced(self):

                return self.ThreeModsEnhanced + self.SixModsEnhanced

        

            def GetLibs(self):

                return self.Libs

        

            def GetLibsEnhanced(self):

                return self.LibsEnhanced

        

            def GetAllDscPaths(self):

                ''' returns an iterable with all the paths that this DSC uses (the base file and any includes).

                    They are not all guaranteed to be DSC files '''

                return self._dsc_file_paths

Classes
-------

### DscParser

```python3
class DscParser(
    
)
```

??? example "View Source"
        class DscParser(HashFileParser):

        

            def __init__(self):

                super(DscParser, self).__init__('DscParser')

                self.SixMods = []

                self.SixModsEnhanced = []

                self.ThreeMods = []

                self.ThreeModsEnhanced = []

                self.OtherMods = []

                self.Libs = []

                self.LibsEnhanced = []

                self.ParsingInBuildOption = 0

                self.LibraryClassToInstanceDict = {}

                self.Pcds = []

                self._dsc_file_paths = set()  # This includes the full paths for every DSC that makes up the file

        

            def __ParseLine(self, Line, file_name=None, lineno=None):

                line_stripped = self.StripComment(Line).strip()

                if(len(line_stripped) < 1):

                    return ("", [], None)

        

                line_resolved = self.ReplaceVariables(line_stripped)

                if(self.ProcessConditional(line_resolved)):

                    # was a conditional

                    # Other parser returns line_resolved, [].  Need to figure out which is right

                    return ("", [], None)

        

                # not conditional keep procesing

        

                # check if conditional is active

                if(not self.InActiveCode()):

                    return ("", [], None)

        

                # check for include file and import lines from file

                if(line_resolved.strip().lower().startswith("!include")):

                    # include line.

                    tokens = line_resolved.split()

                    self.Logger.debug("Opening Include File %s" % os.path.join(self.RootPath, tokens[1]))

                    sp = self.FindPath(tokens[1])

                    self._dsc_file_paths.add(sp)

                    lf = open(sp, "r")

                    loc = lf.readlines()

                    lf.close()

                    return ("", loc, sp)

        

                # check for new section

                (IsNew, Section) = self.ParseNewSection(line_resolved)

                if(IsNew):

                    self.CurrentSection = Section.upper()

                    self.Logger.debug("New Section: %s" % self.CurrentSection)

                    self.Logger.debug("FullSection: %s" % self.CurrentFullSection)

                    return (line_resolved, [], None)

        

                # process line in x64 components

                if(self.CurrentFullSection.upper() == "COMPONENTS.X64"):

                    if(self.ParsingInBuildOption > 0):

                        if(".inf" in line_resolved.lower()):

                            p = self.ParseInfPathLib(line_resolved)

                            self.Libs.append(p)

                            self.Logger.debug("Found Library in a 64bit BuildOptions Section: %s" % p)

                        elif "tokenspaceguid" in line_resolved.lower() and \

                                line_resolved.count('|') > 0 and line_resolved.count('.') > 0:

                            # should be a pcd statement

                            p = line_resolved.partition('|')

                            self.Pcds.append(p[0].strip())

                            self.Logger.debug("Found a Pcd in a 64bit Module Override section: %s" % p[0].strip())

                    else:

                        if(".inf" in line_resolved.lower()):

                            p = self.ParseInfPathMod(line_resolved)

                            self.SixMods.append(p)

                            if file_name is not None and lineno is not None:

                                self.SixModsEnhanced.append({'file': os.path.normpath(file_name), 'lineno': lineno, 'data': p})

                            self.Logger.debug("Found 64bit Module: %s" % p)

        

                    self.ParsingInBuildOption = self.ParsingInBuildOption + line_resolved.count("{")

                    self.ParsingInBuildOption = self.ParsingInBuildOption - line_resolved.count("}")

                    return (line_resolved, [], None)

        

                # process line in ia32 components

                elif(self.CurrentFullSection.upper() == "COMPONENTS.IA32"):

                    if(self.ParsingInBuildOption > 0):

                        if(".inf" in line_resolved.lower()):

                            p = self.ParseInfPathLib(line_resolved)

                            self.Libs.append(p)

                            if file_name is not None and lineno is not None:

                                self.LibsEnhanced.append({'file': os.path.normpath(file_name), 'lineno': lineno, 'data': p})

                            self.Logger.debug("Found Library in a 32bit BuildOptions Section: %s" % p)

                        elif "tokenspaceguid" in line_resolved.lower() and \

                                line_resolved.count('|') > 0 and line_resolved.count('.') > 0:

                            # should be a pcd statement

                            p = line_resolved.partition('|')

                            self.Pcds.append(p[0].strip())

                            self.Logger.debug("Found a Pcd in a 32bit Module Override section: %s" % p[0].strip())

        

                    else:

                        if(".inf" in line_resolved.lower()):

                            p = self.ParseInfPathMod(line_resolved)

                            self.ThreeMods.append(p)

                            if file_name is not None and lineno is not None:

                                self.ThreeModsEnhanced.append({'file': os.path.normpath(file_name),

                                                               'lineno': lineno, 'data': p})

                            self.Logger.debug("Found 32bit Module: %s" % p)

        

                    self.ParsingInBuildOption = self.ParsingInBuildOption + line_resolved.count("{")

                    self.ParsingInBuildOption = self.ParsingInBuildOption - line_resolved.count("}")

                    return (line_resolved, [], None)

        

                # process line in other components

                elif("COMPONENTS" in self.CurrentFullSection.upper()):

                    if(self.ParsingInBuildOption > 0):

                        if(".inf" in line_resolved.lower()):

                            p = self.ParseInfPathLib(line_resolved)

                            self.Libs.append(p)

                            self.Logger.debug("Found Library in a BuildOptions Section: %s" % p)

                        elif "tokenspaceguid" in line_resolved.lower() and \

                                line_resolved.count('|') > 0 and line_resolved.count('.') > 0:

                            # should be a pcd statement

                            p = line_resolved.partition('|')

                            self.Pcds.append(p[0].strip())

                            self.Logger.debug("Found a Pcd in a Module Override section: %s" % p[0].strip())

        

                    else:

                        if(".inf" in line_resolved.lower()):

                            p = self.ParseInfPathMod(line_resolved)

                            self.OtherMods.append(p)

                            self.Logger.debug("Found Module: %s" % p)

        

                    self.ParsingInBuildOption = self.ParsingInBuildOption + line_resolved.count("{")

                    self.ParsingInBuildOption = self.ParsingInBuildOption - line_resolved.count("}")

                    return (line_resolved, [], None)

        

                # process line in library class section (don't use full name)

                elif(self.CurrentSection.upper() == "LIBRARYCLASSES"):

                    if(".inf" in line_resolved.lower()):

                        p = self.ParseInfPathLib(line_resolved)

                        self.Libs.append(p)

                        self.Logger.debug("Found Library in Library Class Section: %s" % p)

                    return (line_resolved, [], None)

                # process line in PCD section

                elif(self.CurrentSection.upper().startswith("PCDS")):

                    if "tokenspaceguid" in line_resolved.lower() and \

                            line_resolved.count('|') > 0 and line_resolved.count('.') > 0:

                        # should be a pcd statement

                        p = line_resolved.partition('|')

                        self.Pcds.append(p[0].strip())

                        self.Logger.debug("Found a Pcd in a PCD section: %s" % p[0].strip())

                    return (line_resolved, [], None)

                else:

                    return (line_resolved, [], None)

        

            def __ParseDefineLine(self, Line):

                line_stripped = self.StripComment(Line).strip()

                if(len(line_stripped) < 1):

                    return ("", [])

        

                # this line needs to be here to resolve any symbols inside the !include lines, if any

                line_resolved = self.ReplaceVariables(line_stripped)

                if(self.ProcessConditional(line_resolved)):

                    # was a conditional

                    # Other parser returns line_resolved, [].  Need to figure out which is right

                    return ("", [])

        

                # not conditional keep procesing

        

                # check if conditional is active

                if(not self.InActiveCode()):

                    return ("", [])

        

                # check for include file and import lines from file

                if(line_resolved.strip().lower().startswith("!include")):

                    # include line.

                    tokens = line_resolved.split()

                    self.Logger.debug("Opening Include File %s" % os.path.join(self.RootPath, tokens[1]))

                    sp = self.FindPath(tokens[1])

                    lf = open(sp, "r")

                    loc = lf.readlines()

                    lf.close()

                    return ("", loc)

        

                # check for new section

                (IsNew, Section) = self.ParseNewSection(line_resolved)

                if(IsNew):

                    self.CurrentSection = Section.upper()

                    self.Logger.debug("New Section: %s" % self.CurrentSection)

                    self.Logger.debug("FullSection: %s" % self.CurrentFullSection)

                    return (line_resolved, [])

        

                # process line based on section we are in

                if(self.CurrentSection == "DEFINES") or (self.CurrentSection == "BUILDOPTIONS"):

                    if line_resolved.count("=") >= 1:

                        tokens = line_resolved.split("=", 1)

                        leftside = tokens[0].split()

                        if(len(leftside) == 2):

                            left = leftside[1]

                        else:

                            left = leftside[0]

                        right = tokens[1].strip()

        

                        self.LocalVars[left] = right

                        self.Logger.debug("Key,values found:  %s = %s" % (left, right))

        

                        # iterate through the existed LocalVars and try to resolve the symbols

                        for var in self.LocalVars:

                            self.LocalVars[var] = self.ReplaceVariables(self.LocalVars[var])

                        return (line_resolved, [])

                else:

                    return (line_resolved, [])

        

            def ParseInfPathLib(self, line):

                if(line.count("|") > 0):

                    line_parts = []

                    c = line.split("|")[0].strip()

                    i = line.split("|")[1].strip()

                    if(c in self.LibraryClassToInstanceDict):

                        line_parts = self.LibraryClassToInstanceDict.get(c)

                    sp = self.FindPath(i)

                    line_parts.append(sp)

                    self.LibraryClassToInstanceDict[c] = line_parts

                    return line.split("|")[1].strip()

                else:

                    return line.strip().split()[0]

        

            def ParseInfPathMod(self, line):

                return line.strip().split()[0].rstrip("{")

        

            def __ProcessMore(self, lines, file_name=None):

                if(len(lines) > 0):

                    for index in range(0, len(lines)):

                        (line, add, new_file) = self.__ParseLine(lines[index], file_name=file_name, lineno=index + 1)

                        if(len(line) > 0):

                            self.Lines.append(line)

                        self.__ProcessMore(add, file_name=new_file)

        

            def __ProcessDefines(self, lines):

                if(len(lines) > 0):

                    for l in lines:

                        (line, add) = self.__ParseDefineLine(l)

                        self.__ProcessDefines(add)

        

            def ResetParserState(self):

                #

                # add more DSC parser based state reset here, if necessary

                #

                super(DscParser, self).ResetParserState()

        

            def ParseFile(self, filepath):

                self.Logger.debug("Parsing file: %s" % filepath)

                self.TargetFile = os.path.abspath(filepath)

                self.TargetFilePath = os.path.dirname(self.TargetFile)

                sp = os.path.join(filepath)

                self._dsc_file_paths.add(sp)

                f = open(sp, "r")

                # expand all the lines and include other files

                file_lines = f.readlines()

                self.__ProcessDefines(file_lines)

                # reset the parser state before processing more

                self.ResetParserState()

                self.__ProcessMore(file_lines, file_name=sp)

                f.close()

                self.Parsed = True

        

            def GetMods(self):

                return self.ThreeMods + self.SixMods

        

            def GetModsEnhanced(self):

                return self.ThreeModsEnhanced + self.SixModsEnhanced

        

            def GetLibs(self):

                return self.Libs

        

            def GetLibsEnhanced(self):

                return self.LibsEnhanced

        

            def GetAllDscPaths(self):

                ''' returns an iterable with all the paths that this DSC uses (the base file and any includes).

                    They are not all guaranteed to be DSC files '''

                return self._dsc_file_paths

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

    
#### GetAllDscPaths

```python3
def GetAllDscPaths(
    self
)
```
returns an iterable with all the paths that this DSC uses (the base file and any includes).
They are not all guaranteed to be DSC files 

??? example "View Source"
            def GetAllDscPaths(self):

                ''' returns an iterable with all the paths that this DSC uses (the base file and any includes).

                    They are not all guaranteed to be DSC files '''

                return self._dsc_file_paths

    
#### GetLibs

```python3
def GetLibs(
    self
)
```

??? example "View Source"
            def GetLibs(self):

                return self.Libs

    
#### GetLibsEnhanced

```python3
def GetLibsEnhanced(
    self
)
```

??? example "View Source"
            def GetLibsEnhanced(self):

                return self.LibsEnhanced

    
#### GetMods

```python3
def GetMods(
    self
)
```

??? example "View Source"
            def GetMods(self):

                return self.ThreeMods + self.SixMods

    
#### GetModsEnhanced

```python3
def GetModsEnhanced(
    self
)
```

??? example "View Source"
            def GetModsEnhanced(self):

                return self.ThreeModsEnhanced + self.SixModsEnhanced

    
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

                self.TargetFile = os.path.abspath(filepath)

                self.TargetFilePath = os.path.dirname(self.TargetFile)

                sp = os.path.join(filepath)

                self._dsc_file_paths.add(sp)

                f = open(sp, "r")

                # expand all the lines and include other files

                file_lines = f.readlines()

                self.__ProcessDefines(file_lines)

                # reset the parser state before processing more

                self.ResetParserState()

                self.__ProcessMore(file_lines, file_name=sp)

                f.close()

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

    
#### ParseInfPathLib

```python3
def ParseInfPathLib(
    self,
    line
)
```

??? example "View Source"
            def ParseInfPathLib(self, line):

                if(line.count("|") > 0):

                    line_parts = []

                    c = line.split("|")[0].strip()

                    i = line.split("|")[1].strip()

                    if(c in self.LibraryClassToInstanceDict):

                        line_parts = self.LibraryClassToInstanceDict.get(c)

                    sp = self.FindPath(i)

                    line_parts.append(sp)

                    self.LibraryClassToInstanceDict[c] = line_parts

                    return line.split("|")[1].strip()

                else:

                    return line.strip().split()[0]

    
#### ParseInfPathMod

```python3
def ParseInfPathMod(
    self,
    line
)
```

??? example "View Source"
            def ParseInfPathMod(self, line):

                return line.strip().split()[0].rstrip("{")

    
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

                #

                # add more DSC parser based state reset here, if necessary

                #

                super(DscParser, self).ResetParserState()

    
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