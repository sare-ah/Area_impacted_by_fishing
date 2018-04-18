# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# AreaImpacted.py
# Created on: 2018-04-18  
# Author: Sarah Davies
# Description: Calculate an estimated cummulative area impacted by fishing events
#
# Steps:
# 1 - Select fishing events of appropriate length - remove extra long events
# 2 - Intersect reef and fishing events
# 2 - Buffer fishing events on reef
# 3 - Check to see if the buffer extends beyond the reef
# 4 - Clip again to the reef and calculate area impacted
# 5 - Create summary table

#------------------------------------------------------------------------------#
#------------------------------------------------------------------------------## ---------------------------------------------------------------------------

# Import arcpy module
import arcpy, csv			# import the ESRI arcpy module
from arcpy import env	# import env from arcpy
from arcpy.sa import *	# import Spatial Analyst
import os				# import Python os module

# Create envrionmental variables
arcpy.env.overwriteOutput = True

# Set variables from parameters from user 
fe = arcpy.GetParameterAsText(0) # FishingEvents shp
dist1 = arcpy.GetParameterAsText(1) # Upper bounds of set length
dist2 = arcpy.GetParameterAsText(2) # Buffer distance for FE
bufPoly = arcpy.GetParameterAsText(3) # Polygons to calcalate area within

# Get fishery name
desc = arcpy.Describe(fe)
fename = desc.baseName
arcpy.AddMessage(fename)

# Set workspace and declare variables
arcpy.env.workspace = out_folder_path = arcpy.GetParameterAsText(4)  
arcpy.AddMessage(out_folder_path)  
outLocation = fename+".gdb"

# Local variables:
v_Name_Lyr = fename+"_lyr"
v_Name_Events = fename+"_Events" 
v_Name_Intersect = fename+"_Intersect"
v_Name_Buffer = fename+"_Buffer"
v_Name_Final = fename+"_Final"

# Execute CreateFileGDB
arcpy.CreateFileGDB_management(out_folder_path, outLocation)

# Set workspace 
newGDB = out_folder_path +"\\"+ outLocation
arcpy.AddMessage(newGDB)
arcpy.env.workspace = newGDB

# Generate the length values Add Geometry Properties tool
arcpy.AddGeometryAttributes_management(fe,"LENGTH","","","")

# Make a layer from the feature class
arcpy.MakeFeatureLayer_management(fe,v_Name_Lyr)

# Select all fishing events that are less than upper bound distance
arcpy.AddMessage("Selecting fishing events...")
arcpy.SelectLayerByAttribute_management(v_Name_Lyr,"NEW_SELECTION","'LENGTH' > '" + dist1 + "'")

# Process: Intersect
arcpy.AddMessage("Intersecting fishing with polygons...")
inFeatures = [v_Name_Lyr,bufPoly]
arcpy.Intersect_analysis(inFeatures, v_Name_Intersect, "ALL", "", "LINE")

# Process: Buffer
arcpy.AddMessage("Buffering...")
arcpy.Buffer_analysis(v_Name_Intersect, v_Name_Buffer, dist2, "FULL", "ROUND", "LIST", "Reef")

# Process: Clip
arcpy.AddMessage("Clipping...")
arcpy.Clip_analysis(v_Name_Buffer, bufPoly, v_Name_Final, "")

# Process: Export Feature Attribute to ASCII...
arcpy.AddMessage("Exporting attribute table...")
arcpy.env.workspace = out_folder_path
input_features = outLocation+"\\"+v_Name_Final
export_ASCII = fename+"_Area.csv"
arcpy.ExportXYv_stats(input_features, ["Reef","Shape_Area"], "COMMA", fename+"_Area.csv", "ADD_FIELD_NAMES")
 

