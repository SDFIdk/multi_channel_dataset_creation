import arcpy
import configparser
def main(config):
    ini_parser = configparser.ConfigParser()
    ini_parser.read(config)
    section = "SETTINGS"
    gdb_file =ini_parser[section]["gdb_file"]
    merged_labels = ini_parser[section]["mask_featureclass"]
    print("clearing the feature_class..")

    merged_labels_feature_class = gdb_file+ "\\" + merged_labels  # r"F:\SDFI\DATA\MachineLearning\befaestelse\arcgislabels\arcgis_labels\arcgis_labels.gdb\merged_labels"
    print("filling the feature class with all labels stored in all the different feature classes that people have saved labels to...")
    unmerged_feature_classes= ini_parser[section]["unmerged_feature_classes"]
    arcpy.management.DeleteFeatures(merged_labels_feature_class)
    #fill the featureclass with all label data in all the differetn featureclasses the people working with making the labels have done
    arcpy.management.Append(unmerged_feature_classes,merged_labels_feature_class , "TEST", None, '', "OBJECTID IS NOT NULL")
    print(merged_labels + " : Done")







