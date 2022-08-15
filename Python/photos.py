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

import time
import functools
import shutil

from numpy import true_divide

filehtmltemplate = '\
<html>\n\
\n\
<head>\n\
    <title>{title}</title>\n\
    <LINK href="../../main.css" type=text/css rel=stylesheet>\n\
</head>\n\
\n\
<body>\n\
    <p>{title} ({filename}) {showdate}</p>\n\
    <p>\n\
        {prev}\n\
        {next}\n\
        <a href="../{name}.htm">This roll</a>\n\
        <a href="{prevr}">Previous roll</a>\n\
        <a href="{nextr}">Next roll</a>\n\
    </p>\n\
    <p>\n\
    <table border="10">\n\
        <caption align="bottom">{filetitle}</Caption>\n\
        <tr>\n\
            <td><a href="../{filename}.jpg"><img src="../{filename}.jpg" height="600"></a></td>\n\
        </tr>\n\
    </table>\n\
    </p>\n\
</body>\n\
\n\
</html>\n\
'

folderhtmltemplate = '\
<html>\n\
<head>\n\
    <title>{title}</title>\n\
    <LINK href="../main.css" type=text/css rel=stylesheet>\n\
</head>\n\
<body>\n\
    <p>\n\
        <a href="{prevr}">Previous roll</a>\n\
        <a href="{nextr}">Next roll</a>\n\
        <a href="../index.htm">CD Index</a>\n\
        <a href="../../index.htm">Full Index</a>\n\
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
    <p>\n\
    </p>\n\
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
                <a href="htm/{name}.htm"><img src="../thumbs/{dirname}/th_{name}.jpg" border="0" {showdate}></a>\n\
            </td>\n\
'

coltemplatetitle = '\
            <td width="{percent}%">\n\
                {filetitle}\n\
            </td>\n\
'


def numstr(st):
    return f"{(int)(st)}" if st.isnumeric() else st

def cmpstr(st1, st2, reverse):
    if st1 > st2:
        return 1 if not reverse else -1
    elif st1 < st2:
        return -1 if not reverse else 1
    else:
        return 0

    
class File:
    def __init__(self, path, modified):
        self.path = path
        self.modified = modified
        self.title = ""
        self.basename = os.path.basename(os.path.dirname(path))
        self.basepath = os.path.dirname(path)
        self.basefilename=os.path.basename(path).split('.', 1)[0]
        parts = self.basefilename.split('-', 1)
        self.filesuffix = parts[1] if len(parts) > 1 else parts[0]

    def get_local_date(self):
        return self.modified.strftime('%d/%m/%Y')

    def get_file_name(self):
        return os.path.splitext(os.path.basename(self.path))[0]

    def get_dir_str(self):
        return self.get_file_name().split("-")[0]

    def get_thumb_name(self):
        x = os.path.abspath(os.path.join(self.basepath, "../thumbs", self.basename, f"th_{self.get_file_name()}.jpg"))
        return x

    def get_title(self):
        if len(self.title) > 0:
            return f"{numstr(self.filesuffix)} {self.title}"
        return numstr(self.filesuffix)


class Dir:
    def __init__(self, path):
        self.path = os.path.abspath(path)
        self.base = os.path.basename(self.path)
        self.heading = self.prev = self.next = ""
        self.files = []
        self.tablecolumns = 7
        self.tablewidth = 624
        self.reverse = False
        self.showdate = False

    def comparefilenames(self, item1, item2):
        retval = 0
        if item1.filesuffix.isnumeric() and item2.filesuffix.isnumeric():
            return (int)(item1.filesuffix) - (int)(item2.filesuffix) if not self.reverse else (int)(item2.filesuffix) - (int)(item1.filesuffix)
        else:
            return cmpstr(item1.filesuffix, item2.filesuffix, self.reverse)
            
    def get_next(self, relative="../"):
        if (self.next != ""):
            return self.next
        elif self.base.isnumeric():
            return f"../{relative}{(int)(self.base)+1}/{(int)(self.base)+1}.htm"
        else:
            return f"{relative}{self.base}.htm"

    def get_prev(self, relative="../"):
        if (self.prev != ""):
            return self.prev
        elif self.base.isnumeric():
            return f"../{relative}{(int)(self.base)-1}/{(int)(self.base)-1}.htm"
        else:
            return f"{relative}{self.base}.htm"

    def getdaterange(self):
        datefrom = dateto = self.files[0].modified
        for index, item in enumerate(self.files):
            datefrom = min(datefrom, item.modified)
            dateto = max(dateto, item.modified)

        if self.showdate:
            return f"({datefrom.strftime('%d/%m/%Y')} to {dateto.strftime('%d/%m/%Y')}) "
        else:
            return ""

    def createthumbs(self):
        thumbsfolder = os.path.abspath(
            os.path.join(self.path, "../thumbs", self.base))
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
        
        if not os.path.exists(googlefilename):
            self.CopyFile(filename, googlefilename)
        if not os.path.exists(filename):
            self.CopyFile(googlefilename, filename)

        if os.path.exists(googlefilename) and os.path.exists(filename):
            if os.path.getmtime(filename) > os.path.getmtime(googlefilename):
                self.CopyFile(filename, googlefilename)
            elif os.path.getmtime(filename) < os.path.getmtime(googlefilename):   
                self.CopyFile(googlefilename, filename)
            else:
                print ("Not copying", googlefilename )

    def ReadTitles(self):
        filename = os.path.join(self.path, "titles.txt")
        self.CopyTitlesToFromDrive(filename)
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
                                if (opt[1] == 'p'):
                                    self.prev = opt[2:]
                                elif (opt[1] == 'n'):
                                    self.next = opt[2:]
                                elif (opt[1] == 'r'):
                                    self.reverse = True
                                elif (opt[1] == 'j'):
                                    self.showdate = True
                    elif strs[0] == "Title:" and len(strs) > 1:
                        self.heading = strs[1]
                    elif len(self.heading) == 0:
                        self.heading = line.strip()
                    else:
                        item = self.search(strs[0])
                        if item != NULL and len(strs) > 1:
                            item.title = strs[1]




    def creatmainhtmlfile(self):
        mainhtmfile = os.path.join(self.path, f"{self.base}.htm")

        tablethumbcols = []
        tablenamecols = []
        tablerows = []

        for index, item in enumerate(self.files):

            tablethumbcols.append(coltemplatethumb.format(name=item.basefilename, dirname=self.base, showdate=f"title={item.get_local_date()}" if self.showdate else "", percent=100//self.tablecolumns))
            tablenamecols.append(coltemplatetitle.format(
                filetitle=item.get_title(), percent=100//self.tablecolumns))

            if (index + 1) % self.tablecolumns == 0 or index == len(self.files) - 1:
                tablerows.append(rowtemplate.format(tablerowthumbcols="".join(
                    tablethumbcols), tablerownamecols="".join(tablenamecols)))
                tablenamecols.clear()
                tablethumbcols.clear()

        html = folderhtmltemplate.format(title=self.heading, prevr=self.get_prev("./"), nextr=self.get_next("./"),
                                         daterange=self.getdaterange(), table="".join(tablerows))

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
    

    def createsubhtmlfiles(self):
        htmfolder = os.path.join(self.path, "htm")
        if os.path.isdir(htmfolder):
            for f in os.listdir(htmfolder):
                os.remove(os.path.join(htmfolder, f))
        else:
            os.makedirs(htmfolder, exist_ok=True)

        for index, item in enumerate(self.files):
            next = f'<a href="{self.files[index + 1 if index < len(self.files) - 1 else 0].basefilename}.htm">Next</a>'
            prev = f'<a href="{self.files[index - 1 if index > 0 else len(self.files) - 1].basefilename}.htm">Previous</a>'
            htmfile = os.path.join(
                htmfolder, f"{item.basefilename}.htm")

            html = filehtmltemplate.format(title=self.heading, name=self.base, showdate=item.get_local_date() if self.showdate else "", prev=prev,
                                           next=next, prevr=self.get_prev(), nextr=self.get_next(),
                                           filetitle=item.get_title(), filename=item.basefilename)

            with open(htmfile, 'w') as f:
                f.write(html)
                f.close()

    def MakeTitles(self):
        self.sortfiles()

        with open(os.path.join(self.path, "titles.txt"), 'w') as f:
            f.write(f"Title: {self.base}\n")
            for index, item in enumerate(self.files):
                f.write(f"{numstr(item.filesuffix)}\n")

    def search(self, id):
        for index, item in enumerate(self.files):
            if numstr(item.filesuffix) == numstr(id):
                return item
        return NULL

    def updateindex(self, startline, endline, bMain):
        indexline = f'<a href = "{os.path.basename(os.path.dirname(self.path)) + "/" if bMain else "" }{self.base}/{self.base}.htm" name = "{self.base}">{self.base}. {self.heading}.</a><font size="1" face="Comic Sans MS"> {self.getdaterange()}</font><br>\n'

        start = end = False
        insertindex = replaceindex = -1
        lines = []
        dirnum = numstr(self.base)
        filename = os.path.abspath(os.path.join(
            self.path, "../" if bMain else "", "../index.htm"))

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
        if image != NULL:
            image.set("datetime_original", filedate)
            image.set("datetime_digitized", filedate)
            # Write image with modified EXIF metadata to an image file
            with open(filename, 'wb') as new_image_file:
                new_image_file.write(image.get_file())

    return datetime.strptime(filedate, '%Y:%m:%d %H:%M:%S')


def readfolder(folder):
    readdir = Dir(folder)

    for f in glob.glob(os.path.join(folder, "*.jpg")):
        readdir.files.append(File(f, DateTaken(f)))
    readdir.ReadTitles()
    return readdir


def sortfiles(folder):
    tmpname = os.path.join(folder, "xxx-")
    finalname = os.path.join(folder, os.path.basename(folder) + "-")
    print("Sorting files in folder", folder)

    dir = readfolder(folder)
    dir.files.sort(key=get_date, reverse=False)

    for index, item in enumerate(dir.files):
        os.rename(item.path, f"{tmpname}{index+1:03d}.jpg")

    for index, item in enumerate(dir.files):
        os.rename(f"{tmpname}{index+1:03d}.jpg",
                  f"{finalname}{index+1:03d}.jpg")

    print(f"Finished Sorting {len(dir.files)} files in {folder}")


def createhtmlfiles(folder, bDoThumbs):

    print(f"Processing {folder}")
    dir = readfolder(folder)
    dir.sortfiles()

    dir.creatmainhtmlfile()
    dir.createsubhtmlfiles()
    if bDoThumbs:
        dir.createthumbs()

    dir.updateindex("<h4>Main Index</h4>",
                "<h4>Parents Old Photos</h4>", True)
    dir.updateindex("<body>", "</body>", False)

    return dir


def numberfromline(line):
    if '.htm" name = ' in line:
        loc = line.index('name = "')
        if loc > 0:
            loc2 = line.index('"', loc + 8)
            if loc2 > 0:
                return numstr(line[loc + 8:loc2])
    return -1

def main():
    if (len(sys.argv) > 1):
        tic = time.perf_counter()
        folder = sys.argv[1]
        if "-rs" in sys.argv:
            sortfiles(os.path.abspath(sys.argv[1]))
        elif "-h" in sys.argv:
            createhtmlfiles(os.path.abspath(sys.argv[1]), True)
        elif "*" in sys.argv:
            subfolders = [f.path for f in os.scandir(os.path.abspath(
                sys.argv[1])) if f.is_dir() and f.name != "thumbs"]
            for folder in subfolders:
                createhtmlfiles(folder, True)
        else:
            createhtmlfiles(folder, False)
        toc = time.perf_counter()
        print(f"Completed in {toc - tic:0.4f} seconds")
    else:
        print("Usage: photos <folder> <options>")


main()
