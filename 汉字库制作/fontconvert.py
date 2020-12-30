#!python3
import freetype
import zlib
import sys
import re
import math
import argparse
from collections import namedtuple

#run 分别制作不同点阵的字库文件
#python3 fontconvert.py --compress msyh16 16 msyh.ttc  >hzwnn_16.h
#python3 fontconvert.py --compress msyh24 24 msyh.ttc  >hzwnn_24.h
#python3 fontconvert.py --compress msyh36 36 msyh.ttc  >hzwnn_36.h
#python3 fontconvert.py --compress msyh48 48 msyh.ttc  >hzwnn_48.h
#intervals 变量定义汉字的unicode码，
#一定要包括前两行的ASCII characters ，否则 Esp32运行时会报错重启: Guru Meditation Error
#msyh 是微软雅黑字库，从win10》控制面板》字体中拷出

print("start", file=sys.stderr)
parser = argparse.ArgumentParser(description="Generate a header file from a font to be used with epdiy.")
parser.add_argument("name", action="store", help="name of the font.")
parser.add_argument("size", type=int, help="font size to use.")
parser.add_argument("fontstack", action="store", nargs='+', help="list of font files, ordered by descending priority.")
parser.add_argument("--compress", dest="compress", action="store_true", help="compress glyph bitmaps.")
args = parser.parse_args()

GlyphProps = namedtuple("GlyphProps", ["width", "height", "advance_x", "left", "top", "compressed_size", "data_offset", "code_point"])

font_stack = [freetype.Face(f) for f in args.fontstack]
compress = args.compress
size = args.size
font_name = args.name

print("compress",compress, file=sys.stderr)
intervals= [
#以下两行是 ASCII characters 必须有！否则esp32运行报错
#Guru Meditation Error: Core  1 panic'ed (StoreProhibited). Exception was unhandled. 
    (32, 126),
    (160, 255),    
(0x4e00,0x4e00),
(0x4e03,0x4e03),
(0x4e09,0x4e09),
(0x4e8c,0x4e8c),
(0x4e94,0x4e94),
(0x516d,0x516d),
(0x5206,0x5206),
(0x5468,0x5468),
(0x56db,0x56db),
(0x5e74,0x5e74),
(0x65e5,0x65e5),
(0x65e5,0x65e5),
(0x65f6,0x65f6),
(0x661f,0x661f),
(0x6674,0x6674),
(0x6708,0x6708),
(0x671f,0x671f),
(0x70b9,0x70b9),
(0x79d2,0x79d2),
(0x9634,0x9634),
(0x96e8,0x96e8),
(0x96ea,0x96ea),

]



def norm_floor(val):
    return int(math.floor(val / (1 << 6)))

def norm_ceil(val):
    return int(math.ceil(val / (1 << 6)))

for face in font_stack:
    # shift by 6 bytes, because sizes are given as 6-bit fractions
    # the display has about 150 dpi.
    face.set_char_size(size << 6, size << 6, 150, 150)

def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]

total_size = 0
total_packed = 0
all_glyphs = []
 
def load_glyph(code_point):
    face_index = 0
    while face_index < len(font_stack):
        face = font_stack[face_index]
        glyph_index = face.get_char_index(code_point)
        if glyph_index > 0:
            face.load_glyph(glyph_index, freetype.FT_LOAD_RENDER)
            return face
            break
        face_index += 1
        print (f"falling back to font {face_index} for {chr(code_point)}.", file=sys.stderr)
    raise ValueError(f"code point {code_point} not found in font stack!")

for i_start, i_end in intervals:
    for code_point in range(i_start, i_end + 1):
        face = load_glyph(code_point)
        bitmap = face.glyph.bitmap
        pixels = []
        px = 0
        for i, v in enumerate(bitmap.buffer):
            y = i / bitmap.width
            x = i % bitmap.width
            if x % 2 == 0:
                px = (v >> 4)
            else:
                px = px | (v & 0xF0)
                pixels.append(px);
                px = 0
            # eol
            if x == bitmap.width - 1 and bitmap.width % 2 > 0:
                pixels.append(px)
                px = 0

        packed = bytes(pixels);
        total_packed += len(packed)
        compressed = packed
        if compress:
            compressed = zlib.compress(packed)

        glyph = GlyphProps(
            width = bitmap.width,
            height = bitmap.rows,
            advance_x = norm_floor(face.glyph.advance.x),
            left = face.glyph.bitmap_left,
            top = face.glyph.bitmap_top,
            compressed_size = len(compressed),
            data_offset = total_size,
            code_point = code_point,
        )
        total_size += len(compressed)
        all_glyphs.append((glyph, compressed))

# pipe seems to be a good heuristic for the "real" descender
face = load_glyph(ord('|'))

glyph_data = []
glyph_props = []
for index, glyph in enumerate(all_glyphs):
    props, compressed = glyph
    glyph_data.extend([b for b in compressed])
    glyph_props.append(props)

print("total", total_packed, file=sys.stderr)
print("compressed", total_size, file=sys.stderr)

print("#pragma once")
print("#include \"epd_driver.h\"")
print(f"const uint8_t {font_name}Bitmaps[{len(glyph_data)}] = {{")
for c in chunks(glyph_data, 16):
    print ("    " + " ".join(f"0x{b:02X}," for b in c))
print ("};");

print(f"const GFXglyph {font_name}Glyphs[] = {{")
for i, g in enumerate(glyph_props):
    print ("    { " + ", ".join([f"{a}" for a in list(g[:-1])]),"},", f"// {chr(g.code_point) if g.code_point != 92 else '<backslash>'}")
print ("};");

print(f"const UnicodeInterval {font_name}Intervals[] = {{")
offset = 0
for i_start, i_end in intervals:
    print (f"    {{ 0x{i_start:X}, 0x{i_end:X}, 0x{offset:X} }},")
    offset += i_end - i_start + 1
print ("};");

print(f"const GFXfont {font_name} = {{")
print(f"    (uint8_t*){font_name}Bitmaps,")
print(f"    (GFXglyph*){font_name}Glyphs,")
print(f"    (UnicodeInterval*){font_name}Intervals,")
print(f"    {len(intervals)},")
print(f"    {1 if compress else 0},")
print(f"    {norm_ceil(face.size.height)},")
print(f"    {norm_ceil(face.size.ascender)},")
print(f"    {norm_floor(face.size.descender)},")
print("};")
