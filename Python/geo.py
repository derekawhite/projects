#python -m pip install --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org GPSPhoto
#python -m pip install --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org exifread
#python -m pip install --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org pillow
#>python -m pip install --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org piexif
#python -m pip install --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org gpsphoto
#python -m pip install --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org pyperclip

from GPSPhoto import gpsphoto
import os
import pathlib
import sys
import pyperclip
from datetime import datetime
from exif import Image as exifimage
import functools

today = datetime.today()
tcxtrackpoints = ""
wpttrackpoints = ""
trpkttrackpoints = ""
kmltrackpoints = ""
kmlplacemarks = ""

kmltemplate = '\
<?xml version="1.0" encoding="utf-8" standalone="yes"?>\n\
<kml xmlns="http://www.opengis.net/kml/2.2">\n\
  <Document>\n\
    <name><![CDATA[{name}]]></name>\n\
    <visibility>1</visibility>\n\
    <open>1</open>\n\
    <Snippet><![CDATA[{name}]]></Snippet>\n\
    <Style id="gv_waypoint_normal">\n\
      <IconStyle>\n\
        <color>ffffffff</color>\n\
        <scale>1</scale>\n\
        <Icon>\n\
          <href>https://maps.google.com/mapfiles/kml/pal4/icon56.png</href>\n\
        </Icon>\n\
        <hotSpot x="0.5" xunits="fraction" y="0.5" yunits="fraction" />\n\
      </IconStyle>\n\
      <LabelStyle>\n\
        <color>ffffffff</color>\n\
        <scale>1</scale>\n\
      </LabelStyle>\n\
    </Style>\n\
    <Style id="gv_waypoint_highlight">\n\
      <IconStyle>\n\
        <color>ffffffff</color>\n\
        <scale>1.2</scale>\n\
        <Icon>\n\
          <href>https://maps.google.com/mapfiles/kml/pal4/icon56.png</href>\n\
        </Icon>\n\
        <hotSpot x="0.5" xunits="fraction" y="0.5" yunits="fraction" />\n\
      </IconStyle>\n\
      <LabelStyle>\n\
        <color>ffffffff</color>\n\
        <scale>1</scale>\n\
      </LabelStyle>\n\
    </Style>\n\
    <StyleMap id="gv_waypoint">\n\
      <Pair>\n\
        <key>normal</key>\n\
        <styleUrl>#gv_waypoint_normal</styleUrl>\n\
      </Pair>\n\
      <Pair>\n\
        <key>highlight</key>\n\
        <styleUrl>#gv_waypoint_highlight</styleUrl>\n\
      </Pair>\n\
    </StyleMap>\n\
    <Folder id="Waypoints">\n\
      <name>Waypoints</name>\n\
      <visibility>1</visibility>\n\
      {places}\n\
    </Folder>\n\
    <Folder id="Tracks">\n\
      <name>Tracks</name>\n\
      <visibility>1</visibility>\n\
      <open>0</open>\n\
      <Placemark>\n\
        <name><![CDATA[{name}]]></name>\n\
        <Snippet></Snippet>\n\
        <description><![CDATA[&nbsp;]]></description>\n\
        <Style>\n\
          <LineStyle>\n\
            <color>ff0000e6</color>\n\
            <width>4</width>\n\
          </LineStyle>\n\
        </Style>\n\
        <LineString>\n\
          <tessellate>1</tessellate>\n\
          <altitudeMode>clampToGround</altitudeMode>\n\
          <coordinates>\n\
            {points}\n\
          </coordinates>\n\
        </LineString>\n\
      </Placemark>\n\
    </Folder>\n\
  </Document>\n\
</kml>\n\
'

kmlplacetemplate = '\
      <Placemark>\n\
        <name>{name}</name>\n\
        <Snippet></Snippet>\n\
        <description><![CDATA[&nbsp;]]></description>\n\
        <styleUrl>#gv_waypoint</styleUrl>\n\
        <Point>\n\
          <altitudeMode>clampToGround</altitudeMode>\n\
          <coordinates>{long},{lat}</coordinates>\n\
        </Point>\n\
      </Placemark>\n\
'

tcxtemplate = '\
<TrainingCenterDatabase xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd">\n\
 <Activities>\n\
  <Activity Sport="Running">\n\
   <Lap>\n\
    <Track>\n\
     {track}\n\
    </Track>\n\
   </Lap>\n\
  </Activity>\n\
 </Activities>\n\
</TrainingCenterDatabase>\n\
'
tracktemplate = '\
     <Trackpoint>\n\
      <Time>{time}</Time>\n\
      <Position>\n\
       <LatitudeDegrees>{lat}</LatitudeDegrees>\n\
       <LongitudeDegrees>{long}</LongitudeDegrees>\n\
      </Position>\n\
     </Trackpoint>\n\
'
wpttemplate = '\
	<wpt lat="{lat}" lon="{long}">\n\
		<name>{name}</name>\n\
	</wpt>\n\
'
trpkttemplate = '\
			<trkpt lat="{lat}" lon="{long}">\n\
				<time>{time}</time>\n\
			</trkpt>\n\
'

trktemplate = '\
	<trk>\n\
		<name>{name}</name>\n\
		<trkseg>\n\
            {trkpts}\n\
		</trkseg>\n\
	</trk>\n\
'

gpxtemplate = '\
<?xml version="1.0" encoding="UTF-8"?>\n\
<gpx>\n\
{wpts}\n\
{trk}\n\
</gpx>\n\
'

def BuildTcxTrackPoint(lat, long, timestr):
    if timestr == "" or (lat == 0 and long == 0):
        return ""
    return tracktemplate.format(time=timestr, lat=lat, long=long)

def BuildWptTrackPoint(lat, long, index):

    if index == 0 or (lat == 0 and long == 0):
        return ""
    return kmlplacetemplate.format(name=index, lat=lat, long=long)


def Buildkmlplacemark(lat, long, index):

    if index == "0" or (lat == 0 and long == 0):
        return ""
    return kmlplacetemplate.format(name=index, lat=lat, long=long)


def BuildtrpktTrackPoint(lat, long, timestr):
    if timestr == "" or (lat == 0 and long == 0):
        return ""
    return trpkttemplate.format(time=timestr, lat=lat, long=long)


def getClipboardText():
    return pyperclip.paste()

def get_geodata(path):
    data = None
    try:
        data = gpsphoto.getGPSData(path)
        if len(data) == 0:
            print(f"No Geo Data in {path}")      
            return ""
                 
        lat = data['Latitude']
        long = data['Longitude']

        return f"{lat},{long}"
    except Exception as e:
        print(f"Invalid Geo Data in {path}")
        return ""

def DateTaken(filename):

    filedate = None
    file = open(filename, "rb")
    try:
        image = exifimage(file)
        if image.has_exif:
            filedate = image.get("datetime_original")
    except:
        image = None

    file.close()

    if (filedate == None):
        filedate = datetime.fromtimestamp(
            os.path.getmtime(filename)).strftime('%Y:%m:%d %H:%M:%S')


    try:
        retval = datetime.strptime(filedate, '%Y:%m:%d %H:%M:%S')
        return retval
    except:
        print ( f"{filename} {filedate}" )
        return datetime.today
    
def get_gpsdata(path):
    data = None
    try:
        data = gpsphoto.getGPSData(path)
        if len(data) == 0:
            print(f"No Geo Data in {path}")      
            return 0,0,""
                 
        lat = data['Latitude']
        long = data['Longitude']

#       try:
#           gpstime = data['UTC-Time'].split(':')
#           gpsdate = data['Date'].split('/')
#          gpsdatetime = datetime(int(gpsdate[2]), int(gpsdate[0]), int(gpsdate[1]), int(gpstime[0]), int(gpstime[1]), int(gpstime[2]))
#        except Exception as e:
        gpsdatetime = DateTaken(path)

        timestr = f"{gpsdatetime.year:04}-{gpsdatetime.month:02}-{gpsdatetime.day:02}T{gpsdatetime.hour:02}:{gpsdatetime.minute:02}:{gpsdatetime.second:02}"
        return lat,long,timestr   
    except Exception as e:
        print(f"Invalid Geo Data in {path}")
        return 0,0,""
    
def set_geodata(path, lat, long):
    try:
        print (f"Setting geodata of {path} to {lat},{long}")
        photo = gpsphoto.GPSPhoto(path)
        info = gpsphoto.GPSInfo((lat, long))
        photo.modGPSData(info, path)
    except Exception as e:
        print (f"Set No Geo Data {path} {e}")

def isfloat(element: any) -> bool:
    try:
        if element == None:
            return False            
        float(element)
        return True
    except ValueError:
        return False

lat = None
long = None
files = []
filens = []
doCheck = False
doAll = False
doGPS = False
doFolders = False
excl = False
doReverse = False
pattern = ""
reverses = {}

titles = {}
def ReadTitles(path):
    global titles
    label = path if path != "." else  os.getcwd().split('\\')[-1]

    try:
        
        with open(f"{path}\\titles.txt") as f:
            for line in f:
                sp = line.split(maxsplit=1)
                if len(sp) == 2 and sp[0].isnumeric():
                    titles[f"{label}-{int(sp[0])}"] = sp[1].strip()
                if line[0:2] == "-r":
                    reverses[label] = 1
    except:
        return

def gettitle(index):
    try:    
        find = f"{index.split('-')[0]}-{int(index.split('-')[1])}"
        title=titles[find]
        try:
            fixedtitle = title.split('>')[-2].split('<')[0]
        except:
            fixedtitle = title
        #return fixedtitle.translate( { ord(i): None for i in '&'} )
        return fixedtitle.replace('&', 'and')
    except:
        return index

def comparefilenames(item1, item2):
    retval = 0
    try:
        label1 = int(item1.split('-')[-1].split('.')[0])
        label2 = int(item2.split('-')[-1].split('.')[0])
        dir1 = ""
        dir2 = ""
        if len(item1.split('\\')) > 0:
            dir1 = item1.split('\\')[0]
        if len(item2.split('\\')) > 0:
            dir2 = item2.split('\\')[0]
        
        if dir1 != "" and dir2 != "" and dir2 != dir1:
            return 1 if dir2 < dir1 else -1            
            
        if not dir1 in reverses:
           return 1 if label2 < label1 else -1
        else:
            return 1 if label2 > label1 else -1
    except:
        return 1 if item2 < item1 else -1
    
def scan(path):
    global files
    ReadTitles(path)
    for it in os.scandir(path):
        if not it.is_dir():
            if pathlib.Path(it.path).suffix.lower() == ".jpg" and not "thumbs" in it.path: 
                files.append(it.path)
        else:
            if doCheck:
                scan (os.path.join(path,it.name))

if  "check" in sys.argv or "c" in sys.argv:
    doCheck = True
if  "gps" in sys.argv or "g" in sys.argv:
    doGPS = True
    if "-e" in sys.argv:
        excl = True
if  "-f" in sys.argv:
    doFolders = True    
if  "-r" in sys.argv:
    doReverse = True        
    
if not doFolders:    
    scan (".")
else:
    for arg in sys.argv:
        if os.path.isdir(arg):
            scan(arg)

if doGPS:
    files.sort(key=functools.cmp_to_key(comparefilenames))

for arg in sys.argv:
    if arg == "h":  #Home
        lat = 53.283315053140974
        long = -6.310825075688937
        print ("Setting to Home")
    elif arg == "f":  #Ferns
        lat = 52.5980703618268
        long = -6.4716902951731985
        print ("Setting to Ferns")    
    elif arg == "b":  #Bray Head
        lat = 53.17385244381283
        long = -6.080280201842008
        print ("Setting to Bray Head")  
    elif arg == "br":  #Brookfield
        lat = 53.313533548090405 
        long = -6.261790574489668
        print ("Setting to Brookfield")  
    elif arg == "r":  #Riversdale Ave
        lat = 53.30685203159486
        long = -6.2801125158601
        print ("Setting to Riversdale")  
    elif not arg.isnumeric() and isfloat(arg):
        if lat == None:
            lat = float(arg)
        elif long == None:
            long = float(arg)
    elif arg.isnumeric() and not doFolders:
        filenum = int(arg)
        for file in files:
            try:
                if int(file.split('-')[1].split('.')[0]) == filenum:
                    filens.append (file)
                    break;
            except:
                continue
    elif arg == '*':
        filens = files
    elif ".jpg" in arg:
        filens.append (arg)
    elif len(arg.split('-')) == 2:
        first = arg.split('-')[0]
        last = arg.split('-')[1]
        if first.isnumeric() and last.isnumeric():
            for file in files:
                try:
                    n = int(file.split('-')[1].split('.')[0])
                    if n >= int(first) and n <= int(last):
                        filens.append (file)
                except:
                    continue   
    else:
        co = arg.split(',')
        if len(co) == 2 and isfloat(co[0]) and isfloat (co[1]):
            if lat == None:
                lat = float(co[0])
            if long == None:
                long = float(co[1])

if len(filens) == 0 and (doCheck or doGPS):
    filens = files

if lat == None and long == None:
    clip = getClipboardText()
    try:
        lat = float(clip.split('@')[1].split(',')[0])
        long = float(clip.split('@')[1].split(',')[1])
    except:
        try:
            lat = float(clip[clip.find('<latitude>')+10:clip.find('</latitude>')])
            long = float(clip[clip.find('<longitude>')+11:clip.find('</longitude>')])
        except:
            lat = None
            long = None

    if len(clip) > 3 and len(clip) < 100:
        co = clip.split(',')
        if len(co) == 2 and isfloat(co[0]) and isfloat (co[1]):
            lat = float(co[0])
            long = float(co[1])    

print ( f"Set Lat {lat} Long {long}")
lastlat = 0
lastlong = 0
index = 1

for filen in filens:
    if doCheck:
        get_geodata(filen)
    elif doGPS:
        lat,long,gpsdate = get_gpsdata(filen)
        if lat != lastlat or long !=lastlong:
            if excl == False or lat < 52 or lat > 54 or long > -5 or long < -7:
                print (f"{filen},{lat},{long}")
                try:
                    index = int(filen.split('.')[-2].split('-')[-1])
                except:
                    index = 0
                #index += 1
                kmlindex = filen.split('.')[-2].split('\\')[-1]
                kmltitle = gettitle(kmlindex)
                tcxtrackpoints += BuildTcxTrackPoint (lat, long, gpsdate)
                wpttrackpoints += BuildWptTrackPoint(lat, long, index)
                trpkttrackpoints += BuildtrpktTrackPoint(lat, long, gpsdate)
                if lat !=0 or long != 0:
                    kmltrackpoints += f"{long},{lat}\n            "
                kmlplacemarks += Buildkmlplacemark(lat, long, kmltitle)
                if lat != 0 or long != 0:
                    index += 1

        lastlat = lat
        lastlong = long

    else:
        print(f"Before {filen} {get_geodata(filen)}")
        if isfloat (lat) and isfloat (long):
            if not doAll:
                i = input(f"Type Y to confirm set geo data of {filen} to {lat},{long} (or enter for all): ")
            else:
                i = 'Y'
            if i == 'y' or i == 'Y' or i=='a' or i=='':
                set_geodata(filen, lat, long)    
                print(f"After {filen} {get_geodata(filen)}")
                if i=='a' or i=='A' or i == '':
                    doAll = True
            else:
                print(f"Skip {filen}")

if doGPS:
    fileb = os.getcwd().split('\\')[-1]
    label = os.getcwd().split('\\')[-2] + "-" + os.getcwd().split('\\')[-1]
    if doFolders:
        dirn = filens[0].split('\\')[0]
        fileb = f"{dirn}\\{dirn}"
        label = os.getcwd().split('\\')[-1] + "-" + dirn
        print ( f"Filebas {fileb}")
    fn = fileb+".tcx"
    with open(fn, 'w') as f:
        f.write(tcxtemplate.format(track=tcxtrackpoints))
        f.close()
        print (f"created {fn}")

    fn = fileb+".gpx"
    with open(fn, 'w') as f:

        trkpts = trktemplate.format(name=label, trkpts=trpkttrackpoints)
        f.write(gpxtemplate.format(wpts=wpttrackpoints, trk=trkpts))
        f.close()
        print (f"created {fn}")

    fn = fn = fileb+".kml"
    with open(fn, 'w') as f:
        f.write(kmltemplate.format(name=label, places=kmlplacemarks, points=kmltrackpoints))
        f.close()
        print (f"created {fn}")