import os
import sys
import e32

sys.stderr = open("E:\\temp\\verboerr.txt", "w")

PACKAGE_LOC = "E:\\Data\\python"
if PACKAGE_LOC not in sys.path:
    sys.path.append(PACKAGE_LOC)

#try:
from verbo import verboapp
verboapp.VerboApp().run()

sys.stderr.close()
sys.stderr = sys.__stderr__
# except Exception, e:
#     #import appuifw
#     #appuifw.note(u"Exception: %s" % (e))
#     print e
