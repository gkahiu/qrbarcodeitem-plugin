# -*- coding: utf-8 -*-
#
# Copyright (c) 2016 - 2020 -- Lars Heuer
# All rights reserved.
#
# License: BSD License
#
"""\
Standard serializers and utility functions for serializers.

DOES NOT belong to the public API.

The serializers are independent of the :py:class:`segno.QRCode` (and the
:py:class:`segno.encoder.Code`) class; they just need a matrix (tuple of
bytearrays) and the version constant.
"""
from __future__ import absolute_import, unicode_literals, division
import io
import re
import zlib
import codecs
import base64
import gzip
from xml.sax.saxutils import quoteattr, escape
from struct import pack
from itertools import chain, repeat
import functools
from functools import partial
from functools import reduce
from operator import itemgetter
from contextlib import contextmanager
from collections import defaultdict
import time
_PY2 = False
try:  # pragma: no cover
    from itertools import zip_longest
    from urllib.parse import quote
except ImportError:  # pragma: no cover
    _PY2 = True
    from itertools import izip_longest as zip_longest
    from urllib import quote
    range = xrange
    str = unicode
    from io import open
from . import consts
from .utils import matrix_to_lines, get_symbol_size, get_border, \
        check_valid_scale, check_valid_border, matrix_iter, matrix_iter_verbose

__all__ = ('writable', 'write_svg', 'write_png', 'write_eps', 'write_pdf',
           'write_txt', 'write_pbm', 'write_pam', 'write_ppm', 'write_xpm',
           'write_xbm', 'write_tex', 'write_terminal')

# Standard creator name
CREATOR = 'Segno <https://pypi.org/project/segno/>'


@contextmanager
def writable(file_or_path, mode, encoding=None):
    """\
    Returns a writable file-like object.

    Usage::

        with writable(file_name_or_path, 'wb') as f:
            ...


    :param file_or_path: Either a file-like object or a filename.
    :param str mode: String indicating the writing mode (i.e. ``'wb'``)
    """
    f = file_or_path
    must_close = False
    try:
        file_or_path.write
        if encoding is not None:
            f = codecs.getwriter(encoding)(file_or_path)
    except AttributeError:
        f = open(file_or_path, mode, encoding=encoding)
        must_close = True
    try:
        yield f
    finally:
        if must_close:
            f.close()


def colorful(dark, light):
    """\
    Decorator to inject a module type -> color mapping into the decorated function.
    """
    def decorate(f):
        @functools.wraps(f)
        def wrapper(matrix, version, out, dark=dark, light=light, finder_dark=False, finder_light=False,
                    data_dark=False, data_light=False, version_dark=False, version_light=False,
                    format_dark=False, format_light=False, alignment_dark=False, alignment_light=False,
                    timing_dark=False, timing_light=False, separator=False, dark_module=False,
                    quiet_zone=False, **kw):
            cm = _make_colormap(version, dark=dark, light=light, finder_dark=finder_dark,
                                finder_light=finder_light, data_dark=data_dark,
                                data_light=data_light, version_dark=version_dark,
                                version_light=version_light, format_dark=format_dark,
                                format_light=format_light, alignment_dark=alignment_dark,
                                alignment_light=alignment_light, timing_dark=timing_dark,
                                timing_light=timing_light, separator=separator,
                                dark_module=dark_module, quiet_zone=quiet_zone)
            return f(matrix, version, out, cm, **kw)
        if _PY2:  # pragma: no cover
            wrapper.__wrapped__ = f  # Needed by CLI to inspect the arguments
        return wrapper
    return decorate


def _valid_width_height_and_border(version, scale, border):
    """"\
    Validates the scale and border and returns the width, height and the border.
    If the border is ``None´` the default border is returned.
    """
    check_valid_scale(scale)
    check_valid_border(border)
    border = get_border(version, border)
    width, height = get_symbol_size(version, scale, border)
    return width, height, border


@colorful(dark='#000', light=None)
def write_svg(matrix, version, out, colormap, scale=1, border=None, xmldecl=True,
              svgns=True, title=None, desc=None, svgid=None, svgclass='segno',
              lineclass='qrline', omitsize=False, unit=None, encoding='utf-8',
              svgversion=None, nl=True, draw_transparent=False):
    """\
    Serializes the QR code as SVG document.

    :param matrix: The matrix to serialize.
    :param int version: The (Micro) QR code version
    :param out: Filename or a file-like object supporting to write bytes.
    :param scale: Indicates the size of a single module (default: 1 which
            corresponds to 1 x 1 pixel per module).
    :param int border: Integer indicating the size of the quiet zone.
            If set to ``None`` (default), the recommended border size
            will be used (``4`` for QR Codes, ``2`` for a Micro QR Codes).
    :param bool xmldecl: Inidcates if the XML declaration header should be
            written (default: ``True``)
    :param bool svgns: Indicates if the SVG namespace should be written
            (default: ``True``).
    :param str title: Optional title of the generated SVG document.
    :param str desc: Optional description of the generated SVG document.
    :param svgid: The ID of the SVG document (if set to ``None`` (default),
            the SVG element won't have an ID).
    :param svgclass: The CSS class of the SVG document
            (if set to ``None``, the SVG element won't have a class).
    :param lineclass: The CSS class of the path element (which draws the
            "black" modules (if set to ``None``, the path won't have a class).
    :param bool omitsize: Indicates if width and height attributes should be
            omitted (default: ``False``). If these attributes are omitted,
            a ``viewBox`` attribute will be added to the document.
    :param str unit: Unit for width / height and other coordinates.
            By default, the unit is unspecified and all values are
            in the user space.
            Valid values: em, ex, px, pt, pc, cm, mm, in, and percentages
    :param str encoding: Encoding of the XML document. "utf-8" by default.
    :param float svgversion: SVG version (default: None)
    :param bool nl: Indicates if the document should have a trailing newline
            (default: ``True``)
    :param bool draw_transparent: Indicates if transparent SVG paths should be
            added to the graphic (default: ``False``)
    """
    def svg_color(clr):
        return _color_to_webcolor(clr, allow_css3_colors=allow_css3_colors) if clr is not None else None

    def matrix_to_lines_verbose():
        j = -.5  # stroke width / 2
        invalid_color = -1
        for row in matrix_iter_verbose(matrix, version, scale=1, border=border):
            last_color = invalid_color
            x1, x2 = 0, 0
            j += 1
            for c in (colormap[mt] for mt in row):
                if last_color != invalid_color and last_color != c:
                    yield last_color, (x1, x2, j)
                    x1 = x2
                x2 += 1
                last_color = c
            yield last_color, (x1, x2, j)

    width, height, border = _valid_width_height_and_border(version, scale, border)
    unit = unit or ''
    if unit and omitsize:
        raise ValueError('The unit "{}" has no effect if the size '
                         '(width and height) is omitted.'.format(unit))
    omit_encoding = encoding is None
    if omit_encoding:
        encoding = 'utf-8'
    allow_css3_colors = svgversion is not None and svgversion >= 2.0
    is_multicolor = len(set(colormap.values())) > 2
    need_background = not is_multicolor and colormap[consts.TYPE_QUIET_ZONE] is not None and not draw_transparent
    need_svg_group = scale != 1 and (need_background or is_multicolor)
    if is_multicolor:
        miter = matrix_to_lines_verbose()
    else:
        x, y = border, border + .5
        dark = colormap[consts.TYPE_DATA_DARK]
        miter = ((dark, (x1, x2, y1)) for (x1, y1), (x2, y2) in matrix_to_lines(matrix, x, y))
    xy = defaultdict(lambda: (0, 0))
    coordinates = defaultdict(list)
    for clr, (x1, x2, y1) in miter:
        x, y = xy[clr]
        coordinates[clr].append((x1 - x, y1 - y, x2 - x1))
        xy[clr] = x2, y1
    if need_background:
        # Add an additional path for the background, will be modified after
        # the SVG paths have been generated
        coordinates[colormap[consts.TYPE_QUIET_ZONE]] = [(0, 0, width // scale)]
    if not draw_transparent:
        try:
            del coordinates[None]
        except KeyError:
            pass
    paths = {}
    scale_info = ' transform="scale({})"'.format(scale) if scale != 1 else ''
    p = '<path{}{}'.format(scale_info if not need_svg_group else '',
                           '' if not lineclass else ' class={}'.format(quoteattr(lineclass)))
    for color, coord in coordinates.items():
        path = p
        clr = svg_color(color)
        if clr is not None:
            opacity = None
            if isinstance(clr, tuple):
                clr, opacity = clr
            path += ' stroke={}'.format(quoteattr(clr))
            if opacity is not None:
                path += ' stroke-opacity={}'.format(quoteattr(str(opacity)))
        path += ' d="'
        path += ''.join('{moveto}{x} {y}h{l}'.format(moveto=('m' if i > 0 else 'M'),
                                                     x=x, l=length,
                                                     y=(int(y) if int(y) == y else y))
                        for i, (x, y, length) in enumerate(coord))
        path += '"/>'
        paths[color] = path
    if need_background:
        # This code is necessary since the path was generated by the loop above
        # but the background path is special: It has no stroke- but a fill-color
        # and it needs to be closed. Further, it has no class attribute.
        k = colormap[consts.TYPE_QUIET_ZONE]
        paths[k] = re.sub(r'\sclass="[^"]+"', '',
                          paths[k].replace('stroke', 'fill')
                                  .replace('"/>', 'v{0}h-{1}z"/>'.format(height // scale, width // scale)))
    svg = ''
    if xmldecl:
        svg += '<?xml version="1.0"'
        if not omit_encoding:
            svg += ' encoding={}'.format(quoteattr(encoding))
        svg += '?>\n'
    svg += '<svg'
    if svgns:
        svg += ' xmlns="http://www.w3.org/2000/svg"'
    if svgversion is not None and svgversion < 2.0:
        svg += ' version={}'.format(quoteattr(str(svgversion)))
    if not omitsize:
        svg += ' width="{0}{2}" height="{1}{2}"'.format(width, height, unit)
    if omitsize or unit:
        svg += ' viewBox="0 0 {} {}"'.format(width, height)
    if svgid:
        svg += ' id={}'.format(quoteattr(svgid))
    if svgclass:
        svg += ' class={}'.format(quoteattr(svgclass))
    svg += '>'
    if title is not None:
        svg += '<title>{}</title>'.format(escape(title))
    if desc is not None:
        svg += '<desc>{}</desc>'.format(escape(desc))
    if need_svg_group:
        svg += '<g{}>'.format(scale_info)
    svg += ''.join(sorted(paths.values(), key=len))
    if need_svg_group:
        svg += '</g>'
    svg += '</svg>'
    if nl:
        svg += '\n'
    with writable(out, 'wt', encoding=encoding) as f:
        f.write(svg)


_replace_quotes = partial(re.compile(br'(=)"([^"]+)"').sub, br"\1'\2'")

def as_svg_data_uri(matrix, version, scale=1, border=None,
                    xmldecl=False, svgns=True, title=None,
                    desc=None, svgid=None, svgclass='segno',
                    lineclass='qrline', omitsize=False, unit='',
                    encoding='utf-8', svgversion=None, nl=False,
                    encode_minimal=False, omit_charset=False, **kw):
    """\
    Converts the matrix to a SVG data URI.

    The XML declaration is omitted by default (set ``xmldecl`` to ``True``
    to enable it), further the newline is omitted by default (set ``nl`` to
    ``True`` to enable it).

    Aside from the missing ``out`` parameter and the different ``xmldecl``
    and ``nl`` default values and the additional parameter ``encode_minimal``
    and ``omit_charset`` this function uses the same parameters as the
    usual SVG serializer.

    :param bool encode_minimal: Indicates if the resulting data URI should
                    use minimal percent encoding (disabled by default).
    :param bool omit_charset: Indicates if the ``;charset=...`` should be omitted
                    (disabled by default)
    :rtype: str
    """
    encode = partial(quote, safe=b"") if not encode_minimal else partial(quote, safe=b" :/='")
    buff = io.BytesIO()
    write_svg(matrix, version, buff, scale=scale, border=border, xmldecl=xmldecl,
              svgns=svgns, title=title, desc=desc, svgclass=svgclass,
              lineclass=lineclass, omitsize=omitsize, encoding=encoding,
              svgid=svgid, unit=unit, svgversion=svgversion, nl=nl, **kw)
    return 'data:image/svg+xml{0},{1}' \
                .format(';charset=' + encoding if not omit_charset else '',
                        # Replace " quotes with ' and URL encode the result
                        # See also https://codepen.io/tigt/post/optimizing-svgs-in-data-uris
                        encode(_replace_quotes(buff.getvalue())))


def write_svg_debug(matrix, version, out, scale=15, border=None,
                    fallback_color='fuchsia', colormap=None,
                    add_legend=True):  # pragma: no cover
    """\
    Internal SVG serializer which is useful for debugging purposes.

    This function is not exposed to the QRCode class by intention and the
    resulting SVG document is very inefficient (a lot of ``<rect/>`` elements).
    Dark modules are black and light modules are white by default. Provide
    a custom `colormap` to override these defaults.
    Unknown modules are red by default.

    :param matrix: The matrix
    :param version: Version constant
    :param out: binary file-like object or file name
    :param scale: Scaling factor
    :param border: Quiet zone
    :param fallback_color: Color which is used for modules which are not 0x0 or 0x1
                and for which no entry in `color_mapping` is defined.
    :param colormap: dict of module values to color mapping (optional)
    :param bool add_legend: Indicates if the bit values should be added to the
                matrix (default: True)
    """
    clr_mapping = {
        0x0: '#fff',
        0x1: '#000',
        0x2: 'red',
        0x3: 'orange',
        0x4: 'gold',
        0x5: 'green',
    }
    if colormap is not None:
        clr_mapping.update(colormap)
    width, height, border = _valid_width_height_and_border(version, scale, border)
    matrix_size = get_symbol_size(version, scale=1, border=0)[0]
    with writable(out, 'wt', encoding='utf-8') as f:
        legend = []
        write = f.write
        write('<?xml version="1.0" encoding="utf-8"?>\n')
        write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {0} {1}">'.format(width, height))
        write('<style type="text/css"><![CDATA[ text { font-size: 1px; font-family: Helvetica, Arial, sans; } ]]></style>')
        write('<g transform="scale({0})">'.format(scale))
        for i in range(matrix_size):
            y = i + border
            for j in range(matrix_size):
                x = j + border
                bit = matrix[i][j]
                if add_legend and bit not in (0x0, 0x1):
                    legend.append((x, y, bit))
                fill = clr_mapping.get(bit, fallback_color)
                write('<rect x="{0}" y="{1}" width="1" height="1" fill="{2}"/>'.format(x, y, fill))
        # legend may be empty if add_legend == False
        for x, y, val in legend:
            write('<text x="{0}" y="{1}">{2}</text>'.format(x+.2, y+.9, val))
        write('</g></svg>\n')


def _color_to_rgb_or_rgba(color, alpha_float=True):
    """\
    Returns the provided color as ``(R, G, B)`` or ``(R, G, B, A)`` tuple.

    If the alpha value is opaque, an RGB tuple is returned, otherwise an RGBA
    tuple.

    :param color: A web color name (i.e. ``darkblue``) or a hexadecimal value
            (``#RGB`` or ``#RRGGBB``) or a RGB(A) tuple (i.e. ``(R, G, B)`` or
            ``(R, G, B, A)``)
    :param bool alpha_float: Indicates if the alpha value should be returned as
            float value. If ``False``, the alpha value is an integer value in
            the range of ``0 .. 254``.
    :rtype: tuple
    """
    rgba = _color_to_rgba(color, alpha_float=alpha_float)
    if rgba[3] in (1.0, 255):
        return rgba[:3]
    return rgba


def _color_to_webcolor(color, allow_css3_colors=True, optimize=True):
    """\
    Returns either a hexadecimal code or a color name.

    :param color: A web color name (i.e. ``darkblue``) or a hexadecimal value
            (``#RGB`` or ``#RRGGBB``) or a RGB(A) tuple (i.e. ``(R, G, B)`` or
            ``(R, G, B, A)``)
    :param bool allow_css3_colors: Indicates if a CSS3 color value like
            rgba(R G, B, A) is an acceptable result.
    :param bool optimize: Inidcates if the shortest possible color value should
            be returned (default: ``True``).
    :rtype: str
    :return: The provided color as web color: ``#RGB``, ``#RRGGBB``,
            ``rgba(R, G, B, A)``, or web color name.
    """
    if _color_is_black(color):
        return '#000'
    elif _color_is_white(color):
        return '#fff'
    clr = _color_to_rgb_or_rgba(color)
    alpha_channel = None
    if len(clr) == 4:
        if allow_css3_colors:
            return 'rgba({0},{1},{2},{3})'.format(*clr)
        alpha_channel = clr[3]
        clr = clr[:3]
    hx = '#{0:02x}{1:02x}{2:02x}'.format(*clr)
    if optimize:
        if hx == '#d2b48c':
            hx = 'tan'  # shorter
        elif hx == '#ff0000':
            hx = 'red'  # shorter
        elif hx[1] == hx[2] and hx[3] == hx[4] and hx[5] == hx[6]:
            hx = '#{0}{1}{2}'.format(hx[1], hx[3], hx[5])
    return hx if alpha_channel is None else (hx, alpha_channel)


def color_to_rgb_hex(color):
    """\
    Returns the provided color in hexadecimal representation.

    :param color: A web color name (i.e. ``darkblue``) or a hexadecimal value
            (``#RGB`` or ``#RRGGBB``) or a RGB(A) tuple (i.e. ``(R, G, B)`` or
            ``(R, G, B, A)``)
    :returns: ``#RRGGBB``.
    """
    return '#{0:02x}{1:02x}{2:02x}'.format(*_color_to_rgb(color))


def _color_is_black(color):
    """\
    Returns if the provided color represents "black".

    :param color: A web color name (i.e. ``darkblue``) or a hexadecimal value
            (``#RGB`` or ``#RRGGBB``) or a RGB(A) tuple (i.e. ``(R, G, B)`` or
            ``(R, G, B, A)``)
    :return: ``True`` if color is represents black, otherwise ``False``.
    """
    try:
        color = color.lower()
    except AttributeError:
        pass
    return color in ('#000', '#000000', 'black', (0, 0, 0), (0, 0, 0, 255),
                     (0, 0, 0, 1.0))


def _color_is_white(color):
    """\
    Returns if the provided color represents "black".

    :param color: A web color name (i.e. ``darkblue``) or a hexadecimal value
            (``#RGB`` or ``#RRGGBB``) or a RGB(A) tuple (i.e. ``(R, G, B)`` or
            ``(R, G, B, A)``)
    :return: ``True`` if color is represents white, otherwise ``False``.
    """
    try:
        color = color.lower()
    except AttributeError:
        pass
    return color in ('#fff', '#ffffff', 'white', (255, 255, 255),
                     (255, 255, 255, 255), (255, 255, 255, 1.0))


def _color_to_rgb(color):
    """\
    Converts web color names like "red" or hexadecimal values like "#36c",
    "#FFFFFF" and RGB tuples like ``(255, 255 255)`` into a (R, G, B) tuple.

    :param color: A web color name (i.e. ``darkblue``) or a hexadecimal value
            (``#RGB`` or ``#RRGGBB``) or a RGB tuple (i.e. ``(R, G, B)``))
    :return: ``(R, G, B)`` tuple.
    """
    rgb = _color_to_rgb_or_rgba(color)
    if len(rgb) != 3:
        raise ValueError('The alpha channel {0} in color "{1}" cannot be '
                         'converted to RGB'.format(rgb[3], color))
    return rgb


def _color_to_rgba(color, alpha_float=True):
    """\
    Returns a (R, G, B, A) tuple.

    :param color: A web color name (i.e. ``darkblue``) or a hexadecimal value
            (``#RGB`` or ``#RRGGBB``) or a RGB(A) tuple (i.e. ``(R, G, B)`` or
            ``(R, G, B, A)``)
    :param bool alpha_float: Indicates if the alpha value should be returned as
            float value. If ``False``, the alpha value is an integer value in
            the range of ``0 .. 254``.
    :return: ``(R, G, B, A)`` tuple.
    """
    res = []
    alpha_channel = (1.0,) if alpha_float else (255,)
    if isinstance(color, tuple):
        col_length = len(color)
        is_valid = False
        if 3 <= col_length <= 4:
            for i, part in enumerate(color[:3]):
                is_valid = 0 <= part <= 255
                res.append(part)
                if not is_valid or i == 2:
                    break
            if is_valid:
                if col_length == 4:
                    res.append(_alpha_value(color[3], alpha_float))
                else:
                    res.append(alpha_channel[0])
        if is_valid:
            return tuple(res)
        raise ValueError('Unsupported color "{0}"'.format(color))
    try:
        return _NAME2RGB[color.lower()] + alpha_channel
    except KeyError:
        try:
            clr = _hex_to_rgb_or_rgba(color, alpha_float=alpha_float)
            if len(clr) == 4:
                return clr
            else:
                return clr + alpha_channel
        except ValueError:
            raise ValueError('Unsupported color "{0}". Neither a known web '
                             'color name nor a color in hexadecimal format.'
                             .format(color))


def _hex_to_rgb_or_rgba(color, alpha_float=True):
    """\
    Helper function to convert a color provided in hexadecimal format (``#RGB``
    or ``#RRGGBB``) to a RGB(A) tuple.

    :param str color: Hexadecimal color name.
    :param bool alpha_float: Indicates if the alpha value should be returned as
            float value. If ``False``, the alpha value is an integer value in
            the range of ``0 .. 254``.
    :return: Tuple of integer values representing a RGB(A) color.
    :rtype: tuple
    :raises: :py:exc:`ValueError` in case the provided string could not
                converted into a RGB(A) tuple
    """
    if color[0] == '#':
        color = color[1:]
    if 2 < len(color) < 5:
        # Expand RGB -> RRGGBB and RGBA -> RRGGBBAA
        color = ''.join([color[i] * 2 for i in range(len(color))])
    color_len = len(color)
    if color_len not in (6, 8):
        raise ValueError('Input #{0} is not in #RRGGBB nor in #RRGGBBAA format'.format(color))
    res = tuple([int(color[i:i+2], 16) for i in range(0, color_len, 2)])
    if alpha_float and color_len == 8:
        res = res[:3] + (_alpha_value(res[3], alpha_float),)
    return res


_ALPHA_COMMONS = {255: 1.0, 128: .5, 64: .25, 32: .125, 16: .625, 0: 0.0}

def _alpha_value(color, alpha_float):
    if alpha_float:
        if not isinstance(color, float):
            if 0 <= color <= 255:
                return _ALPHA_COMMONS.get(color, float('%.02f' % (color / 255.0)))
        else:
            if 0 <= color <= 1.0:
                return color
    else:
        if not isinstance(color, float):
            if 0 <= color <= 255:
                return color
        else:
            if 0 <= color <= 1.0:
                return color * 255.0
    raise ValueError('Invalid alpha channel value: {0}'.format(color))


def _invert_color(rgb_or_rgba):
    """\
    Returns the inverse color for the provided color.

    This function does not check if the color is a valid RGB / RGBA color.

    :param rgb: (R, G, B) or (R, G, B, A) tuple.
    """
    return tuple([255 - c for c in rgb_or_rgba])


# <http://www.w3.org/TR/css3-color/#svg-color>
_NAME2RGB = {
    'aliceblue': (240, 248, 255),
    'antiquewhite': (250, 235, 215),
    'aqua': (0, 255, 255),
    'aquamarine': (127, 255, 212),
    'azure': (240, 255, 255),
    'beige': (245, 245, 220),
    'bisque': (255, 228, 196),
    'black': (0, 0, 0),
    'blanchedalmond': (255, 235, 205),
    'blue': (0, 0, 255),
    'blueviolet': (138, 43, 226),
    'brown': (165, 42, 42),
    'burlywood': (222, 184, 135),
    'cadetblue': (95, 158, 160),
    'chartreuse': (127, 255, 0),
    'chocolate': (210, 105, 30),
    'coral': (255, 127, 80),
    'cornflowerblue': (100, 149, 237),
    'cornsilk': (255, 248, 220),
    'crimson': (220, 20, 60),
    'cyan': (0, 255, 255),
    'darkblue': (0, 0, 139),
    'darkcyan': (0, 139, 139),
    'darkgoldenrod': (184, 134, 11),
    'darkgray': (169, 169, 169),
    'darkgreen': (0, 100, 0),
    'darkgrey': (169, 169, 169),
    'darkkhaki': (189, 183, 107),
    'darkmagenta': (139, 0, 139),
    'darkolivegreen': (85, 107, 47),
    'darkorange': (255, 140, 0),
    'darkorchid': (153, 50, 204),
    'darkred': (139, 0, 0),
    'darksalmon': (233, 150, 122),
    'darkseagreen': (143, 188, 143),
    'darkslateblue': (72, 61, 139),
    'darkslategray': (47, 79, 79),
    'darkslategrey': (47, 79, 79),
    'darkturquoise': (0, 206, 209),
    'darkviolet': (148, 0, 211),
    'deeppink': (255, 20, 147),
    'deepskyblue': (0, 191, 255),
    'dimgray': (105, 105, 105),
    'dimgrey': (105, 105, 105),
    'dodgerblue': (30, 144, 255),
    'firebrick': (178, 34, 34),
    'floralwhite': (255, 250, 240),
    'forestgreen': (34, 139, 34),
    'fuchsia': (255, 0, 255),
    'gainsboro': (220, 220, 220),
    'ghostwhite': (248, 248, 255),
    'gold': (255, 215, 0),
    'goldenrod': (218, 165, 32),
    'gray': (128, 128, 128),
    'green': (0, 128, 0),
    'greenyellow': (173, 255, 47),
    'grey': (128, 128, 128),
    'honeydew': (240, 255, 240),
    'hotpink': (255, 105, 180),
    'indianred': (205, 92, 92),
    'indigo': (75, 0, 130),
    'ivory': (255, 255, 240),
    'khaki': (240, 230, 140),
    'lavender': (230, 230, 250),
    'lavenderblush': (255, 240, 245),
    'lawngreen': (124, 252, 0),
    'lemonchiffon': (255, 250, 205),
    'lightblue': (173, 216, 230),
    'lightcoral': (240, 128, 128),
    'lightcyan': (224, 255, 255),
    'lightgoldenrodyellow': (250, 250, 210),
    'lightgray': (211, 211, 211),
    'lightgreen': (144, 238, 144),
    'lightgrey': (211, 211, 211),
    'lightpink': (255, 182, 193),
    'lightsalmon': (255, 160, 122),
    'lightseagreen': (32, 178, 170),
    'lightskyblue': (135, 206, 250),
    'lightslategray': (119, 136, 153),
    'lightslategrey': (119, 136, 153),
    'lightsteelblue': (176, 196, 222),
    'lightyellow': (255, 255, 224),
    'lime': (0, 255, 0),
    'limegreen': (50, 205, 50),
    'linen': (250, 240, 230),
    'magenta': (255, 0, 255),
    'maroon': (128, 0, 0),
    'mediumaquamarine': (102, 205, 170),
    'mediumblue': (0, 0, 205),
    'mediumorchid': (186, 85, 211),
    'mediumpurple': (147, 112, 219),
    'mediumseagreen': (60, 179, 113),
    'mediumslateblue': (123, 104, 238),
    'mediumspringgreen': (0, 250, 154),
    'mediumturquoise': (72, 209, 204),
    'mediumvioletred': (199, 21, 133),
    'midnightblue': (25, 25, 112),
    'mintcream': (245, 255, 250),
    'mistyrose': (255, 228, 225),
    'moccasin': (255, 228, 181),
    'navajowhite': (255, 222, 173),
    'navy': (0, 0, 128),
    'oldlace': (253, 245, 230),
    'olive': (128, 128, 0),
    'olivedrab': (107, 142, 35),
    'orange': (255, 165, 0),
    'orangered': (255, 69, 0),
    'orchid': (218, 112, 214),
    'palegoldenrod': (238, 232, 170),
    'palegreen': (152, 251, 152),
    'paleturquoise': (175, 238, 238),
    'palevioletred': (219, 112, 147),
    'papayawhip': (255, 239, 213),
    'peachpuff': (255, 218, 185),
    'peru': (205, 133, 63),
    'pink': (255, 192, 203),
    'plum': (221, 160, 221),
    'powderblue': (176, 224, 230),
    'purple': (128, 0, 128),
    'red': (255, 0, 0),
    'rosybrown': (188, 143, 143),
    'royalblue': (65, 105, 225),
    'saddlebrown': (139, 69, 19),
    'salmon': (250, 128, 114),
    'sandybrown': (244, 164, 96),
    'seagreen': (46, 139, 87),
    'seashell': (255, 245, 238),
    'sienna': (160, 82, 45),
    'silver': (192, 192, 192),
    'skyblue': (135, 206, 235),
    'slateblue': (106, 90, 205),
    'slategray': (112, 128, 144),
    'slategrey': (112, 128, 144),
    'snow': (255, 250, 250),
    'springgreen': (0, 255, 127),
    'steelblue': (70, 130, 180),
    'tan': (210, 180, 140),
    'teal': (0, 128, 128),
    'thistle': (216, 191, 216),
    'tomato': (255, 99, 71),
    'turquoise': (64, 224, 208),
    'violet': (238, 130, 238),
    'wheat': (245, 222, 179),
    'white': (255, 255, 255),
    'whitesmoke': (245, 245, 245),
    'yellow': (255, 255, 0),
    'yellowgreen': (154, 205, 50),
}


def _make_colormap(version, dark, light,
                   finder_dark=False, finder_light=False,
                   data_dark=False, data_light=False,
                   version_dark=False, version_light=False,
                   format_dark=False, format_light=False,
                   alignment_dark=False, alignment_light=False,
                   timing_dark=False, timing_light=False,
                   separator=False, dark_module=False,
                   quiet_zone=False):
    """\
    Creates and returns a module type -> color map.

    The result can be used for serializers which support more than two colors.

    Examples

    .. code-block:: python

        # All dark modules (data, version, ...) will be dark red, the dark
        # modules of the finder patterns will be blue
        # The light modules will be rendered in the serializer's default color
        # (usually white)
        cm = colormap(dark='darkred', finder_dark='blue')

        # Use the serializer's default colors for dark / light modules
        # (usually black and white) but the dark modules of the timing patterns
        # will be brown
        cm = colormap(timing_dark=(165, 42, 42))

    :param version: QR Code version (int constant)
    :param dark: Default color of dark modules
    :param light: Default color of light modules
    :param finder_dark: Color of the dark modules of the finder patterns.
    :param finder_light: Color of the light modules of the finder patterns.
    :param data_dark: Color of the dark data modules.
    :param data_light: Color of the light data modules.
    :param version_dark: Color of the dark modules of the version information.
    :param version_light: Color of the light modules of the version information.
    :param format_dark: Color of the dark modules of the format information.
    :param format_light: Color of the light modules of the format information.
    :param alignment_dark: Color of the dark modules of the alignment patterns.
    :param alignment_light: Color of the light modules of the alignment patterns.
    :param timing_dark: Color of the dark modules of the timing patterns.
    :param timing_light: Color of the light modules of the timing patterns.
    :param separator: Color of the separator.
    :param dark_module: Color of the dark module.
    :param quiet_zone: Color of the quiet zone / border.
    :rtype: dict
    """
    unsupported = ()
    if version < 7:
        unsupported = [consts.TYPE_VERSION_DARK, consts.TYPE_VERSION_LIGHT]
        if version < 1:  # Micro QR Code
            unsupported.extend([consts.TYPE_DARKMODULE,
                                consts.TYPE_ALIGNMENT_PATTERN_DARK,
                                consts.TYPE_ALIGNMENT_PATTERN_LIGHT])
    mt2color = {
        consts.TYPE_FINDER_PATTERN_DARK: finder_dark if finder_dark is not False else dark,
        consts.TYPE_FINDER_PATTERN_LIGHT: finder_light if finder_light is not False else light,
        consts.TYPE_DATA_DARK: data_dark if data_dark is not False else dark,
        consts.TYPE_DATA_LIGHT: data_light if data_light is not False else light,
        consts.TYPE_VERSION_DARK: version_dark if version_dark is not False else dark,
        consts.TYPE_VERSION_LIGHT: version_light if version_light is not False else light,
        consts.TYPE_ALIGNMENT_PATTERN_DARK: alignment_dark if alignment_dark is not False else dark,
        consts.TYPE_ALIGNMENT_PATTERN_LIGHT: alignment_light if alignment_light is not False else light,
        consts.TYPE_TIMING_DARK: timing_dark if timing_dark is not False else dark,
        consts.TYPE_TIMING_LIGHT: timing_light if timing_light is not False else light,
        consts.TYPE_FORMAT_DARK: format_dark if format_dark is not False else dark,
        consts.TYPE_FORMAT_LIGHT: format_light if format_light is not False else light,
        consts.TYPE_SEPARATOR: separator if separator is not False else light,
        consts.TYPE_DARKMODULE: dark_module if dark_module is not False else dark,
        consts.TYPE_QUIET_ZONE: quiet_zone if quiet_zone is not False else light,
    }
    return {mt: val for mt, val in mt2color.items() if mt not in unsupported}


_VALID_SERIALIZERS = {
    'svg': write_svg
}


def save(matrix, version, out, kind=None, **kw):
    """\
    Serializes the matrix in any of the supported formats.

    :param matrix: The matrix to serialize.
    :param int version: The (Micro) QR code version
    :param out: A filename or a writable file-like object with a
            ``name`` attribute. If a stream like :py:class:`io.ByteIO` or
            :py:class:`io.StringIO` object without a ``name`` attribute is
            provided, use the `kind` parameter to specify the serialization
            format.
    :param kind: If the desired output format cannot be extracted from
            the filename, this parameter can be used to indicate the
            serialization format (i.e. "svg" to enforce SVG output)
    :param kw: Any of the supported keywords by the specific serialization
            method.
    """
    is_stream = False
    if kind is None:
        try:
            fname = out.name
            is_stream = True
        except AttributeError:
            fname = out
        ext = fname[fname.rfind('.') + 1:].lower()
    else:
        ext = kind.lower()
    is_svgz = not is_stream and ext == 'svgz'
    try:
        serializer = _VALID_SERIALIZERS[ext if not is_svgz else 'svg']
    except KeyError:
        raise ValueError('Unknown file extension ".{0}"'.format(ext))
    if is_svgz:
        with gzip.open(out, 'wb', compresslevel=kw.pop('compresslevel', 9)) as f:
            serializer(matrix, version, f, **kw)
    else:
        serializer(matrix, version, out, **kw)
