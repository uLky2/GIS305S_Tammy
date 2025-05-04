import arcpy.management
import requests
import os
import csv
import yaml

from SpatialEtl import SpatialEtl

class GSheetsEtl(SpatialEtl):

    """GSheets performs an extract, transform, and load process using a URL to a google spreadsheet.
    The spreadsheet must an address and zipcode column.

    Parametres: config_dict (Dictionairy): A Dictionairy containing a  remote_url key to the google spreadsheet and web geocoding services
    """

    config_dict = None
    def __init__ (self, config_dict):
        super().__init__(config_dict)

        """
            Initializes the GSheetsEtl class by calling the parent constructor (SpatialEtl).
            """

    def extract(self):
        print("Extracting addresses from google form spreadsheet")
        r = requests.get(self.config_dict.get('remote_url'))
        r.encoding = "utf-8"
        data = r.text
        with open(f"{self.config_dict.get('proj_dir')}addresses.csv", "w") as output_file:
            output_file.write(data)

        """
            Extracts data from spreadsheet to config dictionary and saves as csv file
            """

    def transform(self):

        """
            Transforms extracted addresses with geocoding into x,y coords
        """
        print("Add City, State")

        output_path = os.path.join(self.config_dict.get('proj_dir'), 'new_addresses.csv')
        transformed_file = open(output_path, "w")
        transformed_file.write("X,Y,Type\n")

        # Use config_dict to get the path to the partial address file
        with open(self.config_dict.get('partial_address_file'), "r") as partial_file:
            csv_dict = csv.DictReader(partial_file, delimiter=',')
            for row in csv_dict:
                address = row["Street Address"] + " Boulder CO"
                print(address)
                geocode_url = f"{self.config_dict.get('geocoder_prefix_url')}{address}{self.config_dict.get('geocoder_suffix_url')}"
                print(geocode_url)
                r = requests.get(geocode_url)

                resp_dict = r.json()
                x = resp_dict['result']['addressMatches'][0]['coordinates']['x']
                y = resp_dict['result']['addressMatches'][0]['coordinates']['y']
                transformed_file.write(f"{x},{y},Residential\n")

        transformed_file.close()

    def load(self):

        """
        Loads transformed addresses into ArcPro feature class & converts csv to points
            """
        arcpy.env.workspace = self.config_dict.get('proj_dir')  # Using proj_dir from config_dict
        arcpy.env.overwriteOutput = True

        in_table = os.path.join(self.config_dict.get('proj_dir'), 'new_addresses.csv')  # Use proj_dir for the CSV file
        out_feature_class = "avoid_points"
        x_coords = "X"
        y_coords = "Y"

        arcpy.management.XYTableToPoint(in_table, out_feature_class, x_coords, y_coords)

        print(arcpy.GetCount_management(out_feature_class))

    def process(self):

        """
            Executes ETL
        """
        self.extract()
        self.transform()
        self.load()