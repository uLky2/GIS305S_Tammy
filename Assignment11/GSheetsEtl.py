import requests
from SpatialEtl import SpatialEtl

class GSheetsEtl(SpatialEtl):

    def __init__ (self, remote, local_dir, data_format, destination):
        super().__init__(remote, local_dir, data_format, destination)

    def extract(self):
        print(f"Extracting data from {self.remote} to {self.local_dir}")


    def process(self):
        super().extract()
        super().transform()
        super().load()