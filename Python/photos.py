#python -m pip install --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org exif
#python -m pip install --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org PIL
#python -m pip install --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org GPSPhoto
#python -m pip install --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org exifread
#python -m pip install --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org piexif

from GPSPhoto import gpsphoto
from asyncio.windows_events import NULL
from datetime import datetime, timedelta, time
from logging import logMultiprocessing
import os
import glob
from shutil import copyfile
import sys
from tkinter import SEL_FIRST
from exif import Image as exifimage
from datetime import datetime
from PIL import Image as pilimage
from PIL import ExifTags
from string import digits
from datetime import datetime
import piexif

import time
import functools
import shutil
import filedate


filehtmltemplate = '\
<html>\n\
\n\
<head>\n\
    <title>{title}</title>\n\
    <LINK href="../../../../{level}main.css" type=text/css rel=stylesheet>\n\
</head>\n\
\n\
<body>\n\
    <p>{title} ({filename}) {showdate}</p>\n\
    <p>\n\
        {prev}\n\
        {next}\n\
        <a href="../{name}.htm">This roll</a>\n\
        {prevr}\n\
        {nextr}\n\
    </p>\n\
    <p>\n\
    <table border="10">\n\
        <caption align="bottom">{location} {filetitle}</Caption>\n\
        <tr>\n\
            <td><a href="../{filename}.jpg"><img src="../{filename}.jpg" height="600"></a></td>\n\
        </tr>\n\
    </table>\n\
    </p>\n\
</body>\n\
\n\
</html>\n\
'
subindex = '\
<html>\n\
<head>\n\
</head>\n\
<title>\n\
My Photographs\n\
</title>\n\
<body>\n\
<h3>My Photographs {year}</h3><p><a href="../../index.htm">Complete Index</a><br>{next}<br>{prev}</p>\n\
</body></html>\n\
'


folderhtmltemplate = '\
<html>\n\
<head>\n\
    <title>{title}</title>\n\
    <LINK href="../../../{level}main.css" type=text/css rel=stylesheet>\n\
</head>\n\
<body>\n\
    <p>\n\
        {prevr}\n\
        {nextr}\n\
        {negat}\n\
        {yearind}\n\
        {fullind}\n\
        Click any image to see a larger version\n\
    </p>\n\
    <p>\n\
        <strong>{title}</strong>\n\
        <font size="1" face="Comic Sans MS"> {daterange}</font>\n\
    </p>\n\
    <table border="1" cellspacing="1" width="624">\n\
{table}\n\
    </table>\n\
    <p></p>\n\
    <p>{makemodels}</p>\n\
</body>\n\
</html>\n\
'

rowtemplate = '\
        <tr>\n\
{tablerowthumbcols}\n\
        <tr>\n\
        </tr>\n\
{tablerownamecols}\n\
        </tr>\n\
'

coltemplatethumb = '\
            <td width="{percent}%">\n\
                <a href="htm/{name}.htm"><img src="thumbs/{name}.jpg" border="0" {showdate}></a>\n\
            </td>\n\
'

coltemplatetitle = '\
            <td width="{percent}%">\n\
               {location} {filetitle}\n\
            </td>\n\
'


def numstr(st):
    return int(st) if st.isnumeric() else st

def cmpstr(st1, st2, reverse):
    if st1 > st2:
        return 1 if not reverse else -1
    elif st1 < st2:
        return -1 if not reverse else 1
    else:
        return 0

    
class File:
    def __init__(self, path, modified, created):
        self.path = path
        self.modified = modified
        self.created = created
        self.title = ""
        self.basename = os.path.basename(os.path.dirname(path))
        self.basepath = os.path.dirname(path)
        self.basefilename=os.path.basename(path).split('.', 1)[0]
        parts = self.basefilename.split('-', 1)
        self.filesuffix = parts[1] if len(parts) > 1 else parts[0]
        self.root = self.path.split(os.sep)[-3]
        self.lat = NULL
        self.long = NULL
        
    def get_local_date(self):
        try:
            return self.modified.strftime('%d/%m/%Y')
        except:
            print (f"bad date {self.path}" )
            return datetime.today
        
    def get_local_date_time(self):
        try:
            return self.modified.strftime("%d/%m/%Y %H:%M:%S")
        except:
            print (f"bad date {self.path}" )
            return datetime.today
        
    def get_make_model(self):
        make = ""
        model = ""
        try:
            im = pilimage.open(self.path)
            exif = im.getexif()
            if exif is not None:
                for key, val in exif.items():                      
                    if key in ExifTags.TAGS:
                        if ExifTags.TAGS[key] == "Make":
                            make = val
                        if ExifTags.TAGS[key] == "Model":
                            model = val
            if make != "" and model != "":
                return f"{make} {model}"
            elif make != "":
                return make
            else:
                return model
        except:
            return ""  
       
    def get_url(self, bSub):

        url = ""

        if self.lat == NULL:
            try:
                data = gpsphoto.getGPSData(self.path)
                self.lat = data['Latitude']
                self.long = data['Longitude']
            except:
                self.lat = 0
                self.long = 0

        dotdot = "../" if bSub else "" 
        if self.lat != 0 or self.long != 0:
            url = (f"<a href=\"https://www.google.com/maps/place/{self.lat},{self.long}\" target=\"_blank\"><img src=\"../../../{dotdot}pin.jpg\" border=\"0\" title=Location></a>")
        
        return url
 
    def get_file_name(self):
        return os.path.splitext(os.path.basename(self.path))[0]

    def get_dir_str(self):
        return self.get_file_name().split("-")[0]

    def get_thumb_name(self):
        x = os.path.abspath(os.path.join(self.basepath, "thumbs", f"{self.get_file_name()}.jpg"))
        return x

    def get_title(self):
        if len(self.title) > 0:
            return f"{numstr(self.filesuffix)} {self.title}"
        return numstr(self.filesuffix)


class Dir:
    def __init__(self, path):
        self.path = os.path.abspath(path)
        self.base = os.path.basename(self.path)
        self.heading = self.prev = self.next = self.longheading = ""
        self.files = []
        self.tablecolumns = 7
        self.tablewidth = 624
        self.reverse = False
        self.showdate = True
        self.root=self.path.split(os.sep)[-2]
        self.dir = self.path.split(os.sep)[-1]
        self.subFolders = []
        self.titles = []
        self.sortbytitle = False

    def comparefilenames(self, item1, item2):
        retval = 0
        if item1.filesuffix.isnumeric() and item2.filesuffix.isnumeric():
            return (int)(item1.filesuffix) - (int)(item2.filesuffix) if not self.reverse else (int)(item2.filesuffix) - (int)(item1.filesuffix)
        else:
            return cmpstr(item1.filesuffix, item2.filesuffix, self.reverse)

    def getdaterange(self):
        if len(self.files) == 0:
            return ""

        datefrom = dateto = self.files[0].modified
        for index, item in enumerate(self.files):
            try:
                datefrom = min(datefrom, item.modified)
                dateto = max(dateto, item.modified)
            except: 
                print ( f"Bad date {item.path}")

        if self.showdate:
            return f"({datefrom.strftime('%d/%m/%Y')} to {dateto.strftime('%d/%m/%Y')}) "
        else:
            return ""

    def createthumbs(self):

        thumbsfolder = os.path.abspath(os.path.join(self.path, "thumbs")) 

        if os.path.isdir(thumbsfolder):
            for f in os.listdir(thumbsfolder):
                os.remove(os.path.join(thumbsfolder, f))
        else:
            os.makedirs(thumbsfolder, exist_ok=True)

        for file in self.files:
            try:
                im = pilimage.open(file.path)

                im.thumbnail((180, 180))
                exif = im.getexif()
                if exif is None:
                    print('Sorry, image has no exif data.')
                else:
                    for key, val in exif.items():                      
                        if key in ExifTags.TAGS:
                            if ExifTags.TAGS[key] == "Orientation":
                                if (val == 8):
                                    im = im.rotate(90)
                                elif (val == 3):
                                    im = im.rotate(180)
                                elif (val == 6):
                                    im = im.rotate(270)
                im.save(file.get_thumb_name())
            except:
                continue

    def CopyFile(self, source, dest):
        shutil.copy2(source, dest)        
        print ("Copying", source, "to", dest)

    def CopyTitlesToFromDrive(self, filename):
        googlefilename = None
        env = os.getenv("USERPROFILE")
        if env != None:
            splitname = filename.replace('/', '\\').split('\\')
            if len (splitname) >= 6:
                googlefilename = os.path.join (env, 'Google Drive', 'Titles', splitname[2], splitname[3], splitname[4], splitname[5])
        if  (googlefilename == None):
            return
        
        if not os.path.isdir(os.path.dirname(googlefilename)):
            os.makedirs(os.path.dirname(googlefilename), exist_ok=True)
        if not os.path.isdir(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        if not os.path.exists(googlefilename) and os.path.exists(filename):
            self.CopyFile(filename, googlefilename)
        if not os.path.exists(filename)  and os.path.exists(googlefilename):
            self.CopyFile(googlefilename, filename)

        if os.path.exists(googlefilename) and os.path.exists(filename):
            if os.path.getmtime(filename) > os.path.getmtime(googlefilename):
                self.CopyFile(filename, googlefilename)
            elif os.path.getmtime(filename) < os.path.getmtime(googlefilename):   
                self.CopyFile(googlefilename, filename)
            else:
                print ("Not copying", googlefilename )

    def ReadTitles(self, level=0):
        filename = os.path.join(self.path, "" if level == 0 else "../", "titles.txt")
        #self.CopyTitlesToFromDrive(filename)
        if not os.path.exists(filename):
            self.MakeTitles()
        with open(filename, 'r') as f:
            while True:
                line = f.readline()
                if len(line) == 0:
                    break

                strs = line.strip().split(maxsplit=1)
                opts = line.strip().split()
                if len(strs) > 0:
                    if strs[0][0] == "-":
                        for opt in opts:
                            if len(opt) > 1 and opt[0] == '-':
                                if (opt[1] == 'r'):
                                    self.reverse = True
                                elif (opt[1] == 'j'):
                                    self.showdate = True
                                elif (opt[1] == 't'):
                                    self.sortbytitle = True
                    elif strs[0] == "Title:" and len(strs) > 1:
                        self.heading = self.longheading  = strs[1]
                    elif len(self.heading) == 0:
                        self.heading = self.longheading = line.strip()
                    else:
                        item = self.search(strs[0])
                        if item != NULL:
                            if len(strs) > 1:
                                item.title = strs[1]
                            self.titles.append(line.strip())

                    if len(self.heading) > 0 and self.heading[-1] == '\\':
                        self.longheading = self.heading[0:-1]
                        self.heading = self.longheading
                        line = f.readline().strip()
                        while True:
                            #print (line)
                            if line[-1] != '\\':
                                self.longheading += f"<br>{line}"
                                break;
                            else:
                                self.longheading += f"<br>{line[0:-1]}"
                                line = f.readline().strip()


    def creatmainhtmlfile(self, level):
        mainhtmfile = os.path.join(self.path, f"{self.base}.htm")

        tablethumbcols = []
        tablenamecols = []
        tablerows = []
        makes = {""}


        if self.sortbytitle:
            files = []       
            for j, title in enumerate(self.titles):
                for i, file in enumerate(self.files):
                    if str(title) == str(file.get_title()):
                        files.append(file)  
            self.files = files    

        #print (f"creathhtmlfile {len(self.files)}")
        for index, item in enumerate(self.files):

            makes.add(item.get_make_model())
            tablethumbcols.append(coltemplatethumb.format(name=item.basefilename, dirname=self.base, showdate=f"title=\"{item.get_local_date_time()}\"" if self.showdate else "", percent=100//self.tablecolumns))
            tablenamecols.append(coltemplatetitle.format(
                location=item.get_url(False), filetitle=item.get_title(), percent=100//self.tablecolumns))

            if (index + 1) % self.tablecolumns == 0 or index == len(self.files) - 1:
                tablerows.append(rowtemplate.format(tablerowthumbcols="".join(
                    tablethumbcols), tablerownamecols="".join(tablenamecols)))
                tablenamecols.clear()
                tablethumbcols.clear()

        makes.remove('')
        
        prevrollh = "" if prevroll == "" or level !=0 else f'<a href="{prevroll}">Previous roll</a>'
        nextrollh = "" if nextroll == "" or level !=0 else f'<a href="{nextroll}">Next roll</a>'

        #print (f"prevroll {prevroll} nextroll {nextroll}")
        if level != 0:
           prevrollh = f'<a href="../{self.root}.htm">Back</a>'
           nextrollh = ""

        subpath = ""
        for subfolder in self.subFolders:
            if ( os.path.exists(os.path.join(self.path, subfolder))):
                link = subfolder.split('\\')[-1]
                #print (f"!!{subfolder} {link}")
                subpath += f'<a href="{link}/{link}.htm">{link}</a> '

        yearindex = "Year Index"

        html = folderhtmltemplate.format(title=self.longheading, prevr=prevrollh, nextr=nextrollh, negat=subpath,
                                         daterange=self.getdaterange(), makemodels=(f'Cameras: {", ".join(makes)}' if len(makes) > 0 else ""), table="".join(tablerows),
                                         level="" if level==0 else "../", 
                                         yearind="" if level>0 else f'<a href="../index.htm">{yearindex}</a>',
                                         fullind="" if level>0 else '<a href="../../../index.htm">Full Index</a>')
                                                                                   
        with open(mainhtmfile, 'w') as f:
            f.write(html)
            f.close()

    def sortfiles(self):

        numericfilenames = []
        nonnumericfilenames = []

        for index, item in enumerate(self.files):  
            if item.filesuffix.isnumeric():
                numericfilenames.append(item)
            else:
                nonnumericfilenames.append(item)

        numericfilenames.sort(key=functools.cmp_to_key(self.comparefilenames))
        nonnumericfilenames.sort(key=functools.cmp_to_key(self.comparefilenames))

        self.files = numericfilenames
        self.files.extend(nonnumericfilenames)
    

    def createsubhtmlfiles(self, level):
        htmfolder = os.path.join(self.path, "htm")
        if os.path.isdir(htmfolder):
            for f in os.listdir(htmfolder):
                try:
                    os.remove(os.path.join(htmfolder, f))
                except:
                    print (f"Failed to remove {os.path.join(htmfolder, f)}")           
        else:
            os.makedirs(htmfolder, exist_ok=True)

        for index, item in enumerate(self.files):
            next = f'<a href="{self.files[index + 1 if index < len(self.files) - 1 else 0].basefilename}.htm">Next</a>'
            prev = f'<a href="{self.files[index - 1 if index > 0 else len(self.files) - 1].basefilename}.htm">Previous</a>'
            htmfile = os.path.join(
                htmfolder, f"{item.basefilename}.htm")

            prevrollh = "" if prevroll == "" or level > 0 else f'<a href="../{prevroll}">Previous roll</a>'
            nextrollh = "" if nextroll == "" or level > 0 else f'<a href="../{nextroll}">Next roll</a>'
            html = filehtmltemplate.format(title=self.heading, name=self.base, showdate=item.get_local_date() if self.showdate else "", prev=prev,
                                           next=next, prevr=prevrollh, nextr=nextrollh,
                                           location=item.get_url(True), filetitle=item.get_title(), filename=item.basefilename
                                           ,level="" if level==0 else "../")

            with open(htmfile, 'w') as f:
                f.write(html)
                f.close()

    def MakeTitles(self):
        self.sortfiles()
        #print (f"MakeTitles {self.path} {self.base}")
        fn = os.path.join(self.path, "titles.txt")
        #print (f"Creating titles {fn}")
        with open(fn, 'w') as f:
            f.write(f"Title: {self.base}\n")
            for index, item in enumerate(self.files):
                f.write(f"{numstr(item.filesuffix)}\n")

    def search(self, id):
        for index, item in enumerate(self.files):
            if numstr(item.filesuffix) == numstr(id):
                return item
        return NULL

    def updateindex(self, startline, endline, bMain):

        x = os.path.basename(os.path.dirname(os.path.dirname(self.path))) +"/" + os.path.basename(os.path.dirname(self.path)) + "/"
        indexline = f'<a href = "{x if bMain else "" }{self.base}/{self.base}.htm" name = "{self.base}">{self.base}. {self.heading}.</a><font size="1" face="Comic Sans MS"> {self.getdaterange()}</font><br>\n'
        start = end = False
        insertindex = replaceindex = -1
        lines = []
        dirnum = numstr(self.base)
        filename = os.path.abspath(os.path.join(
            self.path, "../../" if bMain else "", "../index.htm"))

        print (f"updateindex {filename}")

        if not bMain:
            if not (os.path.exists(filename)):
                with open(filename, "w") as file:
                    print (f"nextyear {nextyear} prevyear {prevyear}" )

                    hnext = "" if nextyear == "" else f'<a href="../{nextyear[6:]}/index.htm">Next Year {os.path.basename(nextyear)}</a>'
                    hprev = "" if prevyear == "" else f'<a href="../{prevyear[6:]}/index.htm">Previous Year {os.path.basename(prevyear)}</a>'
                    html = subindex.format(year=self.root, next=hnext, prev=hprev)                    
                    file.write(html)
                    file.close()
                 
        with open(filename, "r") as file:
            lines = file.readlines()
            for index, line in enumerate(lines):
                if line.strip()[0:len(startline)] == startline:
                    start = True
                    continue
                if line.strip()[0:len(endline)] == endline:
                    end = True
                if not start:
                    continue

                rollnum = numberfromline(line)
                if type(dirnum) == type(""):
                    rollnum = f"{rollnum}"
                

                if type(rollnum) == type(dirnum):
                    if rollnum == dirnum:
                        replaceindex = index
                    elif rollnum > dirnum or end:
                        if insertindex == -1:
                            insertindex = index
                elif end:
                    if insertindex == -1:
                        insertindex = index - 1
                        break

            file.close()
        if replaceindex >= 0:
            lines[replaceindex] = indexline
        elif insertindex >= 0:
            lines.insert(insertindex, indexline)

        with open(filename, "w") as file:
            file.writelines(lines)
            file.close()


def get_date(File):
    return File.modified

def get_date_created(File):
    return File.created

def get_name(File):
    return File.basename

def DateCreated(filename):
    #print(filename)

    try:
        filedate = datetime.fromtimestamp(os.path.getctime(filename)).strftime('%Y:%m:%d %H:%M:%S')
    except:
        filedate = datetime.fromtimestamp(os.path.getmtime(filename)).strftime('%Y:%m:%d %H:%M:%S')   
            
    return datetime.strptime(filedate, '%Y:%m:%d %H:%M:%S')


def GetDateTaken(filename):

    filedate = None
    file = open(filename, "rb")
    try:
        image = exifimage(file)
        if image.has_exif:
            filedate = image.get("datetime_original")
    except:
        filedate = None
    return filedate

def SetDateTaken1(filename, newfilename, filedate):
    #print(f"Setting date of {filename} to {filedate}")
    file = open(filename, "rb")
    try:
        image = exifimage(file)
        if image != NULL:
          #  image.set("datetime_original", filedate)
            image.set("datetime_digitized", "1996:09:01 09:15:30")
            # Write image with modified EXIF metadata to an image file
            with open(newfilename, 'wb') as new_image_file:
                new_image_file.write(image.get_file())

    except:
        None


def SetDateTaken(filename, newfilename, filedate):
    strtm = datetime(int(1981), int(2), int(3), 4, 0, 0).strftime("%Y:%m:%d %H:%M:%S")
    #print(f"Setting date of {filename} to {filedate} {strtm}")
    try:
                exif_dict = piexif.load(filename)
 
                #Update DateTimeOriginal
                exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = filedate
                #Update DateTimeDigitized               
                exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = filedate
                #Update DateTime
                exif_dict['0th'][piexif.ImageIFD.DateTime] = filedate
                exif_bytes = piexif.dump(exif_dict)
                piexif.insert(exif_bytes, filename)
                #print(f"Set date of {filename} to {filedate}")
    except:
        None

def DateTaken(filename):

    filedate = None
    file = open(filename, "rb")
    try:
        image = exifimage(file)
        if image.has_exif:
            filedate = image.get("datetime_original")
    except:
        image = NULL

    file.close()

    if (filedate == None):
        filedate = datetime.fromtimestamp(
            os.path.getmtime(filename)).strftime('%Y:%m:%d %H:%M:%S')
#        if image != NULL:
#            image.set("datetime_original", filedate)
#            image.set("datetime_digitized", filedate)
#            # Write image with modified EXIF metadata to an image file
#            with open(filename, 'wb') as new_image_file:
#                new_image_file.write(image.get_file())

    try:
        retval = datetime.strptime(filedate, '%Y:%m:%d %H:%M:%S')
        return retval
    except:
        #print ( f"{filename} {filedate}" )
        return datetime.today


def readfolder(folder, level = 0):
    readdir = Dir(folder)

    for f in glob.glob(os.path.join(folder, "*.jpg")):
        readdir.files.append(File(f, DateTaken(f), DateCreated(f)))
    if level == 0 or "egatives" in folder:
        readdir.ReadTitles(level)
    return readdir

def readdir(folder):
    readdir = Dir(folder)

    for f in glob.glob(os.path.join(folder, "*.jpg")):
        readdir.files.append(File(f, NULL, NULL))
    return readdir

def sortfilesbyfiledate(folder):
    tmpname = os.path.join(folder, "xxx-")
    finalname = os.path.join(folder, os.path.basename(folder) + "-")
    #print("Sorting files in folder", folder)

    dir = readfolder(folder)
    dir.files.sort(key=get_date, reverse=False)

    for index, item in enumerate(dir.files):
        os.rename(item.path, f"{tmpname}{index+1:03d}.jpg")

    for index, item in enumerate(dir.files):
        os.rename(f"{tmpname}{index+1:03d}.jpg", f"{finalname}{index+1:03d}.jpg")
        #print ( f"{item.modified} {finalname}{index+1:03d}.jpg")

    #print(f"Finished Sorting {len(dir.files)} files in {folder}")


def sortfilesbydatecreated(folder):
    tmpname = os.path.join(folder, "xxx-")
    finalname = os.path.join(folder, os.path.basename(folder) + "-")
    #print("Sorting files in folder", folder)

    dir = readfolder(folder)
    dir.files.sort(key=get_date_created, reverse=False)

    for index, item in enumerate(dir.files):
        os.rename(item.path, f"{tmpname}{index+1:03d}.jpg")

    for index, item in enumerate(dir.files):
        os.rename(f"{tmpname}{index+1:03d}.jpg", f"{finalname}{index+1:03d}.jpg")
        #print ( f"{item.created} {finalname}{index+1:03d}.jpg")

    #print(f"Finished Sorting {len(dir.files)} files in {folder}")


def sortfilesbyfilename(folder, rootname):
    tmpname = os.path.join(folder, "xxx-")
    if len(rootname) > 0:
        finalname = os.path.join(folder, rootname)
    else:    
        finalname = os.path.join(folder, os.path.basename(folder) + "-")
    #print("Sorting files in folder", folder)

    dir = readdir(folder)
    dir.files.sort(key=get_name, reverse=False)

    for index, item in enumerate(dir.files):
        os.rename(item.path, f"{tmpname}{index+1:03d}.jpg")

    for index, item in enumerate(dir.files):
        os.rename(f"{tmpname}{index+1:03d}.jpg",
                  f"{finalname}{index+1:03d}.jpg")

    #print(f"Finished Sorting {len(dir.files)} files in {folder}")

def copywithdate(src, dest):
    #print (f"Copy {src} to {dest} preserving dates")
    shutil.copy (src,dest)
    srcfile = filedate.File(src)
    dstfile = filedate.File(dest)

    dstfile.set (created=srcfile.get().get('created'))
    dstfile.set (modified=srcfile.get().get('modified'))
    dstfile.set (accessed=srcfile.get().get('accessed'))

def splitfilesbyfilename(folder, nSplits):
    #print ( folder, nSplits)
    newpathbase = "dir"
    dir = readdir(folder)
    dir.files.sort(key=get_name, reverse=False)

    for index in range(nSplits):
        finalname = os.path.join(folder, f"{newpathbase}-{index+1}")
        #print (finalname)
        os.makedirs(finalname, exist_ok=True)

    for index, item in enumerate(dir.files):
        oldname = os.path.join(folder, f"{item.get_file_name()}.jpg")
        newbase = f"{newpathbase}-{(index % nSplits)+1}"
        newname = f"{newpathbase}-{(index % nSplits)+1}"
        newpath = os.path.join(folder, newbase, f"{item.get_file_name()}.jpg")

        if not os.path.exists (newpath):
            copywithdate(oldname, newpath)
            #print ( f"Copying {oldname} to {newpath}")

def createhtmlfiles(folder, bDoThumbs, level=0):
    os.chdir(folder)
    global prevroll, nextroll

    if level == 0:
        prevroll = getprevfolder(folder)
        nextroll = getnextfolder(folder)
    else:
        prevroll = ""
        nextroll = ""
    print (f"This: {folder}\nPrev: {prevroll}\nNext: {nextroll}")
        
    subfolders = [ f.path for f in os.scandir(folder) if f.is_dir() and not f.name in ["htm", "thumbs"]]

    dir = readfolder(folder, level)
    dir.sortfiles()

    dir.subFolders = subfolders
    dir.creatmainhtmlfile(level)
    dir.createsubhtmlfiles(level)
    if bDoThumbs:
        dir.createthumbs()

    if level == 0:
        dir.updateindex("<h4>Main Index</h4>", "<!--END-->", True)
        dir.updateindex("<body>", "</body>", False)
    
    for subFolder in subfolders:
        if os.path.exists (subFolder):
            createhtmlfiles(subFolder, bDoThumbs, 1)

def numberfromline(line):
    if '.htm" name = ' in line:
        loc = line.index('name = "')
        if loc > 0:
            loc2 = line.index('"', loc + 8)
            if loc2 > 0:
                return numstr(line[loc + 8:loc2])
    return -1


def sortbydirname(dir1, dir2):
    s1 = dir1.split(maxsplit=1)
    s2 = dir2.split(maxsplit=1)

    n1 = ''.join(filter(str.isdigit, s1[0]))
    n2 = ''.join(filter(str.isdigit, s2[0]))

    if n1.isnumeric() and n2.isnumeric():
        if int(n1) == int(n2) and len(s1) == 2 and len(s2) == 2:
            return 1 if s1[1] > s2[1] else -1  
        else:
            return 1 if int(n1) > int(n2) else -1  
    else:
        return 1 if dir1 > dir2 else -1         

def scanfolder (folder):
    ret = []
    for it in os.scandir(folder):
        if it.is_dir() and it.name != "thumbs":
            ret.append(it.name)
    ret.sort(key=functools.cmp_to_key(sortbydirname))
    return ret

nextyear = ""
prevyear = ""

def getprevfolder(folder):
    global nextyear, prevyear
    yearpath = "../" 
    decadepath = "../../" 
    rootpath = "../../../" 
    prevyearpath = ""
    res = ""

    rollname = os.path.basename(folder)
    yearname = os.path.basename(os.path.dirname(folder))
    decadename = os.path.basename(os.path.dirname(os.path.dirname(folder)))

    yearfolder = scanfolder(yearpath)
    decadefolder = scanfolder(decadepath)
    rootfolder = scanfolder(rootpath)

    rollindex = yearfolder.index(rollname)
    yearindex = decadefolder.index(yearname)
    decadeindex = rootfolder.index(decadename)
    prevyearpath = f"{decadepath}{decadefolder[yearindex-1]}"


    if rollindex >= 1:
        res = f"{yearpath}{yearfolder[rollindex-1]}/{yearfolder[rollindex-1]}.htm"
    
    elif yearindex >= 1:
        prevyearfolder = scanfolder(prevyearpath)
        res = f"{prevyearpath}/{prevyearfolder[len(prevyearfolder)-1]}/{prevyearfolder[len(prevyearfolder)-1]}.htm"
    
    elif decadeindex >= 1:
        prevdecadepath = f"{rootpath}{rootfolder[decadeindex-1]}"
        prevdecadefolder = scanfolder(prevdecadepath)
        prevyearpath = f"{prevdecadepath}/{prevdecadefolder[len(prevdecadefolder)-1]}"
        prevyearfolder = scanfolder(prevyearpath)
        res = f"{prevyearpath}/{prevyearfolder[len(prevyearfolder)-1]}/{prevyearfolder[len(prevyearfolder)-1]}.htm"

    prevyear = prevyearpath
    print (f"prevyear!! {prevyear}")

    return res



def getnextfolder(folder):
    global nextyear, prevyear
    yearpath = "../" 
    decadepath = "../../" 
    rootpath = "../../../" 
    res = ""
    nextyearpath = ""

    rollname = os.path.basename(folder)
    yearname = os.path.basename(os.path.dirname(folder))
    decadename = os.path.basename(os.path.dirname(os.path.dirname(folder)))

    yearfolder = scanfolder(yearpath)
    decadefolder = scanfolder(decadepath)
    rootfolder = scanfolder(rootpath)

    rollindex = yearfolder.index(rollname)
    yearindex = decadefolder.index(yearname)
    decadeindex = rootfolder.index(decadename)

    if yearindex < len(decadefolder) - 1:
        nextyearpath = f"{decadepath}{decadefolder[yearindex+1]}"
    else:
        nextdecadepath = f"{rootpath}{rootfolder[decadeindex+1]}"
        nextdecadefolder = scanfolder(nextdecadepath)
        nextyearpath = f"{nextdecadepath}/{nextdecadefolder[0]}"

    if rollindex < len(yearfolder) - 1:
        res =  f"{yearpath}{yearfolder[rollindex+1]}/{yearfolder[rollindex+1]}.htm"
    
    elif yearindex < len(decadefolder) - 1:
        nextyearfolder = scanfolder(nextyearpath)
        res = f"{nextyearpath}/{nextyearfolder[0]}/{nextyearfolder[0]}.htm"
    
    elif decadeindex < len(rootfolder)-1:
        nextyearfolder = scanfolder(nextyearpath)
        res = f"{nextyearpath}/{nextyearfolder[0]}/{nextyearfolder[0]}.htm"

    nextyear = nextyearpath
    print (f"nextyear!! {nextyear}")

    return res

prevroll = ""
nextroll = ""

def fixnegativedates(folder):
    ret = []
    for it in os.scandir(folder):
        if it.is_dir():
            fixnegativedates(it.path)
        else:
            fn, ext = os.path.splitext(it.path)
            pos = it.path
            neg=os.path.join(os.path.dirname(pos), "Negatives", os.path.basename(pos))
            negn=os.path.join(os.path.dirname(pos), "Negatives", "n_" + os.path.basename(pos))

            if ext.lower() == ".jpg" and  os.path.exists(neg):
                posd = GetDateTaken(pos)            
                negd = GetDateTaken(neg)
                #print (pos, posd, neg, negd)
                if (posd != None and negd == None):
                    SetDateTaken(neg, negn, posd)



def decadepaths(folder):
    folders = folder.split(os.sep)
    decade = ""
    thisdecade = 0

    for  i in range(0, len(folders)):
        if len(folders[i]) == 5 and folders[i][0:4].isnumeric() and (folders[i][4] == 's' or folders[i][4] == 'S'):
            thisdecade = int(folders[i][0:4])
            decade = folders[0] + os.sep
            for j in range (1, i):
                decade = os.path.join(decade, folders[j])
        
    return f"{decade}{os.sep}{thisdecade-10}s", f"{decade}{os.sep}{thisdecade}s", f"{decade}{os.sep}{thisdecade+10}s"

def main():
    if (len(sys.argv) > 1):
        if "fixn" in sys.argv:
            fixnegativedates(".")
            exit(0)

        tic = time.perf_counter()
        folder = os.path.realpath(sys.argv[1])
    
        if not "*" in sys.argv and not "**" in sys.argv:
            if not os.path.exists(folder) or not os.path.isdir(folder):
                print (f"folder {folder} does not exist")
                exit(0)

        bDoThumb = False
        if "-h" in sys.argv:
            bDoThumb = True

        if "-rs" in sys.argv:
            sortfilesbyfiledate(os.path.abspath(sys.argv[1]))
            exit(0)
        if "-rsc" in sys.argv:
            sortfilesbydatecreated(os.path.abspath(sys.argv[1]))
            exit(0)
        elif "-rsn" in sys.argv:
            if len(sys.argv) == 4:
                sortfilesbyfilename(os.path.abspath(sys.argv[1]), sys.argv[3])
            elif len(sys.argv) == 3:
                sortfilesbyfilename(os.path.abspath(sys.argv[1]), "")
            elif len(sys.argv) > 4:
                stDir = os.path.abspath(sys.argv[1])
                sortfilesbyfilename(stDir, "")
                for  i in range(3, len(sys.argv)):
                    stNewDir = os.path.join(os.path.dirname(stDir), sys.argv[i])
                    sortfilesbyfilename(stNewDir, "")
            exit(0)
        elif "-rss" in sys.argv:
            if len(sys.argv) >= 4 and sys.argv[3].isnumeric():
                splitfilesbyfilename(os.path.abspath(sys.argv[1]), (int)(sys.argv[3]))
            else:
                print ("Enter number of splits")
            exit(0)
        elif "*" in sys.argv:
            subfolders = [f.path for f in os.scandir(os.path.abspath(
                sys.argv[1])) if f.is_dir() and f.name != "thumbs"]
            for folder in subfolders:
                createhtmlfiles(folder, bDoThumb)
        elif "**" in sys.argv:
            start = -1
            if len(sys.argv) > 3 and sys.argv[3].isnumeric():
                start = int(sys.argv[3])

            subfolders = [f.path for f in os.scandir(os.path.abspath(
                sys.argv[1])) if f.is_dir() and f.name != "thumbs"]
            for folder in subfolders:
                subfolders1 = [f.path for f in os.scandir(os.path.abspath(os.path.join(sys.argv[1], folder))) if f.is_dir() and f.name != "thumbs"]
                for folder1 in subfolders1:
                    dir = folder1.split(os.sep)[-1]
                    #print (dir)
                    stnDir = ''.join(filter(str.isdigit, dir))
                    if stnDir.isnumeric():
                        nDir = int(stnDir)
                        if nDir < start:
                            continue
                    createhtmlfiles(folder1, bDoThumb)
        else:
            createhtmlfiles(folder, bDoThumb)
        toc = time.perf_counter()
        #print(f"Completed in {toc - tic:0.4f} seconds")
    else:
        print("Usage: photos <folder> <options>")


main()
