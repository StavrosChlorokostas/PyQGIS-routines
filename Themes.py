# Load Raster Layers
Geb = QgsProject.instance().mapLayersByName('Gebäude')[0]
Flur = QgsProject.instance().mapLayersByName('Flurstücke')[0]
overl = QgsProject.instance().mapLayersByName('Flurstücke/Gebäude/Weiteres/Gesetzliche Festlegungen/Tatsächliche Nutzung')[0]
DP = QgsProject.instance().mapLayersByName('DPs')[0]
overlay = [Geb,Flur,overl,DP]

# Load necessary vector layers
trenches = QgsProject.instance().mapLayersByName('Trench')[0]
trenches_copy = QgsProject.instance().mapLayersByName('Trench copy')[0]
Sps = QgsProject.instance().mapLayersByName('Segment Points')[0]
Units = QgsProject.instance().mapLayersByName('Potential')[0]
crossings = QgsProject.instance().mapLayersByName('Crossings')[0]
dpareas = QgsProject.instance().mapLayersByName('DP areas')[0]
layers = [trenches,trenches_copy,Sps,Units,dpareas,crossings]

# Get the number of DPs
# dp_layer = QgsProject.instance().mapLayersByName('DPs')[0]
# fni = dps.fields().indexFromName('id')
# dp_id = trenches.uniqueValues(fni)
# Alternatively, get dp numbers from unique dp values in trench attribute table
fni = dpareas.fields().indexFromName('id')
dps = dpareas.uniqueValues(fni)

# Classify layers by dp number
classify = [trenches,trenches_copy,Sps,Units,dpareas]
for layer in classify:
    categories = []
    # get layer symbol
    symbol = layer.renderer().symbol()
    # create renderer object
    for dp in dps:
        category = QgsRendererCategory(dp,symbol,str(dp))
        # entry for the list of category items
        categories.append(category)
        
    renderer = QgsCategorizedSymbolRenderer('dp', categories)
    del categories
    if renderer is not None:
        layer.setRenderer(renderer)
    
    layer.triggerRepaint()


# Get layer tree
root = QgsProject.instance().layerTreeRoot()
# Get layer tree view
ltv = iface.layerTreeView()
# Get layer tree model
ltm = ltv.layerTreeModel()
# Alternatively : ltm = ltv.model()

# Hide all layers
for layer in root.findLayers():
    print('%s is now hidden!'%(layer.name()))
    layer.setItemVisibilityChecked(False)
    
# Show the layers we want
for layer in (overlay+layers):
    node = root.findLayer(layer.id())
    node.setItemVisibilityChecked(True)
    print('%s is now visible!'%(layer.name()))
# Get themes list
mapThemesCollection = QgsProject.instance().mapThemeCollection()
mapThemes = mapThemesCollection.mapThemes()

# Create theme for each dp
from PyQt4.QtGui import QProgressDialog, QProgressBar

def progdialog(progress):
    dialog = QProgressDialog()
    dialog.setWindowTitle("Progress")
    dialog.setLabelText("Generating themes")
    bar = QProgressBar(dialog)
    bar.setTextVisible(True)
    bar.setValue(progress)
    dialog.setBar(bar)
    dialog.setMinimumWidth(300)
    dialog.show()
    return dialog, bar

print('Generating map themes for each DP area...')
for dp in dps:
    for layer in layers:
        # Get layer node
        node = root.findLayer(layer.id())
        legendNodes = ltm.layerLegendNodes(node)
        legendNode = [ln for ln in legendNodes if ln.data( Qt.DisplayRole ) == '%s' %dp]
        # Set Trench copy features visible only outside the dp area
        if layer.name()=='Crossings':
            for ln in [ln for ln in legendNodes if ln.data( Qt.DisplayRole ) != '%s' %dp]:
                if ln:
                    ln.setData( Qt.Checked, Qt.CheckStateRole )
        elif layer.name()=='Trench copy':
            if legendNode:
                legendNode[0].setData( Qt.Unchecked, Qt.CheckStateRole )
            for ln in [ln for ln in legendNodes if ln.data( Qt.DisplayRole ) != '%s' %dp]:
                if ln:
                    ln.setData( Qt.Checked, Qt.CheckStateRole )
        # Set all other layer features visible only inside the dp area
        else:
            if legendNode:
                legendNode[0].setData( Qt.Checked, Qt.CheckStateRole )
            for ln in [ln for ln in legendNodes if ln.data( Qt.DisplayRole ) != '%s' %dp]:
                if ln:
                    ln.setData( Qt.Unchecked, Qt.CheckStateRole )
    # Register theme for dp area
    mapThemeRecord = QgsMapThemeCollection.createThemeFromCurrentState(root,ltm)
    mapThemesCollection.insert('WO %s' %dp, mapThemeRecord)