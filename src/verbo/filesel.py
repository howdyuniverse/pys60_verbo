# -*- coding: utf-8 -*-
"""
Milkshake
Copyright (C) 2009  Marcelo Barros & Jose Antonio Oliveira

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.


Milkshake
Copyright (C) 2009  Marcelo Barros & Jose Antonio Oliveira
This program comes with ABSOLUTELY NO WARRANTY; for details see 
about box.
This is free software, and you are welcome to redistribute it
under certain conditions; see about box for details.
"""

"""
Open a selection file dialog. Returns the file selected or None.
Initial path and regular expression for filtering file list may be provided.

Examples:
sel = FileSel().run()
if sel is not None:
    ...

sel = FileSel(mask = r"(.*\.jpeg|.*\.jpg|.*\.png|.*\.gif)").run()
if sel is not None:
    ...

"""

import os
import e32
from appuifw import *
import re

class FileSel(object):
    def __init__(self,init_dir = "", mask = ".*"):
        self.cur_dir = unicode(init_dir)
        if not os.path.exists(self.cur_dir):
            self.cur_dir = ""
        self.mask = mask
        self.fill_items()
        
    def fill_items(self):
        if self.cur_dir == u"":
            self.items = [ unicode(d + "\\") for d in e32.drive_list() ]
        else:
            entries = [ e.decode('utf-8')
                        for e in os.listdir( self.cur_dir.encode('utf-8') ) ]
            d = self.cur_dir
            dirs  = [ e.upper() for e in entries
                      if os.path.isdir(os.path.join(d,e).encode('utf-8'))  ]
            
            files = [ e.lower() for e in entries
                      if os.path.isfile(os.path.join(d,e).encode('utf-8')) ]
            
            files = [ f for f in files
                      if re.match(self.mask,f) ]
            dirs.sort()
            files.sort()
            dirs.insert( 0, u".." )
            self.items = dirs + files
        
    def run(self):
        while True:
            item = popup_menu(self.items,u"Select file:")
            if item is None:
                return None
            f = self.items[item]
            d = os.path.abspath( os.path.join(self.cur_dir,f) )
            if os.path.isdir( d.encode('utf-8') ):
                if f == u".." and len(self.cur_dir) == 3:
                    self.cur_dir = u""
                else:
                    self.cur_dir = d 
                self.fill_items()
            elif os.path.isfile( d.encode('utf-8') ):
                return d
              

