#python -m pip install --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org GPSPhoto
#python -m pip install --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org exifread
#python -m pip install --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org piexif

import os
from GPSPhoto import gpsphoto


os.chdir("E:\\My Photographs\\photos\\DVD9\\423\\")
image_list = os.listdir()
image_list = [a for a in image_list if a.endswith('jpg')]

print(image_list)

for a in image_list: 
    fn = os.getcwd() + f'\\{a}'
    try:
        data = gpsphoto.getGPSData(fn)
        lat = data['Latitude']
        long = data['Longitude']
        print(f"https://www.google.com/maps/place/{lat},{long}")
    except:
        print (f"File: {a} Error")    

