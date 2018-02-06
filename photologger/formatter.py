import datetime
import decimal


def date_formatter(date):

    # pyshp format
    # year, month, day = tuple(date)
    # return "{}/{}/{}".format(month, day, year)

    # arcpy format
    fmt = '%m/%d/%Y %H:%M:%S'
    return date.strftime(fmt)


def coord_formatter(coord):
    return str(coord)


def datetime_from_exif_header(date):
    # argument format: '2016:01:03 20:49:20'
    date_part = date.split()[0]
    time_part = date.split()[1]
    y, m, d = date_part.split(':')
    h, minute, s = time_part.split(':')
    timestamp = datetime.datetime(
        int(y), int(m), int(d),
        int(h), int(minute), int(s))
    fmt = '%m/%d/%Y %H:%M:%S'
    return timestamp.strftime(fmt)


def dd_from_exif_coord(coord, coord_ref):
    if coord == "No GPS info":
        return "No GPS info"
    else:
        # argument format ((19, 1), (55, 1), (5007, 100)), 'N'
        if coord_ref in ['W', 'S']:
            cardinal_dir = -1
        else:
            cardinal_dir = 1

        d, m, s = coord
        d = d[0] / d[1]
        m = m[0] / m[1]
        s = float(s[0]) / s[1]
        return (d + float(m) / 60 + s / 3600) * cardinal_dir


def bearing_from_exif_image_direction(image_direction, image_direction_ref):
    if image_direction == "No GPS info":
        return "No GPS info"
    else:
        direction_ref = {'T': 'True', 'M': 'Magnetic'}
        direction_type = direction_ref[image_direction_ref]
        bearing, divisor = image_direction
        bearing = decimal.Decimal(bearing)
        return "{} ({})".format(bearing / divisor, direction_type)
