import fnmatch
import os
import shutil
import glob


matches = []
for root, dirnames, filenames in os.walk('.'):
    for filename in fnmatch.filter(filenames, '*.jpg'):
        path = os.path.realpath(os.path.join(root, filename))
        if ("\\PHOTOS\\" in path.upper() and not "\\THUMBS\\" in path.upper()):
            matches.append(path)
target = R'D:\My Photographs\Scrapbook\decades'

for f in glob.glob(f'{target}\\**\\*.jpg' , recursive=True):
    os.remove(f)

years = {}
for  match in matches:
    year = match.split('\\')[4][1:];
    if year in years:
        years[year] += 1
    else:
        years[year] = 1

    newdir = os.path.join(target, match.split('\\')[4][1:4]+'0s')
    newname = os.path.join(newdir, f"{year}_{years[year]}.jpg")
    if not (os.path.exists(newdir)):
        os.makedirs(newdir)

    if not (os.path.exists(newname)):
        print(match, newname)
        shutil.copy(match, newname)
    else:
        i = 1
        newname1 = os.path.splitext(newname)[0] + f"_{i}" + os.path.splitext(newname)[1]
        while os.path.exists(newname1):
            i += 1;
            newname1 = os.path.splitext(newname)[0] + f"_{i}" + os.path.splitext(newname)[1]

        if not (os.path.exists(newname1)):
            print(match, newname1)
            shutil.copy(match, newname1)
        else:
            print (f"Duplicate: {match}")




