class SpatialEtl:
    """Spatial ETL (Extract, Transform, Load) class.
        Attributes:
        config_dict (dict):
        Dictionary that contains configuration info.
        Methods:
        __init__(self, config_dict):
        Initializes SpatialEtl with the given dictionary.
        extract(self):
        Prints a message confirming extraction.
        """
    def __init__ (self, config_dict):
        self.config_dict = config_dict
        """Starts SpatialEtl"""
    def extract(self):
        print(f"Extracting data from {self.config_dict.get('remote.url')}"
              f" to {self.config_dict.get('proj_dir')}")
        """Print extraction"""

    #def transform(self):
        #print(f"Transforming {self.data_format}")
    #def load(self):
        #print(f"Loading data into {self.destination}")