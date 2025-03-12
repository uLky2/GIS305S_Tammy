import arcpy


def intersect(layer_list, input_lyr_name):
    arcpy.Intersect_analysis(layer_list, input_lyr_name)

def buffer_layer(input_gdb, input_layer, dist):
    # Run a buffer analysis on the input_layer with a user specified distance

    # Distance units are always miles
    units = " miles"
    dist = dist + units
    # Output layer will always be named input layer + "_buf
    output_layer = r"C:\Users\Arc_U\Desktop\GIS3005\Assignment1\Assignment1.gdb\\" + input_layer + "_buf"
    # Always use buffer parameters FULL, ROUND, ALL
    buf_layer = input_gdb + input_layer
    arcpy.Buffer_analysis(buf_layer, output_layer,
                          dist, "FULL", "ROUND", "ALL")
    return output_layer

def main():
    # Define your workspace and point it at the modelbuilder.gdb
    arcpy.env.workspace = r"C:\Users\Arc_U\Desktop\GIS3005\Assignment1\Assignment1.gdb"
    arcpy.env.overwriteOutput = True

    # Buffer cities
    input_gdb = r"C:\Users\Arc_U\Desktop\GIS3005\Assignment1\Admin\AdminData.gdb\\"

    # Change me this next line below to use GetParamters!!
    dist = arcpy.GetParameterAsText(0)

    buf_cities = buffer_layer(input_gdb, "cities", dist)

    # Change me this next line below to use GetParameters!!
    print("Buffer layer " + buf_cities + " created.")

    # Buffer rivers
    # Change me this next line below to use GetParamters!!
    dist = arcpy.GetParameterAsText(1)
    buf_rivers = buffer_layer(input_gdb, "us_rivers", dist)
    print("Buffer layer " + buf_rivers + " created.")

    # Define lyr_list variable
    # Ask the user to define an output layer name
    # Change me this next line below to use GetParamters!!
    intersect_lyr_name = arcpy.GetParameterAsText(2)

    if intersect_lyr_name.isnumeric():
        arcpy.AddError("Invalid name: Intersect layer name cannot be numeric.")
        return

    arcpy.AddMessage(f"Intersect layer name: '{intersect_lyr_name}'")

    lyr_list = [buf_rivers, buf_cities]
    intersect(lyr_list, intersect_lyr_name)
    print(f"New intersect layer generated called: {intersect_lyr_name}")

    aprx = arcpy.mp.ArcGISProject(r"C:\Users\Arc_U\Desktop\GIS3005\Assignment1\Assignment1.aprx")
    map_doc = aprx.listMaps()[0]
    map_doc.addDataFromPath(rf"C:\Users\Arc_U\Desktop\GIS3005\Assignment1\Assignment1.gdb\{intersect_lyr_name}")

    aprx.saveACopy(r"C:\Users\Arc_U\Desktop\Assignment1_test.aprx")


if __name__ == '__main__':
    main()