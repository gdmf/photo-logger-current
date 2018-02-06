import glob
import os
import piexif
from piexif import ExifIFD
from piexif import GPSIFD


def read(photo_dir):
    """
    Reads a photo exif header
    returns a dict of select fields
    """

    os.chdir(photo_dir)
    extensions = ('.jpg', '.JPG', '.jpeg', '.JPEG')
    files = glob.glob("*")
    files = [f for f in files if os.path.splitext(f)[1] in extensions]

    photo_paths = [os.path.join(photo_dir, photo) for photo in files]

    exif_info = []

    for photo in photo_paths:
        exif_dict = piexif.load(photo)
    # option to grab lat/long, orientation (N/S/E/W), datetime, ID (filename?)
    # from EXIF

        if len(exif_dict['GPS'].keys()) > 0:
            output_dict = {
                # file name
                "Photo File Name": os.path.splitext(
                    os.path.basename(photo))[0],
                # ifd = Exif
                "datetime": exif_dict['Exif'][ExifIFD.DateTimeOriginal],
                # ifd = GPS
                "latitude_ref": exif_dict['GPS'][GPSIFD.GPSLatitudeRef],
                "latitude": exif_dict['GPS'][GPSIFD.GPSLatitude],
                "longitude_ref": exif_dict['GPS'][GPSIFD.GPSLongitudeRef],
                "longitude": exif_dict['GPS'][GPSIFD.GPSLongitude],
                "image_direction_ref": exif_dict['GPS'][
                    GPSIFD.GPSImgDirectionRef],
                "image_direction": exif_dict['GPS'][GPSIFD.GPSImgDirection]}
            exif_info.append(output_dict)

        elif len(exif_dict['Exif'].keys()) > 0:
            output_dict = {
                # file name
                "Photo File Name": os.path.splitext(
                    os.path.basename(photo))[0],
                # ifd = Exif
                "datetime": exif_dict['Exif'][ExifIFD.DateTimeOriginal],
                # ifd = GPS
                "latitude_ref": "No GPS info",
                "latitude": "No GPS info",
                "longitude_ref": "No GPS info",
                "longitude": "No GPS info",
                "image_direction_ref": "No GPS info",
                "image_direction": "No GPS info"
            }
            exif_info.append(output_dict)

        else:
            output_dict = {
                # file name
                "Photo File Name": "No GPS info",
                # ifd = Exif
                "datetime": "No GPS info",
                # ifd = GPS
                "latitude_ref": "No GPS info",
                "latitude": "No GPS info",
                "longitude_ref": "No GPS info",
                "longitude": "No GPS info",
                "image_direction_ref": "No GPS info",
                "image_direction": "No GPS info"
            }
            exif_info.append(output_dict)
    return exif_info
