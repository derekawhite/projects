from exif import Image


def format_dms_coordinates(coordinates):
    return f"{coordinates[0]}° {coordinates[1]}\' {coordinates[2]}\""

def dms_coordinates_to_dd_coordinates(coordinates, coordinates_ref):
    decimal_degrees = coordinates[0] + \
                      coordinates[1] / 60 + \
                      coordinates[2] / 3600
    
    if coordinates_ref == "S" or coordinates_ref == "W":
        decimal_degrees = -decimal_degrees
    
    return decimal_degrees

def draw_map_for_location(latitude, latitude_ref, longitude, longitude_ref):
    import webbrowser
    
    decimal_latitude = dms_coordinates_to_dd_coordinates(latitude, latitude_ref)
    decimal_longitude = dms_coordinates_to_dd_coordinates(longitude, longitude_ref)
    url = f"https://www.google.com/maps?q={decimal_latitude},{decimal_longitude}"
    webbrowser.open_new_tab(url)


with open("1-1.jpg", "rb") as palm_1_file:
    palm_1_image = Image(palm_1_file)
    
with open("1-2.jpg", "rb") as palm_2_file:
    palm_2_image = Image(palm_2_file)
    
images = [palm_1_image, palm_2_image]



for index, image in enumerate(images):
    if image.has_exif:
        status = f"contains EXIF (version) information."
    else:
        status = "does not contain any EXIF information."
    print(f"Image {index} {status}")


image_members = []

for image in images:
    image_members.append(dir(image))

for index, image_member_list in enumerate(image_members):
    print(f"Image {index} contains {len(image_member_list)} members:")
    print(f"{image_member_list}\n")

common_members = set(image_members[0]).intersection(set(image_members[1]))
print(f"Image 0 and Image 1 have {len(common_members)} members in common:")
common_members_sorted = sorted(list(common_members))
print(f"{common_members_sorted}")

for index, image in enumerate(images):
    print(f"Device information - Image {index}")
    print("----------------------------")
    try:
        print(f"Make: {image.make}")
    except:
        print(f"Make: Unknown")

    try:
        print(f"Model: {image.model}\n")
    except:
        print(f"Model: Unknown\n")


    print(f"before xp_keywords: {image.xp_keywords}\n")
    image.delete("xp_keywords")
    print(f"insert\n")
    print (image, dir(image), image.get_all())
    image.insert("xp_keywords", "A,B,C")
    print(f"after xp_keywords: {image.xp_keywords}\n")


    try:
        print(f"gps_latitude: {image.gps_latitude}\n")
    except:
        print(f"gps_latitude: Unknown\n")

    image.delete("gps_latitude")


    try:
        print(f"gps_latitude: {image.gps_latitude}\n")
    except:
        print(f"gps_latitude: Unknown\n")


