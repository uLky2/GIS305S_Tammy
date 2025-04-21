import arcpy
import os
import requests
from GSheetsEtl import GSheetsEtl
from wnvoutbreak import setup
import yaml

# My log exercise module

import logging

def etl(config_dict):
    logging.debug("Enter etl()")
    etl_instance = GSheetsEtl(config_dict)
    etl_instance.process()
    logging.debug("Exit etl()")


# Set environment
arcpy.env.workspace = r"C:\Users\Arc_U\Desktop\GIS3005\Lab1\WestNileOutbreak.gdb"
arcpy.env.overwriteOutput = True
input_layer = r"C:\Users\Arc_U\Desktop\GIS3005\Lab1\WestNileOutbreak.gdb\Mosquito_Larval_Sites"

def setup():
    with open(r'C:\Users\Arc_U\Desktop\GIS3005\Assignment7\GIS305S_Tammy\config\wnvoutbreak.yaml') as f:
        config_dict = yaml.load(f, Loader=yaml.FullLoader)

    logging.basicConfig(
        filename=f"{config_dict.get('proj_dir')}wnv.log",
        filemode="w",
        level=logging.DEBUG,
        format='%(name)s - %(levelname)s - %(message)s'
    )

    logging.debug('This is a debug statement')
    logging.info('This will get logged to a file')
    logging.warning('This is a warning')
    logging.error('This is an error!')

    return config_dict



def buffer_layer(layer, distance):
    logging.debug(f"Entering Buf layer")
    input_layer = os.path.join(arcpy.env.workspace, layer)
    output_layer = os.path.join(arcpy.env.workspace, f"{layer}_buffer")
    arcpy.Buffer_analysis(
        input_layer,
        output_layer,
        f"{distance} Feet",
        "FULL",
        "ROUND",
        "ALL"
    )
    logging.debug(f"Exiting Buf layer")
    return output_layer


def intersect_layers(buffered_layers):
    output_layer = os.path.join(arcpy.env.workspace, "intersect_output")
    arcpy.Intersect_analysis(buffered_layers, output_layer)
    logging.info(f"Intersect layer saved")
    return output_layer


def spatial_join(address_layer, intersect_layer):
    output_layer = os.path.join(arcpy.env.workspace, "joined_addresses.shp")
    arcpy.SpatialJoin_analysis(address_layer, intersect_layer, output_layer)
    logging.info(f"Spatial join completed. Results saved to {output_layer}")
    return output_layer


def main():
    logging.info("Starting West Nile Virus Simulation")

    layers = ["Mosquito_Larval_Sites", "Wetlands_fc", "Lakes_and_Reservoirs", "OSMP_Properties"]
    buffered_layers = []

    for layer in layers:
        distance = input(f"Enter buffer distance (1000-5000 ft) for {layer}: ")
        buffered_layer = buffer_layer(layer, distance)
        buffered_layers.append(buffered_layer)

    intersect_layer = intersect_layers(buffered_layers)

    address_layer = os.path.join(arcpy.env.workspace, "Addresses")
    joined_layer = spatial_join(address_layer, intersect_layer)

    aprx = arcpy.mp.ArcGISProject(r"C:\Users\Arc_U\Desktop\GIS3005\Lab1\Lab1_3005.aprx")
    m = aprx.listMaps()[0]
    m.addDataFromPath(joined_layer)
    logging.info("Joined layer added to the project.")

def count_addresses_within_intersect(joined_feature_class):
    count = arcpy.GetCount_management(joined_feature_class)
    logging.info(f"Total addresses in the potential area: {count[0]}")


def exportMap(config_dict):
    aprx = arcpy.mp.ArcGISProject(f"{config_dict.get('proj_dir')}Lab1_3005.aprx")
    lyt = aprx.listLayouts()[0]
    subtitle = input("Enter subtitle: ")

    for el in lyt.listElements():
        if "Title" in el.name:
            el.text += f"\n{subtitle}"


if __name__ == "__main__":
    config_dict = setup()
    print(config_dict)

    # Run the ETL process
    etl(config_dict)
    main()

    count_addresses_within_intersect("C:\\Users\\Arc_U\\Desktop\\GIS3005\\Lab1\\WestNileOutbreak.gdb\\Joined_Addresses")
