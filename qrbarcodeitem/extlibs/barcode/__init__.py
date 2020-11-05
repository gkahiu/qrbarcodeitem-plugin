"""This package provides a simple way to create standard barcodes.
It needs no external packages to be installed, the barcodes are
created as SVG objects. If Pillow is installed, the barcodes can also be
rendered as images (all formats supported by Pillow).
"""
import os
from typing import BinaryIO
from typing import Dict
from typing import Union

from .codex import Code128
from .codex import Code39
from .codex import Gs1_128
from .codex import PZN
from .ean import EAN13
from .ean import EAN14
from .ean import EAN8
from .ean import JAN
from .errors import BarcodeNotFoundError
from .isxn import ISBN10
from .isxn import ISBN13
from .isxn import ISSN
from .itf import ITF
from .upc import UPCA
from .version import version  # noqa: F401

__BARCODE_MAP = {
    "ean8": EAN8,
    "ean13": EAN13,
    "ean": EAN13,
    "gtin": EAN14,
    "ean14": EAN14,
    "jan": JAN,
    "upc": UPCA,
    "upca": UPCA,
    "isbn": ISBN13,
    "isbn13": ISBN13,
    "gs1": ISBN13,
    "isbn10": ISBN10,
    "issn": ISSN,
    "code39": Code39,
    "pzn": PZN,
    "code128": Code128,
    "itf": ITF,
    "gs1_128": Gs1_128,
}

PROVIDED_BARCODES = list(__BARCODE_MAP)
PROVIDED_BARCODES.sort()


def get(name, code=None, writer=None, options=None):
    """Helper method for getting a generator or even a generated code.

    :param str name: The name of the type of barcode desired.
    :param str code: The actual information to encode. If this parameter is
        provided, a generated barcode is returned. Otherwise, the barcode class
        is returned.
    :param Writer writer: An alternative writer to use when generating the
        barcode.
    :param dict options: Aditional options to be passed on to the barcode when
        generating.
    """

    options = options or {}
    try:
        barcode = __BARCODE_MAP[name.lower()]
    except KeyError:
        raise BarcodeNotFoundError(
            "The barcode {!r} you requested is not known.".format(name)
        )

    if code is not None:
        return barcode(code, writer, **options)
    else:
        return barcode


def get_class(name):
    return get_barcode(name)


def generate(
    name: str,
    code: str,
    writer=None,
    output: Union[str, os.PathLike, BinaryIO] = None,
    writer_options: Dict = None,
    text: str = None,
):
    """Shortcut to generate a barcode in one line.

    :param name: Name of the type of barcode to use.
    :param code: Data to encode into the barcode.
    :param writer: A writer to use (e.g.: ImageWriter or SVGWriter).
    :param output: Destination file-like or path-like where to save the generated
     barcode.
    :param writer_options: Options to pass on to the writer instance.
    :param text: Text to render under the barcode.
    """
    from .base import Barcode

    writer = writer or Barcode.default_writer()
    writer.set_options(writer_options or {})

    barcode = get(name, code, writer)

    if isinstance(output, str):
        fullname = barcode.save(output, writer_options, text)
        return fullname
    elif output:
        barcode.write(output, writer_options, text)
    else:
        raise TypeError("'output' cannot be None")


get_barcode = get
get_barcode_class = get_class
