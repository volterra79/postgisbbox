"""
/***************************************************************************
 PostgisBBox
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
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *
#from mymap import MyWnd
from qgis.gui import *
from PyQt4.QtGui import QAction, QMainWindow
from PyQt4.QtCore import SIGNAL, Qt, QString
from qgis.core import *
import os, sys, math
from urllib2 import urlopen
import xml.etree.ElementTree as ET, re, decimal
#from xml.etree.ElementTree import ElementTree





# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from postgisbboxdialog import PostgisBBoxDialog
import postgis_utils
from ui_postgisbbox import Ui_PostgisBBox


class PostgisBBox (QDialog, Ui_PostgisBBox):

    def __init__(self, iface):
        
        QDialog.__init__(self)
        #QMessageBox.information( self.iface.mainWindow(),"Info", "Main" ) 
        # Set up the user interface from Designer.
        self.ui = Ui_PostgisBBox()
        self.ui.setupUi(self)
        #QObject.connect(self.ui.ConnectToPostgis, SIGNAL("clicked()"), self.salutare)
        #database = self.listDatabases()
        #datbasestring=''
        #for i in database:
                #QMessageBox.information( self.iface.mainWindow(),"Info", i )
                #databasestring +=i
        #        self.ui.ConnessioniPostgis.addItem(i)
        # Save reference to the QGIS interface
        self.iface = iface
        self.canvas = self.iface.mapCanvas() #CHANGE
        # this QGIS tool emits as QgsPoint after each click on the map canvas
        #self.clickTool = QgsMapToolEmitPoint(self.canvas)
        self.db = None
        
        #self.ConnessioniPostgis.clear()
        #self.database = self.listDatabases()
        #datbasestring=''
       
            #QMessageBox.information( self.iface.mainWindow(),"Info",collegamento)
        
        #QMessageBox.information( self.iface.mainWindow(),"Info", str(self.ConnessioniPostgis.count()))
        #QObject.connect(self.ConnessioniPostgis, SIGNAL("currentIndexChanged(QString)"), self.update)
        
        #QMessageBox.information( self.iface.mainWindow(),"Info", str(self.ConnessioniPostgis.count()))
    
        


    def initGui(self):
        # Create action that will start plugin configuration
        QDialog.__init__(self)
        #self.iface = iface
        self.setupUi(self)
        # Set up the user interface from Designer.
        #self.ui = Ui_PostgisBBox()
        #self.ui.setupUi(self)
        
        self.action = QAction(QIcon(":/plugins/PostgisBBox/postgis_select.png"), \
            "PostgisBBOX", self.iface.mainWindow())
        # connect the action to the run method
        QObject.connect(self.action, SIGNAL("triggered()"), self.run)
        #QObject.connect(self.ConnectToPostgis, SIGNAL("clicked()"), self.salutare)
        

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("&PostgisBBOX", self.action)
        
        #self.statusBar = QStatusBar(self)
        #self.setStatusBar(self.statusBar)
        #result = QObject.connect(self.clickTool, SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), self.handleMouseDown)
        #QMessageBox.information( self.iface.mainWindow(),"Info", "connect = %s"%str(result) )
    
    
    def updateListDatabase(self):    
        database = self.listDatabases()
        #datbasestring=''
        for i in database:
                #QMessageBox.information( self.iface.mainWindow(),"Info", i )
                #databasestring +=i
                self.ConnessioniPostgis.addItem(i)
                #self.BBoxBottom.insert(i)
                #self.ConnessioniPostgis.insertItems(i)
                #self.listView.setText(i)
        #self.ConnessioniPostgis.view()
    #def handleMouseDown(self, point, button):
        #QMessageBox.information( self.iface.mainWindow(),"Info", "X,Y = %s,%s" % (str(point.x()),str(point.y())) )
#

    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu("&PostgisBBOX",self.action)
        self.iface.removeToolBarIcon(self.action)
    
    def listDatabases(self):
        
        #self.ui.setupUi(self)
        self.actionsDb = {}
        settings = QSettings()
        settings.beginGroup("/PostgreSQL/connections")
        keys = settings.childGroups()
        #QMessageBox.information( self.iface.mainWindow(),"Info", unicode(keys) ) 
        
        for key in keys:
            self.actionsDb[unicode(key)] = key
            
        settings.endGroup()
        
        return self.actionsDb

   
        
    def dbConnect(self):
      
        selected = self.dlg.ui.ConnessioniPostgis.currentText()
        self.currentindex = self.dlg.ui.ConnessioniPostgis.currentIndex()
        self.dlg.ui.comboBoxschema.clear()
        self.dlg.ui.comboBoxschema.addItem('All')
        
             
        
        
        settings = QSettings()
    
        # if there's open database already, get rid of it
        if self.db:
            self.dbDisconnect()
        
        # get connection details from QSettings
        settings.beginGroup( u"/PostgreSQL/connections/" + selected )
        if not settings.contains("database"): # non-existent entry?
            QMessageBox.critical(self, "Error", "Unable to connect: there is no defined database connection \"%s\"." % selected)
            return
        #else:
            #QMessageBox.information( self.iface.mainWindow(),"Prima", "Databse conesso a " + selected)
        get_value_str = lambda x: unicode(settings.value(x).toString())
        self.host, self.database, self.username, self.password = map(get_value_str, ["host", "database", "username", "password"])
        self.port = settings.value("port").toInt()[0]
        
        # qgis1.5 use 'savePassword' instead of 'save' setting
        if not ( settings.value("save").toBool() or settings.value("savePassword").toBool() ):
            (password, ok) = QInputDialog.getText(self, "Enter password", "Enter password for connection \"%s\":" % selected, QLineEdit.Password)
            if not ok: return
        settings.endGroup()
        
        #self.statusBar.showMessage("Connecting to database (%s) ..." % selected)
        QApplication.processEvents() # give the user chance to see the message :)
        
        # connect to DB
        try:
            self.db = postgis_utils.GeoDB(host=self.host, port=self.port, dbname=self.database, user=self.username, passwd=self.password)
            #QMessageBox.information( self.iface.mainWindow(),"Prima", "Databse conesso a " + selected)
            self.tables = self.db.list_geotables()
            self.n_tables = len(self.tables)
            t_n = 0
            #QMessageBox.information( self.iface.mainWindow(),"Prima", "Tabella " + str(n_tables))
            for t in self.tables :
                if str(t[7]) != "None" :        
                        t_n+=1
            self.n_tables = t_n
            self.dlg.ui.tableWidget.setRowCount(self.n_tables)
            #QMessageBox.information( self.iface.mainWindow(),"Prima", "Tabella " + str(n_tables))
            i = 0
            schemaold = ''
            try:
                _fromUtf8 = QString.fromUtf8
            except AttributeError:
                _fromUtf8 = lambda s: s
            for t in self.tables :
                
                #self.geo = t.check_geometry_columns_table()
                if str(t[7]) != "None" :
                        #self.tableWidget.insertRow(i)
                        tab = QTableWidgetItem(str(t[0]))
                        schema = QTableWidgetItem(str(t[1]))
                        geotype = QTableWidgetItem(str(t[7]))
                        #schemaold = ""
                        #type = QTableWidgetItem(str(t[7]))
                        self.dlg.ui.tableWidget.setItem(i,0,tab)
                        self.dlg.ui.tableWidget.setItem(i,1,schema)
                        if str(t[7]) == 'POINT':
                            PointItem= QTableWidgetItem()
                            PointItem.setText(str(t[7]))
                            layerPointIcon = QIcon()
                            layerPointIcon.addPixmap(QPixmap(_fromUtf8(":/icons/layer_point.png")), QIcon.Normal, QIcon.Off)
                            PointItem.setIcon(layerPointIcon)
                            self.dlg.ui.tableWidget.setItem(i,2,PointItem)
                        elif str(t[7]) == 'LINESTRING' or str(t[7]) == 'MULTILINESTRING':     
                            LineItem= QTableWidgetItem()
                            LineItem.setText(str(t[7]))
                            layerLineIcon = QIcon()
                            layerLineIcon.addPixmap(QPixmap(_fromUtf8(":/icons/layer_line.png")), QIcon.Normal, QIcon.Off)
                            LineItem.setIcon(layerLineIcon)
                            self.dlg.ui.tableWidget.setItem(i,2,LineItem)
                        elif str(t[7]) == 'POLYGON' or  str(t[7]) == 'MULTIPOLYGON' :    
                            PolyItem= QTableWidgetItem()
                            PolyItem.setText(str(t[7]))
                            layerPolyIcon = QIcon()
                            layerPolyIcon.addPixmap(QPixmap(_fromUtf8(":/icons/layer_polygon.png")), QIcon.Normal, QIcon.Off)
                            PolyItem.setIcon(layerPolyIcon)
                            self.dlg.ui.tableWidget.setItem(i,2,PolyItem)
                        else:
                            UnkItem= QTableWidgetItem()
                            UnkItem.setText('Unknow')
                            layerUnkIcon = QIcon()
                            layerUnkIcon.addPixmap(QPixmap(_fromUtf8(":/icons/layer_unknow.png")), QIcon.Normal, QIcon.Off)
                            UnkItem.setIcon(layerUnkIcon)
                            self.dlg.ui.tableWidget.setItem(i,2,UnkItem)   
                        if schemaold != str(t[1]):
                            self.dlg.ui.comboBoxschema.addItem(str(t[1]))
                            schemaold = str(t[1])
                        
                       
                        i+=1
            
            
                        #QMessageBox.information( self.iface.mainWindow(),"Prima", "Tabella " + str(t[7]))
            #QMessageBox.information( self.iface.mainWindow(),"Prima", "Tabella " + str(self.ui.tableWidget.rowCount()))             
        except postgis_utils.DbError, e:
            #self.statusBar.clearMessage()
            QMessageBox.critical(self, "error", "Couldn't connect to database:\n"+e.msg)
            return
        self.writeLastConnection(selected)
       
    def dbDisconnect(self):
        
        # uncheck previously selected DB
        """
        for a in self.actionsDb.itervalues():
            if a.isChecked():
                a.setChecked(False)
        
        self.db = None
        self.txtMetadata.setDatabase(None)
        self.refreshTable()
        
        self.actionDbDisconnect.setEnabled(False)
        """
        #self.enableGui(False)
        
        #self.currentView = ManagerWindow.ViewNothing
        #self.updateView()

        #self.updateWindowTitle()
        
    def addLayers (self):
        
            
        
            selTable = self.dlg.ui.tableWidget.selectedItems()
        #QMessageBox.information( self.iface.mainWindow(),"Lunghezza", str(len(selTable)) )
            self.lt = len(selTable) 
        #QMessageBox.information( self.iface.mainWindow(),"Lunghezza", str(l) )
        
        
        
            i=0
            for l in selTable:  
                for t in self.tables:
                    if str(t[0]) == selTable[i].text():   
                        uri = QgsDataSourceURI()
                        
                #uri.setConnection("localhost", "5432", "test_postgis", "postgres", "postgres")
                        uri.setConnection(str(self.host), str(self.port), str(self.database), str(self.username), str(self.password))
                        #QMessageBox.information( self.iface.mainWindow(),"Lunghezza", "Prima" )
                        uri.setDataSource(str(t[1]),  selTable[i].text(), str(t[6]))
                        layer = QgsVectorLayer(uri.uri(), selTable[i].text(), "postgres")
                        
                        
                        #QMessageBox.information( self.iface.mainWindow(),"Mappa", str(self.epgslayermap) )
                        #QMessageBox.information( self.iface.mainWindow(),"Tabella", str(layer.crs().epsg() ))
        
                        crsStart = QgsCoordinateReferenceSystem()
                        crsStart.createFromProj4(self.proj4layermap)
                        crsDest = QgsCoordinateReferenceSystem()  
                        crsDest.createFromProj4(layer.crs().toProj4())
                        #if self.epgslayermap != layer.crs().epsg():
                        
                        if crsStart != crsDest:
                            
                            #QMessageBox.information( self.iface.mainWindow(),"Mappa", str(self.w.xmin()) )
                            uri.setDataSource(str(t[1]),  selTable[i].text(), str(t[6]))
                        
                            bbox = QgsRectangle()
                            bbox.setXMinimum(self.dlg.ui.widget.extent().xMinimum())
                            bbox.setXMaximum(self.dlg.ui.widget.extent().xMaximum())
                            bbox.setYMinimum(self.dlg.ui.widget.extent().yMinimum())
                            bbox.setYMaximum(self.dlg.ui.widget.extent().yMaximum())
                            
                            
                            bboxNew = QgsCoordinateTransform(crsStart,crsDest).transformBoundingBox(bbox)
                            #QMessageBox.information( self.iface.mainWindow(),"Tabella", str(bboxNew.xMinimum()) )
                            #QMessageBox.information( self.iface.mainWindow(),"Mappa", str(bboxNew.xMinimum()) )
        
                            #sql = "the_geom && setsrid('BOX3D(" + left+ " " + bottom + " , " + right + " " + top + ")'::box3d,-1)"
                            sql = str(t[6]) + " && setsrid('BOX3D(" + str(bboxNew.xMinimum()) + " " + str(bboxNew.yMinimum()) + " , " + str(bboxNew.xMaximum()) + " " + str(bboxNew.yMaximum()) + ")'::box3d, " + str(layer.crs().epsg()) + ")"
                        
                            uri.setDataSource(str(t[1]),  selTable[i].text(), str(t[6]), sql)
                            #QMessageBox.information( self.iface.mainWindow(),"Mappa", "Diversi3" )
                            #QMessageBox.information( self.iface.mainWindow(),"Mappa", str(uri.uri()) )
                            self.iface.addVectorLayer(uri.uri(), selTable[i].text(), "postgres")
                            self.start = 0
                            
                            #QMessageBox.information( self.iface.mainWindow(),"Mappa", "Diversi5" )
                            
                        else:
                            
                            #QMessageBox.information( self.iface.mainWindow(),"Mappa", "Uguali" )
                            uri.setDataSource(str(t[1]),  selTable[i].text(), str(t[6]))
                                                    
        
                            #sql = "the_geom && setsrid('BOX3D(" + left+ " " + bottom + " , " + right + " " + top + ")'::box3d,-1)"
                            sql = str(t[6]) + " && setsrid('BOX3D(" + str(self.dlg.ui.widget.extent().xMinimum()) + " " + str(self.dlg.ui.widget.extent().yMinimum()) + " , " + str(self.dlg.ui.widget.extent().xMaximum()) + " " + str(self.dlg.ui.widget.extent().yMaximum()) + ")'::box3d," + str(layer.crs().epsg()) + ")"
                        
                            uri.setDataSource(str(t[1]),  selTable[i].text(), str(t[6]), sql)
                            self.iface.addVectorLayer(uri.uri(), selTable[i].text(), "postgres")
                            self.start = 0
                            #self.iface.zoomActiveLayer()
                            
                           
                                
                i+=1 
                #self.iface.zoomActiveLayer()
                self.writeLastBBox(str(self.dlg.ui.widget.extent().xMinimum()),str(self.dlg.ui.widget.extent().yMinimum()), str(self.dlg.ui.widget.extent().xMaximum()), str(self.dlg.ui.widget.extent().yMaximum()))
                self.view = 1
      
    
        
    def showMap(self):
        
        #self.start = 0
        try:
                #QMessageBox.information( self.iface.mainWindow(),"Prima", "Provo a leggere layer")
                self.layervector = self.iface.activeLayer()
                
                crsStart = QgsCoordinateReferenceSystem()
                crsStart.createFromProj4(self.layervector.crs().toProj4())
                crsDest = QgsCoordinateReferenceSystem()  
                crsDest.createFromProj4(self.layer.crs().toProj4())
                #QMessageBox.information( self.iface.mainWindow(),"Mappa", str(crsStart) )
                
                #QMessageBox.information( self.iface.mainWindow(),"Start", str(self.start))
                if crsStart != crsDest:
                    bbox = self.layervector.extent()    
                    bboxNew = QgsCoordinateTransform(crsStart,crsDest).transformBoundingBox(bbox)
                    
                    if self.start == 0:
                        self.start = 1
                    
                    #QMessageBox.information( self.iface.mainWindow(),"Start Trasform", str(self.start))
                    if self.start == 1 and self.layervector.featureCount() != 0:
                        #QMessageBox.information( self.iface.mainWindow(),"Start Trasform","bboxNew")
                        self.start=2
                        return bboxNew 
                    else:
                        #QMessageBox.information( self.iface.mainWindow(),"Start Trasform","bboxMap")
                        return self.BBOXMap()
                else:
                    
                    self.start=1
                    if self.start == 1 and self.layervector.featureCount() != 0:
                        #QMessageBox.information( self.iface.mainWindow(),"No Trasform", "Layer")
                        self.start=2
                        return self.layervector.extent()
                    else:
                        #QMessageBox.information( self.iface.mainWindow(),"Trasform","bboxMap")
                        return self.BBOXMap()
                
                
                
        except:   
            #QMessageBox.information( self.iface.mainWindow(),"Prima", "NO Layer attivo , Leggo BBox ultimo")
            return self.BBOXMap()
            
            
    def BBOXMap(self): 
        
        
        readBB = open(self.currentPath  + "/BBox.txt","r") 
                        
                        
        ex = QgsRectangle()
        #ex.setXMinimum("%.2f" % float(readBB.readline()))
        #ex.setYMinimum("%.2f" % float(readBB.readline()))
        #ex.setXMaximum("%.2f" % float(readBB.readline()))
        #ex.setYMaximum("%.2f" % float(readBB.readline()))
        xmin = float("%.2f" % float(readBB.readline()))
        ymin = float("%.2f" % float(readBB.readline()))
        xmax = float("%.2f" % float(readBB.readline()))
        ymax = float("%.2f" % float(readBB.readline()))
        #QMessageBox.information( self.iface.mainWindow(),"Prima", str(xmin))
        
        ex.setXMinimum(xmin)
        ex.setYMinimum(ymin)
        ex.setXMaximum(xmax)
        ex.setYMaximum(ymax)
        readBB.close()
                
        #self.start = 1
        return ex
                
                
        
            
        
        #self.w.show()
        
    def writeLastBBox(self,xmin,ymin,xmax,ymax):
        
        
        self.writeBB = open(self.currentPath + "/BBox.txt","w") 
        self.writeBB.write(xmin + "\n" + ymin + "\n" + xmax + "\n" + ymax)
             
        self.writeBB.close()
                
    def writeLastConnection(self,LastConnection):
        
       self.writeCon = open(self.currentPath  + "/Connection.txt","w") 
       self.writeCon.write(LastConnection)
             
       self.writeCon.close()            
        
    def ChangeExt(self):
        
        
        #QMessageBox.information( self.iface.mainWindow(),"Prima", "Cambiato")

            
    
        self.dlg.ui.BBoxTop.setText(str(self.w.ymax()))
        
        self.dlg.ui.BBoxBottom.setText(str(self.w.ymin()))
        
        self.dlg.ui.BBoxRight.setText(str(self.w.xmax()))
        
        self.dlg.ui.BBoxLeft.setText(str(self.w.xmin()))
    
    
    def outProjFile(self):
        
        format = QString( "<h2>%1</h2>%2 <br/> %3" )
        header = QString( "Define layer CRS:" )
        sentence1 = self.tr( "Please select the projection system that defines the current layer." )
        sentence2 = self.tr( "Layer CRS information will be updated to the selected CRS." )
        self.projSelect = QgsGenericProjectionSelector(self, Qt.Widget)
        self.projSelect.setMessage( format.arg( header ).arg( sentence1 ).arg( sentence2 ))
        if self.projSelect.exec_():
            self.projString = self.projSelect.selectedProj4String()
            self.epsgString = str(self.projSelect.selectedEpsg())
            
            if self.projString == "":
                QMessageBox.information(self, self.tr("Export to new projection"), self.tr("No Valid CRS selected"))
                return
            else:
                self.dlg.ui.txtProjection.clear()
                #self.dlg.ui.txtProjection.insert(self.projString)
                
                self.dlg.ui.txtProjection.insert("EPSG:" + self.epsgString)
                
                
                #QMessageBox.information( self.iface.mainWindow(),"Prima", projString)
        else:
            return
        
        
    
    def ShowMapCanvas (self):
        
        #QMessageBox.information( self.iface.mainWindow(),"HEIGHT", "Ciao")
        
        if self.dlg.ui.widget.extent().xMinimum() != 0:
            
            self.writeLastBBox(str(self.dlg.ui.widget.extent().xMinimum()),str(self.dlg.ui.widget.extent().yMinimum()), str(self.dlg.ui.widget.extent().xMaximum()), str(self.dlg.ui.widget.extent().yMaximum()))
        

      
        
        selectedMap = self.dlg.ui.SelectMapcomboBox.currentText()
        
        
        if selectedMap == "Google Street":
                self.layer = QgsRasterLayer(self.currentPath + "/googlemap.xml",'Google Map')
                        
        elif selectedMap == "OpenStreetMap":
                self.layer = QgsRasterLayer(self.currentPath+ "/osm.xml",'Osm')
                        
        elif selectedMap == "Google Satellite":
                self.layer = QgsRasterLayer(self.currentPath + "/googlesat.xml",'Google Satellite')
                        
        elif selectedMap == "Google Physical":
                self.layer = QgsRasterLayer(self.currentPath + "/googlephy.xml",'Google Physical')
        
        #QMessageBox.information( self.iface.mainWindow(),"HEIGHT", home)
        self.dlg.ui.widget.setCanvasColor(Qt.white)
        self.dlg.ui.widget.enableAntiAliasing(True)
        
        if not self.layer.isValid():
            raise IOError, "Failed to open the layer"
        self.dlg.ui.widget.refresh()
        QgsMapLayerRegistry.instance().addMapLayer(self.layer,False)
        
        ex = self.showMap()
        
        #QMessageBox.information( self.iface.mainWindow(),"HEIGHT", str(ex.xMinimum()))
        
        if (ex.xMinimum() == 0.0 and ex.xMaximum() == 0.0):
            
            
            self.dlg.ui.widget.setExtent(self.layer.extent())
        
        else:
            #QMessageBox.information( self.iface.mainWindow(),"Show map", str(self.showMap().xMinimum()))
            #QMessageBox.information( self.iface.mainWindow(),"BBOX", str(ex.xMinimum()))  
            #self.showMap()  
          
            self.dlg.ui.widget.setExtent(ex)
            
                #self.dlg.ui.widget.setExtent(self.BBOXMap())
        
        self.dlg.ui.widget.setLayerSet( [ QgsMapCanvasLayer(self.layer) ] )
        #self.setCentralWidget(self.dlg.ui.widget)
        #self.iface.setCentralWidget(self.dlg.ui.widget)
        
        
        
       
        actionZoomIn = QAction(QString("Zoom in"), self)
        actionZoomOut = QAction(QString("Zoom out"), self)
        actionPan = QAction(QString("Pan"), self)
        self.toolPan = QgsMapToolPan(self.dlg.ui.widget)
        self.toolPan.setAction(actionPan)
        self.toolZoomIn = QgsMapToolZoom(self.dlg.ui.widget, False) # false = in
        self.toolZoomIn.setAction(actionZoomIn)
        self.toolZoomOut = QgsMapToolZoom(self.dlg.ui.widget, True) # true = out
        self.toolZoomOut.setAction(actionZoomOut)
       
     
    
        self.pan()
        
      
        
        return self.layer
    
    def zoomIn(self):
    
        self.dlg.ui.widget.setMapTool(self.toolZoomIn)
        #self.dlg.ui.widget.refresh()
    

      
    def zoomOut(self):
        self.dlg.ui.widget.setMapTool(self.toolZoomOut)
        #self.dlg.ui.widget.refresh()
    

    def pan(self):
        self.dlg.ui.widget.setMapTool(self.toolPan)
        #self.dlg.ui.widget.refresh()
    
    def search(self):

        city = self.dlg.ui.SearchEdit.displayText()
        if city != '':
        
            #url = "http://www.geonames.org/search.html?q=" + str(city)
            url = "http://ws.geonames.org/search?q=" + str(city) + "&maxRows=10"
            #url = "http://ws.geonames.org/findNearbyPlaceName?lat="+str(lat)+"&lng="+str(long)+"&style=full"
            self.page = urlopen(url).read()
            
            self.dlg.ui.tableSearch.setRowCount(10)
            name=re.findall('(<'+'name'+'>.*</'+'name'+'>)',self.page)
            lat = re.findall('(<'+'lat'+'>.*</'+'lat'+'>)',self.page)
            lon = re.findall('(<'+'lng'+'>.*</'+'lng'+'>)',self.page)
            country = re.findall('(<'+'countryName'+'>.*</'+'countryName'+'>)',self.page)
            self.latlist= []
            self.longlist=[]
            i=0
            for n in name:
                
                na=n.split("<"+'name'+">")[1].split("</"+'name'+">")[0]
                #namelist.append(na)
                self.dlg.ui.tableSearch.setItem(i,0, QTableWidgetItem(na) )
                
                i+=1
            for la in lat:
                
                na=la.split("<"+'lat'+">")[1].split("</"+'lat'+">")[0]
                self.latlist.append(na)
                
                
            for lo in lon:
                
                na=lo.split("<"+'lng'+">")[1].split("</"+'lng'+">")[0]
                self.longlist.append(na)
                
                
            i=0    
            for co in country:
                
                na=co.split("<"+'countryName'+">")[1].split("</"+'countryName'+">")[0]
                self.dlg.ui.tableSearch.setItem(i,1, QTableWidgetItem(na) )
                i+=1
        else:
           
            QMessageBox.information( self.iface.mainWindow(),"Search", "Please enter a city")  
              
    def centerMap(self):
        
        
        selrow = self.dlg.ui.tableSearch.currentRow( )
        try: 
            latitude = self.latlist[selrow]
            longitude = self.longlist[selrow]
            latitude = float(latitude)
            longitude = float (longitude)
            start=QgsCoordinateReferenceSystem()
            start.createFromEpsg(4326)
            end=QgsCoordinateReferenceSystem()
            end.createFromEpsg(900913)
            #for i in ind:
            center = QgsPoint()
            center.setX(longitude)
            center.setY(latitude)
            
            newcenter = QgsCoordinateTransform(start,end).transform(center)
            
            self.writeLastBBox(str(newcenter.x() - 1800),str(newcenter.y() - 1800), str(newcenter.x() + 2100), str(newcenter.y() + 2100))
            self.dlg.ui.widget.setExtent(self.BBOXMap())
            self.dlg.ui.widget.refresh()
        except:
            QMessageBox.information( self.iface.mainWindow(),"Go","No row selected" )  
        
        #self.dlg.ui.widget.panActionEnd(newcenter)        
        #QMessageBox.information( self.iface.mainWindow(),"Prima",longitude )
        
    def FilterTable(self):
        
        selectedSchema = self.dlg.ui.comboBoxschema.currentText()
        
        
        rows = self.dlg.ui.tableWidget.rowCount()
       
        #QMessageBox.information( self.iface.mainWindow(),"Prima",str(rows) )       
        if selectedSchema == 'All':
            while rows != 0:
                self.dlg.ui.tableWidget.showRow(rows-1)
                #QMessageBox.information( self.iface.mainWindow(),"Ciclo",str(rows) )       
                rows-=1
        else:
            while rows!=0:
                #r = self.dlg.ui.tableWidget.cellWidget(1,5)
                r = self.dlg.ui.tableWidget.item(rows-1,1)
                #r1 = self.dlg.ui.tableWidget.cellWidget(0,0)
                r.text()
                #QMessageBox.information( self.iface.mainWindow(),"Nome schema",r.text())
                
                if r.text() != selectedSchema:
                    
                    self.dlg.ui.tableWidget.setRowHidden(rows-1,True) 
                else:
                    self.dlg.ui.tableWidget.showRow(rows-1)
                rows-=1    
            #self.dlg.ui.tableWidget.rowCount()
            
      
    # run method that performs all the real work
    def run(self):
        
        
        #self.first = 0
        #Check if psycopg2 python module is installed.This module is usefull 
        #to connect to Postgresql/Postgis database 
        self.currentPath = os.path.dirname( __file__ ).replace("\\", "/")
        self.start = 0
        try:
            import psycopg2
        except ImportError, e:
            QMessageBox.information(self.iface.mainWindow(), "hey", "Couldn't import Python module 'psycopg2' for communication with PostgreSQL database. Without it you won't be able to run PostGIS manager.")
            return
        #self.listDatabases()
        
        #self.dbConnectInit("Local")
        
        # create and show the dialog
        self.dlg = PostgisBBoxDialog()
        
        
        
        
        
        self.actionsDb = {}
        settings = QSettings()
        settings.beginGroup("/PostgreSQL/connections")
        keys = settings.childGroups()
        
        for key in keys:
            self.actionsDb[unicode(key)] = key
            self.dlg.ui.ConnessioniPostgis.addItem(key)
            
        settings.endGroup()
       
        #QObject.connect(self.dlg.ui.ConnectToPostgis, SIGNAL("clicked()"), self.salutare)
        QObject.connect(self.dlg.ui.ConnectToPostgis, SIGNAL("clicked()"), self.dbConnect)
        QObject.connect(self.dlg.ui.SelectMapcomboBox, SIGNAL("currentIndexChanged(QString)"), self.ShowMapCanvas)
        QObject.connect(self.dlg.ui.ZoomIn, SIGNAL("clicked()"), self.zoomIn)
        QObject.connect(self.dlg.ui.ZoomOut, SIGNAL("clicked()"), self.zoomOut)
        QObject.connect(self.dlg.ui.Pan, SIGNAL("clicked()"), self.pan)
        QObject.connect(self.dlg.ui.SearchButton, SIGNAL("clicked()"), self.search)
        QObject.connect(self.dlg.ui.goMap, SIGNAL("clicked()"), self.centerMap)
        QObject.connect(self.dlg.ui.comboBoxschema, SIGNAL("currentIndexChanged(QString)"), self.FilterTable)
        
        #QObject.connect(self.dlg.ui.BBoxButton, SIGNAL("clicked()"), self.showMap)
        
        
        try :
            if self.view == 1:
                self.dlg.ui.ConnessioniPostgis.setCurrentIndex(self.currentindex)
                self.dbConnect()
        except:
            pass
        
        
            
        #self.epgslayermap = self.layer.crs().epsg()
        self.proj4layermap = self.ShowMapCanvas().crs().toProj4()
        #QMessageBox.information( self.iface.mainWindow(),"Prima", str(self.ConnessioniPostgis.count()))
        
               
        self.dlg.show()
      
        result = self.dlg.exec_()
        
        
     
            
        
            # See if OK was pressed
        if result == 1:
                
                #self.ChangeExt()
                #self.first = 0
                self.addLayers()
                
                #self.iface.zoomActiveLayer()
                #self.writeLastBBox(str(self.dlg.ui.widget.extent().xMinimum()),str(self.dlg.ui.widget.extent().yMinimum()), str(self.dlg.ui.widget.extent().xMaximum()), str(self.dlg.ui.widget.extent().yMaximum()))
                # Scrive un file.
                if self.lt == 0:
                    QMessageBox.information( self.iface.mainWindow(),"Waring", "No postigis layer selected")
                    
                try:
                    
                    QgsMapLayerRegistry.instance().removeMapLayer(self.ChangeMapLayer().getLayerID())
                except:
                    pass         
                try:
                    self.w.close()
                except:
                    pass
               
        else:
            
            try:
                
                #self.writeLastBBox(str(self.dlg.ui.widget.extent().xMinimum()),str(self.dlg.ui.widget.extent().yMinimum()), str(self.dlg.ui.widget.extent().xMaximum()), str(self.dlg.ui.widget.extent().yMaximum()))
                QgsMapLayerRegistry.instance().removeMapLayer(self.ChangeMapLayer().getLayerID())
            except:
                pass
                #self.writeLastBBox(str(self.dlg.ui.widget.extent().xMinimum()),str(self.dlg.ui.widget.extent().yMinimum()), str(self.dlg.ui.widget.extent().xMaximum()), str(self.dlg.ui.widget.extent().yMaximum()))

            
        
                
                
        
              
        
    
