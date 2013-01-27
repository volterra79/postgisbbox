"""
/***************************************************************************
 PostgisBBox
                                 A QGIS plugin
 Load all postgis features that intersect with Bounding Box
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
 This script initializes the plugin, making it known to QGIS.
"""
def name():
    return "Postgis Bounding Box"
def description():
    return "Load all postgis features that intersect with Bounding Box"
def version():
    return "Version 1.0"
def icon():
    return "postgis_select.png"
def qgisMinimumVersion():
    return "1.0"
def classFactory(iface):
    # load PostgisBBox class from file PostgisBBox
    from postgisbbox import PostgisBBox
    return PostgisBBox(iface)
