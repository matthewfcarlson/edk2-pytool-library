# @file recipte_parser.py
# Code to help parse DSC files into recipes
#
# Copyright (c) Microsoft Corporation
#
# SPDX-License-Identifier: BSD-2-Clause-Patent
##
from edk2toollib.uefi.edk2.parsers.dsc_parser import DscParser
from edk2toollib.uefi.edk2.build_objects.recipe import recipe
from edk2toollib.uefi.edk2.build_objects.recipe import source_info
from edk2toollib.uefi.edk2.build_objects.recipe import component
from edk2toollib.uefi.edk2.build_objects.recipe import sku_id
from edk2toollib.uefi.edk2.build_objects.recipe import pcd
import os


class RecipeParser(DscParser):
    ''' 
    This acts like a normal DscParser, but outputs recipes 
    Returns none if a file has not been parsed yet
    '''

    def GetRecipe(self):
        if not self.Parsed:
            return None
        rec = recipe()

        # process libraries
        libraries = self.GetLibsEnhanced()
        for library in libraries:
            pass
            # print(library)
            # raise ValueError()
        
        # process Skus
        skus = self.GetSkus()
        for s in skus:
            rec.skus.add(sku_id(s["id"], s["name"], s["parent"]))

        # process PCD's
        pcds = self.GetPcds()
        pcd_store = set()
        for p in pcds:
            namespace, name = p.split(".")
            new_pcd = pcd(namespace, name)
            pcd_store.add(new_pcd)            
            # TODO extend PCD in base parser
            
        print(pcd_store)
        
        # process components
        modules = self.GetModsEnhanced()
        for module in modules:
            pass
            source = source_info(module['file'], module['lineno'])
            comp = component(module['data'], [], source)
            rec.components.add(comp)
            # TODO - we should have parsed all the libraries
            # TODO- we should have parsed the skus
            
            #raise ValueError()
        return rec
