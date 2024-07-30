from datetime import datetime, time, timedelta
import io
import os
import random
import re
import string
from typing import Literal
from xml.etree import ElementTree

from dateutil import relativedelta
from ttoolly.utils.utils import convert_size_to_bytes


def get_randname(l: int = 10, _type: str = "a", length_of_chunk: int = 10) -> str:
    """
    a - all
    d - digits
    w - letters
    p - punctuation
    s - whitespace
    """
    if "a" == _type:
        text = string.printable
    else:
        text = ""
        letters_dict = {
            "d": string.digits,
            "w": string.ascii_letters,
            "p": string.punctuation,
            "s": string.whitespace,
        }
        for t in _type:
            text += letters_dict.get(t, t)

    count_of_chunks = l // length_of_chunk
    n = "".join(
        [random.choice(text) for _ in range(length_of_chunk)]
    ) * count_of_chunks + "".join(
        [random.choice(text) for _ in range(l % length_of_chunk)]
    )
    return n


def get_random_color(type_: Literal['rgb', 'hex'] = 'rgb') -> str:
    if type_ == 'rgb':
        return f'rgb({random.randint(1, 255)}, {random.randint(1, 255)}, {random.randint(1, 255)})'
    if type_ == 'hex':
        return '#%06x' % random.randint(0, 0xFFFFFF)


def get_random_datetime_value(
    datetime_from=None,
    datetime_to=None,
):
    month_start = datetime.combine(datetime.today().replace(day=1), time.min)
    month_end = (
        month_start + relativedelta.relativedelta(months=1) - timedelta(microseconds=1)
    )
    datetime_from = datetime_from or month_start
    datetime_to = datetime_to or month_end
    return datetime.fromtimestamp(
        random.randint(
            int(datetime_from.timestamp() * 10**6),
            int(datetime_to.timestamp() * 10**6),
        )
        / 10**6
    )


def get_random_domain_value(length):
    end_length = random.randint(2, min(length - 2, 6))
    domain_length = random.randint(1, min(length - end_length - 1, 62))
    subdomain_length = length - end_length - 1 - domain_length - 1
    if subdomain_length <= 1:
        subdomain = ""
        if subdomain_length >= 0:
            domain_length += 1 + subdomain_length
    else:
        subdomain = (
            f"{get_randname(1, 'w')}{get_randname(subdomain_length - 1, 'wd.-')}."
        )
        while any([len(el) > 62 for el in subdomain.split(".")]):
            subdomain = ".".join(
                [
                    (el if len(el) <= 62 else el[:61] + "." + el[62:])
                    for el in subdomain.split(".")
                ]
            )
        subdomain = re.sub(r"\.[\.\-]", ".%s" % get_randname(1, "w"), subdomain)
        subdomain = re.sub(r"\-\.", "%s." % get_randname(1, "w"), subdomain)
    if domain_length < 3:
        domain = get_randname(domain_length, "wd")
    else:
        domain = "%s%s%s" % (
            get_randname(1, "w"),
            get_randname(domain_length - 2, "wd-"),
            get_randname(1, "w"),
        )
        domain = re.sub(r"\-\-", "%s-" % get_randname(1, "w"), domain)

    return "%s%s.%s" % (subdomain, domain, get_randname(end_length, "w"))


def get_random_email_value(length, safe=False):
    """
    https://www.ietf.org/rfc/rfc2821.txt
    https://www.ietf.org/rfc/rfc3696.txt
    """
    if length < 3:  # a@b
        raise ValueError("Email length cannot be less than 3")
    if length < 6:  # a@b.cd
        username = get_randname(1, "wd")
        domain = get_randname(length - 2, "wd")
        return f"{username}@{domain}".lower()

    MAX_USERNAME_LENGTH = 64
    min_length_without_name = 1 + 1 + 3  # @X.aa
    name_length = random.randint(
        min(2, length - min_length_without_name),
        min(MAX_USERNAME_LENGTH, length - min_length_without_name),
    )

    domain_length = length - name_length - 1  # <name>@<domain>
    symbols_for_generate = "wd"
    symbols_with_escaping = ""
    if not safe and name_length > 1:
        symbols_for_generate += "!#$%&'*+-/=?^_`{|}~."
        symbols_with_escaping = '\\"(),:;<>@[]'
        symbols_for_generate += symbols_with_escaping
    username = get_randname(name_length, symbols_for_generate)
    while ".." in username:
        username = username.replace("..", get_randname(1, "wd") + ".")
    for s in symbols_with_escaping:
        if s in username:
            username = username.replace(s, fr"\{s}")[:name_length]
    username = re.sub(r"(\.$)|(^\.)|(\\$)", get_randname(1, "wd"), username)
    while len(username) < name_length:
        username += get_randname(1, "wd")
    domain = get_random_domain_value(domain_length)
    return f"{username}@{domain}".lower()


def get_random_image(
    path: str = '',
    filename: str = '',
    size: int | str | None = None,
    width: int | None = None,
    height: int | None = None,
):
    """
    generate image file with size
    """
    width = width or random.randint(1, 1000)
    height = height or random.randint(1, 1000)

    filename = filename or get_randname(10, 'wrd ').strip()
    if os.path.splitext(filename)[1] in ('.bmp',):
        content = get_random_bmp_content(convert_size_to_bytes(size or 10))
    else:
        if size is not None:
            size = convert_size_to_bytes(size)
            _size = max(1, size - 800)
            width = min(_size, width)
            height = min(int(_size / width), height)
        else:
            size = 10
        content = {
            '.gif': get_random_gif_content,
            '.svg': get_random_svg_content,
            '.png': get_random_png_content,
        }.get(os.path.splitext(filename)[1].lower(), get_random_jpg_content)(
            size, width, height
        )
    if path:
        if os.path.exists(os.path.join(path, filename)):
            os.remove(os.path.join(path, filename))
        with open(os.path.join(path, filename), 'ab') as f:
            f.write(content)
    else:
        f = io.BytesIO()
        f.write(content)
    return f


def get_random_img_content(_format, size=10, width=1, height=1):
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        raise ImportError("Pillow required. Install ttoolly as ttoolly[images]")
    size = convert_size_to_bytes(size)
    image = Image.new('RGB', (width, height), get_random_color('hex'))
    draw = ImageDraw.Draw(image)
    draw.rectangle(
        (0, 0, width - 1, height - 1),
        fill=None,
        outline=get_random_color('hex'),
        width=3,
    )
    circle_r = int(min(width, height) / 2 - 1)
    draw.circle(
        (width / 2, height / 2),
        radius=circle_r,
        fill=get_random_color('hex'),
        outline=get_random_color('hex'),
        width=3,
    )

    output = io.BytesIO()
    image.save(output, format=_format)
    content = output.getvalue()
    size -= len(content)
    if size > 0:
        content += bytearray(size)
    del draw
    return content


def get_random_bmp_content(size=10, width=1, height=1):
    return get_random_img_content('BMP', size, width, height)


def get_random_gif_content(size=10, width=1, height=1):
    return get_random_img_content('GIF', size, width, height)


def get_random_jpg_content(size=10, width=1, height=1):
    return get_random_img_content('JPEG', size, width, height)


def get_random_png_content(size=10, width=1, height=1):
    return get_random_img_content('PNG', size, width, height)


def get_random_svg_content(size=10, width=1, height=1):
    """
    generates svg content
    """
    size = convert_size_to_bytes(size)
    doc = ElementTree.Element(
        'svg',
        width=str(width),
        height=str(height),
        version='1.1',
        xmlns='http://www.w3.org/2000/svg',
    )
    ElementTree.SubElement(
        doc,
        'rect',
        width=str(width),
        height=str(height),
        style=f'fill:{get_random_color()};stroke-width:3;stroke:{get_random_color()}',
    )

    circle_r = int(min(width, height) / 2 - 1)
    ElementTree.SubElement(
        doc,
        'circle',
        r=str(circle_r),
        cx=str(int(width / 2)),
        cy=str(int(height / 2)),
        style=f'fill:{get_random_color()};stroke-width:3;stroke:{get_random_color()}',
    )

    output = io.StringIO()
    header = (
        '<?xml version=\"1.0\" standalone=\"no\"?>\n'
        '<!DOCTYPE svg PUBLIC \"-//W3C//DTD SVG 1.1//EN\" \"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd\">\n'
    )
    output.write(header)
    output.write(ElementTree.tostring(doc).decode())
    content = output.getvalue()
    size -= len(content)
    if size > 0:
        content += '<!-- %s -->' % ('a' * (size - 9))
    output.close()
    return content.encode()
