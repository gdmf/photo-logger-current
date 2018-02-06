import arcpy


def read_fc(fc):
    """
    Read a featureclass and return a list of fieldnames and a list
    of records as dicts.
    """

    def rows_as_dicts(cursor):
        colnames = cursor.fields
        for row in cursor:
            yield dict(zip(colnames, row))

    table = []

    fieldnames = [field.name for field in arcpy.Describe(fc).fields]

    with arcpy.da.SearchCursor(fc, '*') as src:
        for row in rows_as_dicts(src):
            table.append(row)

    return fieldnames, table
