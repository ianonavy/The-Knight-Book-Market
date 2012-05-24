#!/usr/bin/env python

"""Custom tags and filters for bookmarket templates."""

from django import template
from django.conf import settings
from bookmarket import utils
import locale
import os

__author__ = "Ian Adam Naval"
__copyright__ = "Copyright 2011 Ian Adam Naval"
__credits__ = []

__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Ian Adam Naval"
__email__ = "ianonavy@gmail.com"
__status__ = "Development"
__date__ = "02 September 2011"


register = template.Library()

@register.filter
def title_case(s):
    return utils.title_case(s)


@register.filter()
def currency(value):
    return utils.currency(value)


# Image editing configuration
FORMAT = 'JPEG'
EXTENSION = 'jpg'
QUALITY = 75

def resized_path(path, size, method):
    "Returns the path for the resized image."

    dir, name = os.path.split(path)
    image_name, extension = name.rsplit('.', 1)
    return os.path.join(dir, '%s_%s_%s.%s' % (image_name, method, size,
                                              EXTENSION))


@register.filter
def scale(imagefield, size, method='scale'):
    """Scales an image up or down maintaining the aspect ratio.

    Template filter used to scale an image that will fit inside the defined
    area. The image will scale both up and down, but scaling up tends to make
    tiny images look pixelated. This filter maintains the aspect ratio. If you
    want to resie to an exact dimension, use the "resize" filter.

    The server will only resize it if the image has not already been resized
    with the exact same method.

    Returns the url of the resized image.

    {% load mentaurus_extras %}
    <img src="{{ profile.picture|scale:"48x48" }}" alt="Profile Picture" />
    """

    # imagefield can be a dict with "path" and "url" keys
    if imagefield.__class__.__name__ == 'dict':
        imagefield = type('imageobj', (object,), imagefield)

    image_path = resized_path(imagefield.path, size, method)

    # If the image has not been resized or the original image has been updated,
    if (not os.path.exists(image_path) or
            os.path.getmtime(image_path) <
            os.path.getmtime(imagefield.path)):
        try:
            import Image
        except ImportError:
            try:
                from PIL import Image
            except ImportError:
                raise ImportError('Cannot import the Python Image Library.')

        # Open a new image
        image = Image.open(imagefield.path)

        # Normalize image color mode
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Get the width and height
        width, height = [float(i) for i in size.split('x')]

        # Calculate the new dimensions with the aspect ratio intact if scaling.
        if method == 'scale':
            # Grab the original image's width and height.
            old_ratio = float(imagefield.width) / imagefield.height

            # Calculate new width and height by proportions
            if old_ratio  > width / height:
                # If the floating point aspect ratio of the original image
                # is greater than that of the sizing box, scale the image
                # up or down using width as the maximum size.
                height = width / old_ratio
            else:
                # Otherwise, use height as the maximum size.
                width = height * old_ratio

        width, height = map(round, [width, height])
        width, height = map(int, [width, height])

        # Use the Python Image Library to edit images.
        if method == 'scale' or method == 'resize':
            image = image.resize((width, height), Image.ANTIALIAS)
            image.save(image_path, FORMAT, quality=QUALITY)

        elif method == 'thumbnail':
            image.thumbnail((width, height), Image.ANTIALIAS)
            image.save(image_path, FORMAT, quality=QUALITY)

        elif method == 'crop':
            try:
                import ImageOps
            except ImportError:
                from PIL import ImageOps
            ImageOps.fit(image, (width, height), Image.ANTIALIAS
                        ).save(image_path, FORMAT, quality=QUALITY)

    return resized_path(imagefield.url, size, method)


@register.filter
def crop(imagefield, size):
    """
    Template filter used to crop an image to make it fill the defined area.

    {% load mentaurus_extras %}
    <img src="{{ profile.picture|crop:"48x48" }}" alt="Profile Picture" />

    """
    return scale(imagefield, size, 'crop')


@register.filter
def resize(imagefield, size):
    """
    Template filter used to resize an image without keeping the aspect ratio.

    """
    return scale(imagefield, size, 'resize')


@register.filter
def thumbnail(imagefield, size):
    """
    Template filter used to scale an image down while keeping the aspect
    ratio. Same as the "scale" filter, but only scalese down.

    """
    return scale(imagefield, size, 'thumbnail')
