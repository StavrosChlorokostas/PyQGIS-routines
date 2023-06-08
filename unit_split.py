from qgis.core import *
from qgis.PyQt.QtCore import QVariant
import math
project = QgsProject.instance()

# Load necessary layer with potential subscribers
subscribers = project.mapLayersByName('Potential')[0]
prov = subscribers.dataProvider()
caps = prov.capabilities()

# Distribute Units
subscribers.selectByExpression( '"UNITS">1' )
features = subscribers.selectedFeatures()
subscribers.startEditing()   
c_idx = subscribers.fields().indexFromName('CUSTOMER')
y_idx = subscribers.fields().indexFromName('Y')
x_idx = subscribers.fields().indexFromName('X')
u_idx = subscribers.fields().indexFromName('UNITS')

for feat in features:
    attr = feat.attributes()
    units = attr[u_idx]-1
    feat_X = attr[x_idx]
    feat_Y = attr[y_idx]
    for i in range(units):
        if i < 5 :
            j = i+1
            radius = 4 #distribution Radius for unit points
            # add a feature
            new = QgsFeature(subscribers.fields())
            if units > 6 :
                rep_angle=math.radians(360/5)
            if units < 6 :
                rep_angle=math.radians(360/units)
            new_X = feat_X+radius*math.sin(rep_angle*j)
            new_Y = feat_Y+radius*math.cos(rep_angle*j)
            new.setAttributes(attr)
            new.setAttribute(x_idx,new_X)
            new.setAttribute(y_idx,new_Y)
            new.setAttribute(c_idx,i+1)
            new.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(new_X,new_Y)))
            prov.addFeatures([new])
        if i >= 5 :
            j = i-4
            radius = 7
            rep_angle=math.radians(360/(units-5))
            new_X = feat_X+radius*math.sin(rep_angle*(j))
            new_Y = feat_Y+radius*math.cos(rep_angle*(j))
            new.setAttributes(attr)
            new.setAttribute(x_idx,new_X)
            new.setAttribute(y_idx,new_Y)
            new.setAttribute(c_idx,i+1)
            new.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(new_X,new_Y)))
            prov.addFeatures([new])
        if i >= 15 :
            j = i-14
            radius = 10
            rep_angle=math.radians(360/(units-15))
            new_X = feat_X+radius*math.sin(rep_angle*(j))
            new_Y = feat_Y+radius*math.cos(rep_angle*(j))
            new.setAttributes(attr)
            new.setAttribute(x_idx,new_X)
            new.setAttribute(y_idx,new_Y)
            new.setAttribute(c_idx,i+1)
            new.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(new_X,new_Y)))
            prov.addFeatures([new])

subscribers.commitChanges()
subscribers.triggerRepaint()

# Add C.ID field
subscribers.startEditing()
if caps & QgsVectorDataProvider.AddAttributes:
    res = prov.addAttributes([QgsField('C.ID', QVariant.String)])
    subscribers.updateFields()
    subscribers.commitChanges()

cid_idx = subscribers.fields().indexFromName('C.ID')

subscribers.startEditing()
for feature in subscribers.getFeatures():
    fid = feature.id()
    attr = feature.attributes()
    tzip = feature['TZIP']
    no = feature['NO']
    sup = feature['SUPPL']
    c = feature['CUSTOMER']
    if sup==NULL:
        string = tzip+str(no)+'-'+str(c)
    else:
        string = tzip+str(no)+str(sup)+'-'+str(c)
    subscribers.changeAttributeValue(fid,cid_idx,string)

subscribers.commitChanges()