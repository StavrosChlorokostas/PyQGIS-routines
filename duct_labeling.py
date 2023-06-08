project = QgsProject.instance()

# Load necessary vector layers
dpareas = project.mapLayersByName('DP areas')[0]
trenches = project.mapLayersByName('test trench')[0]
crossings = project.mapLayersByName('test crossings')[0]
dducts = project.mapLayersByName('test d-duct')[0]
fducts = project.mapLayersByName('test f-duct')[0]
ducts = [dducts,fducts]

# Get the number of DPs
# dp_layer = QgsProject.instance().mapLayersByName('DPs')[0]
# fni = dps.fields().indexFromName('id')
# dp_id = trenches.uniqueValues(fni)
# Alternatively, get dp numbers from unique dp values in trench attribute table
fni = dpareas.fields().indexFromName('id')
dps = dpareas.uniqueValues(fni)

# Update trench dp
trenches.startEditing()
tr_dpidx= trenches.fields().indexFromName('dp')
for area in dpareas.getFeatures():
    area_id = area.attributes()[fni]
    bbox = area.geometry().boundingBox()
    filterRect = QgsFeatureRequest().setFilterRect(bbox)
    features = trenches.getFeatures(filterRect)
    for feature in features:
        if feature.geometry().within(area.geometry()):
            trenches.changeAttributeValue(feature.id(),tr_dpidx,area_id)

trenches.commitChanges()

crossings.startEditing()
cr_dpidx= crossings.fields().indexFromName('dp')
for area in dpareas.getFeatures():
    area_id = area.attributes()[fni]
    bbox = area.geometry().boundingBox()
    filterRect = QgsFeatureRequest().setFilterRect(bbox)
    features = crossings.getFeatures(filterRect)
    for feature in features:
        if feature.geometry().within(area.geometry()):
            crossings.changeAttributeValue(feature.id(),tr_dpidx,area_id)

crossings.commitChanges()

# Updating D-duct labels
dducts.startEditing()
dd_dpidx= dducts.fields().indexFromName('dp')
for area in dpareas.getFeatures():
    area_id = area.attributes()[fni]
    bbox = area.geometry().boundingBox()
    filterRect = QgsFeatureRequest().setFilterRect(bbox)
    features = dducts.getFeatures(filterRect)
    for feature in features:
        if feature.geometry().within(area.geometry()):
            dducts.changeAttributeValue(feature.id(),dd_dpidx,area_id)

dducts.commitChanges()

trenches.startEditing()

idx = trenches.fields().indexFromName('line')
label_idx = trenches.fields().indexFromName('label')

for dp in dps:
    # select trench segments per dp area
    trenches.selectByExpression( '"dp"=%s'%dp )
    features = trenches.selectedFeatures()
    dducts.selectByExpression( '"dp"=%s'%dp )
    ducts = dducts.selectedFeatures()
    ddo = [] # d-duct overlaps
    fdo = [] # f-duct overlaps
    # Get d-ducts and f-ducts overlapping with trench segment
    cnt = 1
    for trench in features:
        trenches.changeAttributeValue(trench.id(),idx,'L.%s'%cnt)
        cnt = cnt+1
        
        ddo24 = [] # d-duct overlaps
        ddo12 = []
        ddosd = []
        fdo7 = [] # f-duct overlaps
        fdo2 = []
        for dduct in ducts:
            check = trench.geometry().intersection(dduct.geometry())
            if trench.geometry().intersects(dduct.geometry()) and check.length()>0:
                if dduct['type']=='24x7/4':
                    ddo24.append(dduct.id())
                if dduct['type']=='12x7/4':
                    ddo12.append(dduct.id())
                if dduct['type']=='sd7':
                    ddosd.append(dduct.id())
        for fduct in fducts.getFeatures():
            check = trench.geometry().intersection(fduct.geometry())
            if trench.geometry().intersects(fduct.geometry()) and check.length()>0:
                if fduct['type']=='7x14/10':
                    fdo7.append(fduct.id())
                if fduct['type']=='2x14/10':
                    fdo2.append(fduct.id())
                    
        label = '(%s)'%trench['line']
        if len(ddosd)>0:
            label="%s%s,%s"%(len(ddosd),'xSD7',label)
        if len(ddo12)>0:
            label="%s%s,%s"%(len(ddo12),'x(12x7/4)',label)
        if len(ddo24)>0:
            label="%s%s,%s"%(len(ddo24),'x(24x7/4)',label)
        if len(fdo2)>0:
            label="%s%s,%s"%(len(fdo2),'x(2x14/10)',label)
        if len(fdo7)>0:
            label="%s%s,%s"%(len(fdo7),'x(7x14/10)',label)
        trenches.changeAttributeValue(trench.id(),label_idx,label)

trenches.commitChanges()

# Classify ducts by label
for layer in ducts:
    categories = []
    for dp in dps:
        # get layer symbol
        symbol = layer.renderer().symbol()
        # create renderer object
        category = QgsRendererCategory(dp,symbol,str(dp))
        # entry for the list of category items
        categories.append(category)
        
    renderer = QgsCategorizedSymbolRenderer('dp', categories)
    
    if renderer is not None:
        layer.setRenderer(renderer)
        
    layer.triggerRepaint()