# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PartirUsoSuelo
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
from qgis.core import *
from qgis.utils import *
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt
from PyQt4.QtGui import QAction, QIcon, QDockWidget, QLabel, QGridLayout, QWidget
import processing

# import sys
# sys.path.append('C:/dependencias-propias/pycharm-debug.egg')
import pydevd
pydevd.settrace('localhost', port=62117, suspend=False)

# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from PartirUsoSuelo_dialog import PartirUsoSueloDialog
from PartirUsoSuelo_dockwidget import PartirUsoSueloDockWidget
import os.path


class PartirUsoSuelo:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'PartirUsoSuelo_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference

        """ Creamos el dialogo """
        #self.dlg = PartirUsoSueloDialog()

        """ Creamos el DockWidget (le asignamos tambien al nombre dlg para no tener que modificar el codigo)"""
        self.dockWidget = PartirUsoSueloDockWidget()
        self.dlg = self.dockWidget

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&PartirUsoSuelo')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'PartirUsoSuelo')
        self.toolbar.setObjectName(u'PartirUsoSuelo')

        """ Estas linias solo lo tiene el dialogo, el dock no """
        # self.dlg.lineEdit.clear()
        # self.dlg.pushButton.clicked.connect(self.abrire_archivo)

        self.dlg.comboBox.currentIndexChanged.connect(self.habilitar_edicion)
        self.dlg.comboBox_2.currentIndexChanged.connect(self.habilitar_edicion)
        self.dlg.pushButton_iniciar.clicked.connect(self.iniciar_edicion)
        self.dlg.pushButton_finalizar.clicked.connect(self.finalizar_edicion)

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('PartirUsoSuelo', message)

    def add_action(
            self,
            icon_path,
            text,
            callback,
            enabled_flag=True,
            add_to_menu=True,
            add_to_toolbar=True,
            status_tip=None,
            whats_this=None,
            parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/PartirUsoSuelo/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Partir Uso Suelo'),
            callback=self.run,
            parent=self.iface.mainWindow())

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr(u'&PartirUsoSuelo'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def habilitar_edicion(self):

        # Guardamos la capa seleccionada
        indiceLayerCortarSeleccionada = self.dlg.comboBox.currentIndex()
        indiceLayerProcesarSeleccionada = self.dlg.comboBox_2.currentIndex()
        layers = self.iface.legendInterface().layers()
        layerCortarSeleccionada = layers[indiceLayerCortarSeleccionada]
        layerProcesarSeleccionada = layers[indiceLayerProcesarSeleccionada]
        self.vlayer = layerCortarSeleccionada
        self.vlayerProcesar = layerProcesarSeleccionada

        # Habilitamos la edicion
        self.dlg.pushButton_iniciar.setEnabled(True)

    def iniciar_edicion(self):
        self.iface.setActiveLayer(self.vlayer)
        self.listado_features_modificadas = []
        self.listado_features_nuevas = []
        self.connect_signals()
        self.vlayer.startEditing()
        self.iface.actionSplitFeatures().trigger()
        self.dlg.pushButton_iniciar.setEnabled(False)
        self.dlg.pushButton_finalizar.setEnabled(True)

    def finalizar_edicion(self):
        self.vlayer.commitChanges()
        self.dlg.pushButton_iniciar.setEnabled(True)
        self.dlg.pushButton_finalizar.setEnabled(False)

        # Obtenemos la lista de campos
        inFields = self.vlayer.dataProvider().fields()

        # Convert its geometry type enum to a string we can pass to
        # QgsVectorLayer's constructor
        inLayerGeometryType = ['Point', 'Line', 'Polygon'][self.vlayer.geometryType()]

        # Convert its CRS to a string we can pass to QgsVectorLayer's constructor
        inLayerCRS = self.vlayer.crs().authid()

        self.listado_features_final = []

        for feature in self.listado_features_nuevas:

            # Make the output layer
            outLayer = QgsVectorLayer(inLayerGeometryType + '?crs=' + inLayerCRS, \
                                      u'parcela_nueva_id_' + str(feature.id()), \
                                      'memory')

            # changes are only possible when editing the layer
            outLayer.startEditing()
            outLayer.dataProvider().addAttributes(inFields.toList())
            outLayer.dataProvider().addFeatures([feature])
            # outLayer.addFeature(feature, True)

            # commit to stop editing the layer
            outLayer.commitChanges()

            # update layer's extent when new features have been added
            # because change of extent in provider is not propagated to the layer
            outLayer.updateExtents()

            # Add it to the map
            QgsMapLayerRegistry.instance().addMapLayer(outLayer)

            # Realizamos la intersección de la feautre nueva con la capa que se quiere procesar
            # interseccion = processing.runalg("qgis:intersection", self.vlayerProcesar, outLayer, None)
            nombre_interseccion = "interseccion_parcela_" + str(feature.id())
            interseccion = processing.runalg("qgis:intersection", self.vlayerProcesar, outLayer,
                                             "C:\\Temp\\" + nombre_interseccion + ".shp")
            # self.iface.addVectorLayer(interseccion.get("OUTPUT"), nombre_interseccion, "ogr")
            # intersectionLayer = QgsMapLayerRegistry.instance().mapLayersByName(nombre_interseccion)[0]
            layer_intersect = QgsVectorLayer(interseccion.get("OUTPUT"), nombre_interseccion, "ogr")
            layer_intersect.startEditing()

            for feature_intersect in layer_intersect.getFeatures():
                feature_intersect['id_parcela'] = feature.id()
                layer_intersect.updateFeature(feature_intersect)

            layer_intersect.commitChanges()

            # Eliminamos los campos que sobran
            numero_campos_original = self.vlayerProcesar.dataProvider().fields().count()
            numero_campos_intersect = layer_intersect.dataProvider().fields().count()
            lista_ids_campos_eliminar = range(numero_campos_original, numero_campos_intersect)

            layer_intersect.dataProvider().deleteAttributes(lista_ids_campos_eliminar)
            layer_intersect.commitChanges()
            layer_intersect.updateExtents()

            # QgsMapLayerRegistry.instance().addMapLayer(layer_intersect)
            QgsMapLayerRegistry.instance().removeMapLayer(outLayer.id())

            # Añadimos la feature nueva al listado final
            self.listado_features_final.extend(layer_intersect.getFeatures())

        for feature in self.listado_features_modificadas:
            outLayer = QgsVectorLayer(inLayerGeometryType + '?crs=' + inLayerCRS, \
                                      u'parcela_modificada_id_' + str(feature.id()), \
                                      'memory')

            # changes are only possible when editing the layer
            outLayer.startEditing()
            outLayer.dataProvider().addAttributes(inFields.toList())
            outLayer.dataProvider().addFeatures([feature])

            outLayer.commitChanges()
            outLayer.updateExtents()

            QgsMapLayerRegistry.instance().addMapLayer(outLayer)

            nombre_interseccion = "interseccion_parcela_" + str(feature.id())
            interseccion = processing.runalg("qgis:intersection", self.vlayerProcesar, outLayer,
                                             "C:\\Temp\\" + nombre_interseccion + ".shp")
            layer_intersect = QgsVectorLayer(interseccion.get("OUTPUT"), nombre_interseccion, "ogr")

            layer_intersect.startEditing()

            # Eliminamos los campos que sobran
            numero_campos_original = self.vlayerProcesar.dataProvider().fields().count()
            numero_campos_intersect = layer_intersect.dataProvider().fields().count()
            lista_ids_campos_eliminar = range(numero_campos_original, numero_campos_intersect)

            layer_intersect.dataProvider().deleteAttributes(lista_ids_campos_eliminar)
            layer_intersect.commitChanges()
            layer_intersect.updateExtents()

            # QgsMapLayerRegistry.instance().addMapLayer(layer_intersect)
            QgsMapLayerRegistry.instance().removeMapLayer(outLayer.id())

            # Añadimos la feature modificada al listado final
            self.listado_features_final.extend(layer_intersect.getFeatures())

        # Unimos las intersecciones
        nombre_layer_final = self.vlayerProcesar.name() + "_procesado"
        layerFinal = QgsVectorLayer(inLayerGeometryType + '?crs=' + inLayerCRS, \
                                    nombre_layer_final, \
                                    'memory')

        # Obtenemos la lista de campos
        campos = self.vlayerProcesar.dataProvider().fields()

        layerFinal.startEditing()
        layerFinal.dataProvider().addAttributes(campos.toList())
        layerFinal.dataProvider().addFeatures(self.listado_features_final)

        layerFinal.commitChanges()
        layerFinal.updateExtents()

        QgsMapLayerRegistry.instance().addMapLayer(layerFinal)

    def abrire_archivo(self):
        hola = "Hola Mundo!"
        self.dlg.lineEdit.setText(hola)
        # layers = self.iface.legendInterface().layers()
        # layer_list = []
        # for layer in layers:
        #     layer_list.append(layer.name())
        #     iter = layer.getFeatures()
        #     for feature in iter:
        #         geom = feature.geometry()
        #         print "Feature ID %d: " % feature.id()

        # layer = self.iface.activeLayer()
        # if layer != None:
        #     self.vlayer = layer
        #     self.connect_signals()
        #     iter = layer.getFeatures()
        #     for feature in iter:
        #         # retrieve every feature with its geometry and attributes
        #         # fetch geometry
        #         geom = feature.geometry()
        #         print "Feature ID %d: " % feature.id()
        #         print "Area:", geom.area()
        #         print "Perimeter:", geom.length()
        #
        #         # show some information about the feature
        #         if geom.type() == QGis.Point:
        #             x = geom.asPoint()
        #             print "Point: " + str(x)
        #         elif geom.type() == QGis.Line:
        #             x = geom.asPolyline()
        #             print "Line: %d points" % len(x)
        #         elif geom.type() == QGis.Polygon:
        #             x = geom.asPolygon()
        #             numPts = 0
        #             for ring in x:
        #                 numPts += len(ring)
        #             print "Polygon: %d rings with %d points" % (len(x), numPts)
        #         else:
        #             print "Unknown"
        #
        #         # fetch attributes
        #         attrs = feature.attributes()
        #
        # else:
        #     self.dlg.lineEdit.setText("Seleccione una capa para editarla")

    def connect_signals(self):
        self.vlayer.editingStarted.connect(self.editing_started)
        self.vlayer.editingStopped.connect(self.editing_stopped)

    def editing_started(self):
        # # Disable attributes dialog
        # QSettings().setValue(
        #     '/qgis/digitizing/disable_enter_attribute_values_dialog', True)
        self.edit_handler = EditHandler(self.vlayer)

    def editing_stopped(self):
        print('Editing stopped')
        self.listado_features_modificadas = self.edit_handler.get_listado_features_modificadas()
        self.listado_features_nuevas = self.edit_handler.get_listado_features_nuevas()
        self.edit_handler.disconnect_committed_signals()
        self.edit_handler = None

    def clean_up(self):
        QgsMapLayerRegistry.instance().removeMapLayer(self.vlayer.id())
        self.iface.mapCanvas().clearCache()
        self.iface.mapCanvas().refresh()

    def crear_widget(self):
        self._widget_demo = QWidget()
        vbox = QGridLayout(self._foglioNotInLavWidget)
        styleSheet = "QLabel{font: bold italic 'DejaVu Sans'; font:14pt; color: darkGray}"
        self._foglioNotInLavWidget.setStyleSheet(styleSheet)
        self.lblFoglioNotInLav1 = QLabel("Selecciona la capa que quieres cortar", self._foglioNotInLavWidget)
        self.lblFoglioNotInLav2 = QLabel("Selecciona la capa que quieres que se actualice", self._foglioNotInLavWidget)
        vbox.addWidget(self.lblFoglioNotInLav1, 0, 0, Qt.AlignCenter)
        vbox.addWidget(self.lblFoglioNotInLav2, 1, 0, Qt.AlignCenter)
        vbox.addWidget(self.btnApriFoglio, 2, 0, Qt.AlignCenter)
        vbox.addWidget(self.btnCercaFoglio, 3, 0, Qt.AlignCenter)

    def crear_dockwidget(self):
        self.crear_widget()
        nombre = "Widget de prueba"
        self.dockWidget = QDockWidget(nombre)
        self.dockWidget.setObjectName(nombre)
        self.dockWidget.setWidget(self._widget_demo)

        self.iface().removeDockWidget(self.dockWidget)
        self.iface().mainWindow().addDockWidget(Qt.LeftDockWidgetArea, self.dockWidget)
        self.dockWidget.show()

    def run(self):
        """Run method that performs all the real work"""
        # lista_algoritmos = processing.alglist()
        # opciones_interseccion = processing.alghelp("qgis:intersection")

        """ Cargamos el listado de capas en los combobox """
        layers = self.iface.legendInterface().layers()
        layer_list = []
        for layer in layers:
            layer_list.append(layer.name())

        self.dlg.comboBox.addItems(layer_list)
        self.dlg.comboBox_2.addItems(layer_list)

        """ Mostramos el dockWidget """
        self.iface.mainWindow().addDockWidget(Qt.LeftDockWidgetArea, self.dockWidget)
        self.dockWidget.show()

        """ Mostramos el dialogo """
        # self.dlg.show()
        # # Run the dialog event loop
        # result = self.dlg.exec_()
        # # See if OK was pressed
        # if result:
        #     # Do something useful here - delete the line containing pass and
        #     # substitute with your code.
        #     pass


class EditHandler(object):
    """
    Listens for committed feature additions and changes feature attributes.
    """

    def __init__(self, vlayer):
        self.vlayer = vlayer
        self.listado_features_modificadas = []
        self.listado_features_nuevas = []
        self.connect_committed_signals()

    def connect_committed_signals(self):
        self.vlayer.committedFeaturesAdded.connect(self.committed_adds)
        self.vlayer.geometryChanged.connect(self.geometry_changed)

    def disconnect_committed_signals(self):
        self.vlayer.committedFeaturesAdded.disconnect()
        self.vlayer.geometryChanged.disconnect()

    def committed_adds(self, layer_id, added_features):
        self.listado_features_nuevas = added_features

    # Listener cuando cambia una geometria, devuelve la geometria cambiada, con los nuevos valores
    def geometry_changed(self, feature_id, geometry):
        feature = self.vlayer.getFeatures(QgsFeatureRequest().setFilterFid(feature_id)).next()
        self.listado_features_modificadas.append(feature)

        # geometry = feature.geometry()
        #
        # # Create new feature
        # new_feature = QgsFeature(self.vlayer.pendingFields())
        # geometry.translate(0, 50)  # Modify original geometry
        # new_feature.setGeometry(geometry)
        # new_feature.setAttribute('symbol', 10)  # Customise attributes
        #
        # # Update layer by removing old and adding new
        # result = self.vlayer.dataProvider().deleteFeatures([feature_id])
        # result, new_features = self.vlayer.dataProvider().addFeatures([new_feature])

    def get_listado_features_modificadas(self):
        return self.listado_features_modificadas

    def get_listado_features_nuevas(self):
        return self.listado_features_nuevas
