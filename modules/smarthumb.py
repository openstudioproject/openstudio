# -*- coding: utf-8 -*-

from gluon import current
import os
import io
try:
    from PIL import Image
except:
    import Image


 
def SMARTHUMB(image, box, fit=True, name="thumb", field_string=None):
    """
    Downsample the image.
    @param img: Image -  an Image-object
    @param box: tuple(x, y) - the bounding box of the result image
    @param fit: boolean - crop the image to fill the box
    """
    if image:
        db = current.db
        field = _get_db_field(field_string)
        request = current.request
        img = Image.open(os.path.join(request.folder, 'uploads', image))
        #preresize image with factor 2, 4, 8 and fast algorithm
        factor = 1
        while img.size[0] / factor > 2 * box[0] and img.size[1] * 2 / factor > 2 * box[1]:
            factor *= 2
        if factor > 1:
            img.thumbnail((img.size[0] / factor, img.size[1] / factor), Image.NEAREST)
 
        #calculate the cropping box and get the cropped part
        if fit:
            x1 = y1 = 0
            x2, y2 = img.size
            wRatio = 1.0 * x2 / box[0]
            hRatio = 1.0 * y2 / box[1]
            if hRatio > wRatio:
                y1 = int(y2 / 2 - box[1] * wRatio / 2)
                y2 = int(y2 / 2 + box[1] * wRatio / 2)
            else:
                x1 = int(x2 / 2 - box[0] * hRatio / 2)
                x2 = int(x2 / 2 + box[0] * hRatio / 2)
            img = img.crop((x1, y1, x2, y2))
 
        #Resize the image with best quality algorithm ANTI-ALIAS
        img.thumbnail(box, Image.ANTIALIAS)

        # Fetch extension
        root, ext = os.path.splitext(image)
        if ext.lower() == '.jpg' or ext.lower() == ".jpeg":
            format = "JPEG"
        else:
            format = "PNG"

        # Save image in memory
        temp_stream = io.BytesIO()
        img.save(temp_stream, format=format)

        # Set new file name
        filename = '%s%s' % (name, ext)
        # Get db field value
        filevalue = field.store(temp_stream, filename)
        # write file to disk
        new_file_path = os.path.join(request.folder, 'uploads', filevalue)
        img.save(new_file_path)

        return filevalue


def _get_db_field(field_string=None):
    db = current.db

    if field_string == "auth_user.thumbsmall":
        return db.auth_user.thumbsmall
    elif field_string == "auth_user.thumblarge":
        return db.auth_user.thumblarge
    elif field_string == "school_classtypes.thumbsmall":
        return db.school_classtypes.thumbsmall
    elif field_string == "school_classtypes.thumblarge":
        return db.school_classtypes.thumblarge
    elif field_string == "shop_products.thumbsmall":
        return db.shop_products.thumbsmall
    elif field_string == "shop_products.thumblarge":
        return db.shop_products.thumblarge
    elif field_string == "shop_products_variants.thumbsmall":
        return db.shop_products_variants.thumbsmall
    elif field_string == "shop_products_variants.thumblarge":
        return db.shop_products_variants.thumblarge
    elif field_string == "workshops.thumbsmall":
        return db.workshops.thumbsmall
    elif field_string == "workshops.thumblarge":
        return db.workshops.thumblarge
    elif field_string == "workshops.thumbsmall_2":
        return db.workshops.thumbsmall_2
    elif field_string == "workshops.thumblarge_2":
        return db.workshops.thumblarge_2
    elif field_string == "workshops.thumbsmall_3":
        return db.workshops.thumbsmall_3
    elif field_string == "workshops.thumblarge_3":
        return db.workshops.thumblarge_3
    elif field_string == "workshops.thumbsmall_4":
        return db.workshops.thumbsmall_4
    elif field_string == "workshops.thumblarge_4":
        return db.workshops.thumblarge_4
    elif field_string == "workshops.thumbsmall_5":
        return db.workshops.thumbsmall_5
    elif field_string == "workshops.thumblarge_5":
        return db.workshops.thumblarge_5

    else:
        raise ValueError('Field string was not mapped to db table in SMARTTHUMB function')
