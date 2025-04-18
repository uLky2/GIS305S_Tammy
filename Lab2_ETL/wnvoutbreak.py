import yaml
import arcpy
from GSheetsEtl import GSheetsEtl

def setup():
    with open(r'C:\Users\Arc_U\Desktop\GIS3005\Assignment7\GIS305S_Tammy\config\wnvoutbreak.yaml') as f:
        config_dict = yaml.load(f, Loader=yaml.FullLoader)
    return config_dict
