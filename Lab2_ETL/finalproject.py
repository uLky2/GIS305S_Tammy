import arcpy
import os
import requests
from GSheetsEtl import GSheetsEtl
from wnvoutbreak import setup
import yaml

# My log exercise module

import logging

def etl(config_dict):

    """
        Run extract, transform, load process using GSheetsEtl
    """
    try:
        logging.debug("Enter etl()")
        etl_instance = GSheetsEtl(config_dict)
        etl_instance.process()
        logging.debug("Exit etl()")
    except Exception as e:
        logging.error(f"ETL process failed: {e}")
        raise

# Set environment
arcpy.env.workspace = r"C:\Users\Arc_U\Desktop\GIS3005\Lab1\WestNileOutbreak.gdb"
arcpy.env.overwriteOutput = True
input_layer = r"C:\Users\Arc_U\Desktop\GIS3005\Lab1\WestNileOutbreak.gdb\Mosquito_Larval_Sites"

def setup():

    """
        Load yaml and logging

        Returns: Loaded config. dictionary
    """
    try:
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
    except Exception as e:
        print(f"Error loading config/logging: {e}")
        raise

def buffer_layer(layer, distance):

    """
        BUffer input layer with given distance (ft)

        Parameters:
            layer: Name of layer to buffer
            distance: Buffer distance (ft)
    """
    try:
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
    except Exception as e:
        logging.error(f"Error buffering {layer}")
        raise

def intersect_layers(buffered_layers):
    """
        Intersect buffered layers into output.

        Parameters:
            buffered_layers

        Returns:
            Path to intersected layer
    """
    try:
        output_layer = os.path.join(arcpy.env.workspace, "intersect_output")
        arcpy.Intersect_analysis(buffered_layers, output_layer)
        logging.info(f"Intersect layer saved")
        return output_layer
    except Exception as e:
        logging.error(f"Error intersecting layers: {e}")
        raise

def spatial_join(address_layer, intersect_layer):
    """
        Executes spatial join between address layer and intersected areas

        Parameters:
            address_layer
            intersect_layer

        Returns:
            Path to join output
    """
    try:
        output_layer = os.path.join(r"C:\Users\Arc_U\Desktop\GIS3005\Lab1\Lab1_3005.gdb", "Target_Addresses")
        arcpy.SpatialJoin_analysis(address_layer, intersect_layer, output_layer)
        logging.info(f"Spatial join completed. Results saved to {output_layer}")
        return output_layer
    except Exception as e:
        logging.error(f"Error in spatial join: {e}")
        raise

def renderer():

    """
        Applies symbology to the intersect_output
    """
    try:
        aprx = arcpy.mp.ArcGISProject(r"C:\Users\Arc_U\Desktop\GIS3005\Lab1\Lab1_3005.aprx")
        map_doc = aprx.listMaps()[0]
        lyr = map_doc.listLayers("intersect_output")[0]
        sym = lyr.symbology
        sym.renderer.symbol.color = {'RGB': [255, 0, 0, 100]}  # Red fill with 50% transparency
        sym.renderer.symbol.outlineColor = {'RGB': [0, 0, 0, 100]}  # Black outline with 50% transparency
        lyr.symbology = sym
        lyr.transparency = 50
    except Exception as e:
        logging.error(f"Error applying symbology: {e}")
        raise

def main():
    """
        Workflow for whole function
        Executes all previous work
    """
    try:
        logging.info("Starting West Nile Virus Simulation")

        layers = ["Mosquito_Larval_Sites", "Wetlands_fc", "Lakes_and_Reservoirs", "OSMP_Properties"]
        buffered_layers = []

        for layer in layers:
            try:
                distance = input(f"Enter buffer distance (1000-5000 ft) for {layer}: ")
                buffered_layer = buffer_layer(layer, distance)
                buffered_layers.append(buffered_layer)
            except Exception as e:
                logging.error(f"Error buffering layer {layer}@ {e}")
                continue

        intersect_layer = intersect_layers(buffered_layers)

        address_layer = os.path.join(arcpy.env.workspace, "Addresses")
        joined_layer = spatial_join(address_layer, intersect_layer)

        if not arcpy.Exists(joined_layer):
            logging.error(f"Joined layer does not exist: {joined_layer}")
            raise FileNotFoundError(f"Joined layer does not exist: {joined_layer}")

        aprx = arcpy.mp.ArcGISProject(r"C:\Users\Arc_U\Desktop\GIS3005\Lab1\Lab1_3005.aprx")
        m = aprx.listMaps()[0]
        m.addDataFromPath(joined_layer)
        logging.info("Joined layer added to the project.")

        renderer()

        target_lyr = m.listLayers("Target_Addresses")[0]
        target_lyr.definitionQuery = "Join_Count = 1"

        layout = aprx.listLayouts("Layout1")[0]
        map_frame = layout.listElements("MAPFRAME_ELEMENT")[0]
        spatial_ref = arcpy.SpatialReference(104970)
        map_frame.map.spatialReference = spatial_ref

        aprx.save()
    except Exception as e:
        logging.error(f"Main function failed: {e}")
        raise

def count_addresses_within_intersect(joined_feature_class):

    """
        Counts addresses that are within the intersected area of mosquito risk.
    """
    try:
        count = arcpy.GetCount_management(joined_feature_class)
        logging.info(f"Total addresses in the potential area: {count[0]}")
    except Exception as e:
        logging.error(f"Error counting addresses: {e}")
        raise


def exportMap(config_dict):
    """
        Adds title/subtitle and exports layout to PDF
    """
    try:
        aprx_path = r"C:\Users\Arc_U\Desktop\GIS3005\Lab1\Lab1_3005.aprx"
        aprx = arcpy.mp.ArcGISProject(aprx_path)
        layouts = aprx.listLayouts()
        print(f"Layouts found: {[l.name for l in layouts]}")
        lyt = [l for l in layouts if l.name == "Layout1"][0]
        print("All layout element names:")
        for el in lyt.listElements():
            print(f"- {el.name} ({el.type})")

        subtitle = input("Enter subtitle: ")

        # Check if the layout has a Title element
        print("All layout element names:", [el.name for el in lyt.listElements("TEXT_ELEMENT")])
        title_elements = [el for el in lyt.listElements("TEXT_ELEMENT") if el.name == "Text 2"]
        if not title_elements:
            raise Exception("No Title element found on the layout.")

        for el in lyt.listElements():
            print(f"Element name: {el.name}")

        for el in title_elements:
            el.text += f"\n{subtitle}"

        output_pdf = f"{config_dict.get('proj_dir')}WestNileMap.pdf"
        lyt.exportToPDF(output_pdf)
        logging.info(f"Exported map to: {output_pdf}")
    except Exception as e:
        logging.error(f"Error in exporting map: {e}")
        raise

if __name__ == "__main__":
    try:
        config_dict = setup()
        print(config_dict)

    # Run the ETL process
        etl(config_dict)
        main()

        count_addresses_within_intersect("C:\\Users\\Arc_U\\Desktop\\GIS3005\\Lab1\\Lab1_3005.gdb\\Target_Addresses")
        exportMap(config_dict)
    except Exception as e:
        print(f"Script failed: {e}")
        logging.critical(f"Script execution failed: {e}")