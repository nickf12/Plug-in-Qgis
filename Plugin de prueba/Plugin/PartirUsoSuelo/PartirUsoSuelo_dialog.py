# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PartirUsoSueloDialog
                                 A QGIS plugin
 PartirUsoSuelo
                             -------------------
        begin                : 2016-06-17
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Telespazio
        email                : jbarcelo@Telespazio.es
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

import os

from PyQt4 import QtGui, uic

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'PartirUsoSuelo_dialog_base.ui'))


class PartirUsoSueloDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(PartirUsoSueloDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
