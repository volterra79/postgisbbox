"""
/***************************************************************************
 PostgisBBoxDialog
                                 A QGIS plugin
 Load a BBO from postgis layers
                             -------------------
        begin                : 2011-10-02
        copyright            : (C) 2011 by Francesco Boccacci
        email                : francescoboccacci@libero.it
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt4 import QtCore, QtGui
from ui_postgisbbox import Ui_PostgisBBox
from qgis.core import *
from qgis.gui import *

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
import postgis_utils
from ui_postgisbbox import Ui_PostgisBBox

# create the dialog for zoom to point
class PostgisBBoxDialog(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        # Set up the user interface from Designer.
        self.ui = Ui_PostgisBBox()
        self.ui.setupUi(self)
        
