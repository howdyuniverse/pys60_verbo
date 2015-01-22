# -*- coding: utf-8 -*-
"""
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

Marcelo Barros de Almeida <marcelobarrosalmeida (at) gmail.com>
Copyright (C) 2009  Marcelo Barros de Almeida
This program comes with ABSOLUTELY NO WARRANTY; for details see 
about box.
This is free software, and you are welcome to redistribute it
under certain conditions; see about box for details.

== Introduction ==

The API for writing applications using Python for S60 is really straightforward.
Since you have decided what kind of body your  application will use (canvas,
listbox, or text), you need to define your main menu, application title
and default callback handler for exiting. The user interface (UI) is based
on events and there is a special mechanism that relies on a semaphore for
indicating if the application is closing. The user must obtain the semaphore
and wait for any signal on it. Once signalized, the application may close
properly. The UI allows tabs as well but in this case a body must be defined
for each tab. An routine for handling tabs changing is required in such
situation. 

However, if your application has more than one window, I mean, more than a
set of body, menu and exit handler, you will need exchanging these elements
each time a new window is displayed, giving to the user the impression that
he is using a multiple windows application. Although this solution is possible,
some problems arise:

* the strategy for exiting, based on semaphores, must be unique across your
  application.
* you can not commit any mistake when switching UI, that is, the set
  body+menu+exit handler must be consistently changed   
* an unified strategy for blocking UI when a time consuming operation is
  pending is necessary. For instance, when downloading a file, you may want
  to disable all menu options.  Otherwise they will be available for the user
  during the download operation.


For unifying this process, three additional classes are suggested in this
article. The first, called Window, is responsible for holding UI contents
like menu, body and exit handler and exchanging properly all UI elements
for the derived classes. Moreover, it may lock/unlock the UI when necessary.
The second class is named Application. It represents the running application
itself and it is responsible for handling the termination semaphore. Only one
Application class must be instantiated per application. Finally, the third
class is called Dialog. As its name suggests, it is in the charge of
showing/hiding dialogs when necessary. Many dialogs are allowed, each one
with their own set of body+menu+exit handler.  

Application and Dialog inherit from Window the content handler ability while
each one has different ways for finishing itself (finishing application or
just the dialog).

== Usage examples == 

Using this framework, user attention is focused on application and not
on appuifw stuff. Consider this first example, with only one window
(no dialogs). Since your program inherits from Application, default actions
for some specific appuifw are already defined:

* Termination semaphore is controlled by Application class, being properly
initialized inside its constructor (Application.__lock = e32.Ao_lock()).
Only one Application object per program is allowed.
* exit_default_handler is set to Application.close_app(), where termination
semaphore is set (Application.__lock.signal()).
* Application.run() initializes the application, calling refresh() for
updating the UI and waits for termination semaphore. When signalized, all
necessary cleanup is done and application is closed.

We can see one simple example in action:

<code python>
# -*- coding: utf-8 -*-
#
# Marcelo Barros de Almeida
# marcelobarrosalmeida (at) gmail.com
#
from window import Application
from appuifw import Listbox, note

class MyApp(Application):
    def __init__(self):
        items = [ u"Option A",
                  u"Option B",
                  u"Option C" ]
        menu = [ (u"Menu A", self.option_a),
                 (u"Menu B", self.option_b),
                 (u"Menu C", self.option_c) ]
        body = Listbox(items, self.check_items )
        Application.__init__(self,
                             u"MyApp title",
                             body,
                             menu)
    
    def check_items(self):
        idx = self.body.current()
        ( self.option_a, self.option_b, self.option_c )[idx]()

    def option_a(self): note(u"A","info")
    def option_b(self): note(u"B","info")
    def option_c(self): note(u"C","info")

if __name__ == "__main__":

    app = MyApp()
    app.run()
</code>

Of course, if you need special actions, like some confirmation when exiting,
this may be implemented just overriding close_app():

<code python>
# -*- coding: utf-8 -*-
#
# Marcelo Barros de Almeida
# marcelobarrosalmeida (at) gmail.com
#
from window import Application
from appuifw import Listbox, note, popup_menu

class MyApp(Application):
    def __init__(self):
        items = [ u"Option A",
                  u"Option B",
                  u"Option C" ]
        menu = [ (u"Menu A", self.option_a),
                 (u"Menu B", self.option_b),
                 (u"Menu C", self.option_c) ]
        body = Listbox(items, self.check_items )
        Application.__init__(self,
                             u"MyApp title",
                             body,
                             menu)
    
    def check_items(self):
        idx = self.body.current()
        ( self.option_a, self.option_b, self.option_c )[idx]()

    def option_a(self): note(u"A","info")
    def option_b(self): note(u"B","info")
    def option_c(self): note(u"C","info")

    def close_app(self):
        ny = popup_menu( [u"No", u"Yes"], u"Exit ?")
        if ny is not None:
            if ny == 1:
                Application.close_app(self)

if __name__ == "__main__":

    app = MyApp()
    app.run()
</code>

== Dialogs ==

Suppose now user wants to add a dialog call. Really simple and hiding all
appuifw stuff:

<code python>
# -*- coding: utf-8 -*-
#
# Marcelo Barros de Almeida
# marcelobarrosalmeida (at) gmail.com
#
from window import Application, Dialog
from appuifw import Listbox, note, popup_menu, Text

class Notepad(Dialog):
    def __init__(self, cbk, txt=u""):
        menu = [(u"Save", self.close_app),
                (u"Discard", self.cancel_app)]
        Dialog.__init__(self, cbk, u"MyDlg title", Text(txt), menu)
           
class MyApp(Application):
    def __init__(self):
        self.txt = u""
        items = [ u"Text editor",
                  u"Option B",
                  u"Option C" ]
        menu = [ (u"Text editor", self.text_editor),
                 (u"Menu B", self.option_b),
                 (u"Menu C", self.option_c) ]
        body = Listbox(items, self.check_items )
        Application.__init__(self,
                             u"MyApp title",
                             body,
                             menu)
    
    def check_items(self):
        idx = self.body.current()
        ( self.text_editor, self.option_b, self.option_c )[idx]()

    def text_editor(self):
        def cbk():
            if not self.dlg.cancel:
                self.txt = self.dlg.body.get()
                note(self.txt, "info")
            self.refresh()
            return True
        
        self.dlg = Notepad(cbk, self.txt)
        self.dlg.run()
        
    def option_b(self): note(u"B","info")
    def option_c(self): note(u"C","info")

    def close_app(self):
        ny = popup_menu( [u"No", u"Yes"], u"Exit ?")
        if ny is not None:
            if ny == 1:
                Application.close_app(self)

if __name__ == "__main__":

    app = MyApp()
    app.run()
</code>

When a dialog is created, a callback function need to be defined. This
callback is called when the user cancels or closes the dialog. Inside the
callback body, it is possible to check if the dialog was canceled just
verifying the cancel variable. Dialog variables may be accessed as well
as in any other python object and this is the way of retrieving dialog data. 

The callback function must either return True or False, before finishing.
If it returns '''True''', ''self.refresh() must be called before, inside
callback body''. This way, the ''menu, body and exit handler will be updated
using the context of the dialog caller'' (MyApp, in this case).
If it returns '''False''', ''self.refresh() is called inside dialog context
and the dialog is restored''. This is an excellent way to check dialog data
and to avoid data loss. A better example with this feature is given below
(see '''number_sel()''' method).

<code python>
# -*- coding: utf-8 -*-
#
# Marcelo Barros de Almeida
# marcelobarrosalmeida (at) gmail.com
#
from window import Application, Dialog
from appuifw import Listbox, note, popup_menu, Text

class Notepad(Dialog):
    def __init__(self, cbk, txt=u""):
        menu = [(u"Save", self.close_app),
                (u"Discard", self.cancel_app)]
        Dialog.__init__(self, cbk, u"MyDlg title", Text(txt), menu)

class NumSel(Dialog):
    def __init__(self, cbk):
        self.items = [ u"1", u"2", u"a", u"b" ]
        Dialog.__init__(self, cbk,
                        u"Select a number",
                        Listbox(self.items, self.close_app))
        
class MyApp(Application):
    def __init__(self):
        self.txt = u""
        items = [ u"Text editor",
                  u"Number selection",
                  u"Option C" ]
        menu = [ (u"Text editor", self.text_editor),
                 (u"Number selection", self.number_sel),
                 (u"Menu C", self.option_c) ]
        body = Listbox(items, self.check_items )
        Application.__init__(self,
                             u"MyApp title",
                             body,
                             menu)
    
    def check_items(self):
        idx = self.body.current()
        ( self.text_editor, self.number_sel, self.option_c )[idx]()

    def text_editor(self):
        def cbk():
            if not self.dlg.cancel:
                self.txt = self.dlg.body.get()
                note(self.txt, "info")
            self.refresh()
            return True
        
        self.dlg = Notepad(cbk, self.txt)
        self.dlg.run()
        
    def number_sel(self):
        def cbk():
            if not self.dlg.cancel:
                val = self.dlg.items[self.dlg.body.current()]
                try:
                    n = int(val)
                except:
                    note(u"Invalid number. Try again.", "info")
                    return False
                note(u"Valid number", "info")
            self.refresh()
            return True
        
        self.dlg = NumSel(cbk)
        self.dlg.run()
        
    def option_c(self): note(u"C","info")

    def close_app(self):
        ny = popup_menu( [u"No", u"Yes"], u"Exit ?")
        if ny is not None:
            if ny == 1:
                Application.close_app(self)

if __name__ == "__main__":

    app = MyApp()
    app.run()
</code>

As last example, how about changing menu and body dynamically ? Yes, it is
possible, just overriding '''refresh()'''. refresh() is responsible for
all UI updates, assigning desired values for menu, body and exit_handler.
If you made changes to any UI elements, it is necessary to redraw it. In
the next example, '''NameList()''' dialog has its menu and body contents
changed dynamically.

<code python>
# -*- coding: utf-8 -*-
#
# Marcelo Barros de Almeida
# marcelobarrosalmeida (at) gmail.com
#
from window import Application, Dialog
from appuifw import Listbox, note, popup_menu, Text, query, app

class Notepad(Dialog):
    def __init__(self, cbk, txt=u""):
        menu = [(u"Save", self.close_app),
                (u"Discard", self.cancel_app)]
        Dialog.__init__(self, cbk, u"MyDlg title", Text(txt), menu)

class NumSel(Dialog):
    def __init__(self, cbk):
        self.items = [ u"1", u"2", u"a", u"b" ]
        Dialog.__init__(self, cbk,
                        u"Select a number",
                        Listbox(self.items, self.close_app))

class NameList(Dialog):
    def __init__(self, cbk, names=[]):
        self.names = names
        self.body = Listbox([(u"")],self.options)
        # Do not populate Listbox() ! Refresh will do this.
        Dialog.__init__(self, cbk, u"Name list", self.body)

    def options(self):
        op = popup_menu( [u"Insert", u"Del"] , u"Names:")
        if op is not None:
            if op == 0:
                name = query(u"New name:", "text", u"" )
                if name is not None:
                    self.names.append(name)
                    print self.names
            elif self.names:
                del self.names[self.body.current()]
            # Menu and body are changing !
            # You need to refresh the interface.
            self.refresh()

    def refresh(self):
        menu = []
        if self.names:
            menu = map(lambda x: (x, lambda: None), self.names)
            items = self.names
        else:
            items = [u"<empty>"]
        self.menu = menu + [(u"Exit", self.close_app)]
        self.body.set_list(items,0)
        # Since your self.menu and self.body have already defined their
        # new values, call base class refresh()
        Dialog.refresh(self)
        
class MyApp(Application):
    def __init__(self):
        self.txt = u""
        self.names = []
        items = [ u"Text editor",
                  u"Number selection",
                  u"Name list" ]
        menu = [ (u"Text editor", self.text_editor),
                 (u"Number selection", self.number_sel),
                 (u"Name list", self.name_list) ]
        body = Listbox(items, self.check_items )
        Application.__init__(self,
                             u"MyApp title",
                             body,
                             menu)
    
    def check_items(self):
        idx = self.body.current()
        ( self.text_editor, self.number_sel, self.name_list )[idx]()

    def text_editor(self):
        def cbk():
            if not self.dlg.cancel:
                self.txt = self.dlg.body.get()
                note(self.txt, "info")
            self.refresh()
            return True
        
        self.dlg = Notepad(cbk, self.txt)
        self.dlg.run()
        
    def number_sel(self):
        def cbk():
            if not self.dlg.cancel:
                val = self.dlg.items[self.dlg.body.current()]
                try:
                    n = int(val)
                except:
                    note(u"Invalid number", "info")
                    return False
                note(u"Valid number", "info")
            self.refresh()
            return True
        
        self.dlg = NumSel(cbk)
        self.dlg.run()
        
    def name_list(self):
        def cbk():
            if not self.dlg.cancel:
                self.names = self.dlg.names
            self.refresh()
            return True
        
        self.dlg = NameList(cbk, self.names)
        self.dlg.run()        

    def close_app(self):
        ny = popup_menu( [u"No", u"Yes"], u"Exit ?")
        if ny is not None:
            if ny == 1:
                Application.close_app(self)

if __name__ == "__main__":

    app = MyApp()
    app.run()
</code>

== Tabbed dialogs ==

Tabbed dialogs are supporting as well. In this case, the body must be replaced by a list of bodies with the following format:

[(tab_text, body, menu),(tab_text, body, menu),...]

            
where:
 * tab_text: unicode string used in tab
 * body: a valid body (Listbox, Text or Canvas)
 * menu: menu for that body

Each entry in this list will be displayed in a tab. You can specify a global menu to be added to the bottom of each tab menu. This way, it is simple to share common function (like exit) among all tabs. Just specify this menu when calling Dialog() or Application.

<code python>
# -*- coding: utf-8 -*-
#
# Marcelo Barros de Almeida
# marcelobarrosalmeida (at) gmail.com
# License: GPL3

from window import Application
from appuifw import *

class MyApp(Application):
    def __init__(self):
        # defining menus for each tab/body
        ma=[(u"menu a",lambda:self.msg(u"menu a"))]
        mb=[(u"menu b",lambda:self.msg(u"menu b"))]
        mc=[(u"menu c",lambda:self.msg(u"menu c"))]
        md=[(u"menu d",lambda:self.msg(u"menu d"))]
        # common menu for all tabs
        common_menu=[(u"common menu",lambda:self.msg(u"common menu"))]
        # bodies
        ba=Listbox([u"a",u"b",u"c"])
        bb=Canvas()
        bc=Text(u"Text")
        bd=Listbox([u"1",u"2",u"3"])
        
        Application.__init__(self,
                             u"MyApp title",
                             [(u"Tab a",ba,ma),(u"Tab b",bb,mb),
                              (u"Tab c",bc,mc),(u"Tab d",bd,md)],
                             common_menu)

    def msg(self,m):
        note(m,"info")
        
if __name__ == "__main__":
    app = MyApp()
    app.run()
</code>

== Locking UI ==

For time consuming operations, like network connections, it is interesting
to lock the user interface, avoiding undesired user actions. Two methods
are used in such situation: '''lock_ui()''' and '''unlock_ui()'''. Just
lock the UI, do wherever you want, and unlock UI. If you want, change the
application title during this locking. 

<code python>
self.lock_ui(u"Connecting...")
#
# your stuff here
#
self.unlock_ui()
self.set_title(u"My app")
</code>

"""

from appuifw import *
import e32
import key_codes

__all__ = [ "Application", "Dialog" ]

class Window(object):
    """ This class is responsible for holding UI contents like menu, body
        and exit handler and exchanging properly all UI elements for
        the derived classes. Moreover, it may lock/unlock the UI when necessary.
    """
    __ui_lock = False
    
    def __init__(self, title, body, global_menu = None, exit_handler = None):
        """ Creates a new window given a title, body or a set of bodies (for tabbed
            window) and optional global_menu and exit handler. Global menu is
            available for all tabs at bottom or it is used as the default
            menu for non tabbed window

            The list of bodies must have the following format:
                [(tab_text, body, menu),(tab_text, body, menu),...]
            
            where:
                tab_text: unicode string used in tab
                body: a valid body (Listbox, Text or Canvas)
                menu: typical menu            
        """
        self.set_ui(title, body, global_menu, exit_handler)
        
    def set_ui(self, title, body, global_menu = None, exit_handler = None):

        self.title = title
        self.tab_title = None
        
        if isinstance(body,list):
            self.tabbed = True
            self.bodies = body
            self.body = None
        else:
            self.tabbed = False
            self.bodies = None
            self.body = body
    
        if global_menu is None:
            global_menu = [(u"Exit", self.close_app)]

        if exit_handler is None:
            exit_handler = self.close_app

        self.global_menu = global_menu
        self.exit_handler = exit_handler
        self.last_tab = 0
        
    def set_title(self,title):
        " Sets the current application title "
        app.title = self.title = title

    def get_title(self):
        " Returns the current application title "
        return self.title

    def bind(self, key, cbk):
        " Bind a key to the body. A callback must be provided."
        self.body.bind(key,cbk)
        
    def refresh(self):
        " Update the application itens (menu, body and exit handler) "
        if self.tabbed:
            app.set_tabs([b[0] for b in self.bodies],self.tab_handler)
            self.tab_handler(self.last_tab)
            app.activate_tab(self.last_tab)
            # use tab title as title if we have just one tab
            if len(self.bodies) == 1:
                app.title = self.bodies[0][0]
        else:
            app.set_tabs([], None)
            app.menu = self.global_menu
            app.body = self.body
            self.tab_title = None
            app.title = self.title
        app.exit_key_handler = self.exit_handler

    def tab_handler(self,idx):
        " Update tab and its related contents "
        self.last_tab = idx
        self.tab_title = self.bodies[idx][0]
        self.body = self.bodies[idx][1]
        self.menu = self.bodies[idx][2] + self.global_menu
        app.title = self.title
        app.menu = self.menu
        app.body = self.body
        
    def run(self):
        " Show the dialog/application "
        self.refresh()
        
    def lock_ui(self,title = u""):
        """ Lock UI (menu, body and exit handler are disabled).
            You may set a string to be shown in the title area.
        """
        Window.__ui_lock = True
        app.menu = []
        app.set_tabs([], None)
        app.exit_key_handler = lambda: None
        if title:
            app.title = title

    def unlock_ui(self):
        "Unlock UI. Call refresh() for restoring menu, body and exit handler."
        Window.__ui_lock = False

    def ui_is_locked(self):
        "Chech if UI is locked or not, return True or False"
        return Window.__ui_lock

class Application(Window):
    """ This class represents the running application itself
        and it is responsible for handling the termination semaphore.
        Only one Application class must be instantiated per application.
    """
    __highlander = None
    __lock = None
    
    def __init__(self, title, body, menu = None, exit_handler = None):
        """ Only one application is allowed. It is resposible for starting
            and finishing the program.
            run() is overrided for controling this behavior.
        """
        if Application.__highlander:
            raise "Only one Application() allowed"
        Application.__highlander = self

        if not Application.__lock:
            Application.__lock = e32.Ao_lock()

        Window.__init__(self, title, body, menu, exit_handler)

    def close_app(self):
        """ Signalize the application lock, allowing run() to terminate the application.
        """
        Application.__lock.signal()
            
    def run(self):
        """ Show the the application and wait until application lock is
            signalized. After that, make all necessary cleanup.
        """
        old_title = app.title
        self.refresh()        
        Application.__lock.wait()
        # restore everything !
        app.set_tabs( [], None )
        app.title = old_title
        app.menu = []
        app.body = None
        #app.set_exit()        

class Dialog(Window):
    """ This class is in the charge of showing/hiding dialogs when necessary.
        Many dialogs are allowed, each one with their own set of body+menu+exit
        handler.
    """
    def __init__(self, cbk, title, body, menu = None, exit_handler = None):
        """ Create a dialog. cbk is called when dialog is closing.
            Dialog contents, like title and body need
            to be specified. If menu or exit_handler are not specified,
            defautl values for dialog class are used. 
        """
        self.cbk = cbk
        self.cancel = False
        Window.__init__(self, title, body, menu, exit_handler)

    def close_app(self):
        """ When closing the dialog, a call do self.cbk() is done.
            If this function returns True the dialog is not refreshed
            and the latest dialog/window takes control. If something fails
            during calback execution, callback function should return False
            and does not call refresh(). Using self.cancel it is possible
            to determine when the dialog  was canceled or not. 
        """
        if self.cbk() == False:
            self.refresh()

    def cancel_app(self):
        """ Close the dialog but turn the cancel flag on.
        """
        self.cancel = True
        self.close_app()
