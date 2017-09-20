# encoding: utf-8
"""
Things and stuff
"""
import string
import os
from collections import namedtuple
import xml.etree.ElementTree
from xml.etree.ElementTree import ElementTree, XML
import binpack

from . import conf

namespace_string = 'http://www.w3.org/2000/svg'
namespace = lambda x: '{{{ns}}}{x}'.format(ns=namespace_string, x=x)
parser = ElementTree()

# parse_dim = lambda x: float(x[:-2]) if x[-2:] == 'pt' else float(x)
# class viewBox(object):
#     def __init__(self, minx, miny, width, height):
#         self.minx = minx
#         self.miny = miny
#         self.width = width
#         self.height = height

viewBox = namedtuple('viewBox', ['minx', 'miny', 'width', 'height'])

parse_dim = lambda x: float(x.strip(string.ascii_lowercase + string.ascii_uppercase))
unparse_dim = lambda x: "{}pt".format(x)
parse_viewbox = lambda x: viewBox(*[float(y) for y in x.replace(',', ' ').split()])
unparse_viewbox = lambda vb: "{minx} {miny} {width} {height}".format(**vb._asdict())

part_map = {}
print(len(conf.parts))
for part in conf.parts:
    with open(os.path.join(conf.svgdir, "{}.svg".format(part))) as fd:
        svg_tag = parser.parse(fd)

        # import IPython
        # IPython.embed()

        # svg_element = svg_tag.findall(namespace('svg'))
        # assert len(svg_element) == 1, "We expect only one svg document in this file. ({}) ({})".format(part, svg_tag.attrib)

        pages = [x for x in svg_tag.findall(namespace('g')) if x.attrib['id'] == 'page1']
        assert len(pages) == 1, "We expect only one page1."

        vb, width, height = (
            parse_viewbox(svg_tag.attrib['viewBox']),
            parse_dim(svg_tag.attrib['width']),
            parse_dim(svg_tag.attrib['height']))

        assert vb.width == width, "omg width wrong. {} == {}".format(vb.width, width)
        assert vb.height == height, "omg height wrong. {} == {}".format(vb.height, height)

        item = binpack.Item(width + 2 * conf.epsilon, height + 2 * conf.epsilon)
        part_map[item] = {
            'xml': pages[0],
            'viewBox': vb
        }


        # print("viewBox: {}, width: {}, height: {}".format(
        #     svg_tag.attrib['viewBox'],
        #     svg_tag.attrib['width'],
        #     svg_tag.attrib['height']))
        # print(pages)

bp_manager = binpack.BinManager(
    conf.sheet_width,
    conf.sheet_height,
    pack_algo=conf.algorithm,
    rotation=True,
    sorting=True)

bp_manager.add_items(*part_map.keys())

bp_manager.execute()

empty_svg = """<?xml version='1.0' encoding='UTF-8'?>
<svg version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'>
</svg>
"""
new_svg = XML(empty_svg)

new_svg.attrib['width'] = unparse_dim(conf.sheet_width)
new_svg.attrib['height'] = unparse_dim(conf.sheet_height)
new_svg.attrib['viewBox'] = unparse_viewbox(viewBox(56.4094, 53.8583, conf.sheet_width, conf.sheet_height))

def transform(point, vb, rotated):
    transformations = []
    transformations.append("translate({x} {y})".format(
        x=point[0] + conf.epsilon, 
        y=point[1] + conf.epsilon))
    if rotated:
        transformations.append("translate({height})".format(height=vb.height))
        transformations.append("rotate(90 {x0} {y0})".format(x0=vb.minx, y0=vb.miny))
    print(" ".join(transformations))
    return " ".join(transformations)

for item, part in part_map.items():
    part_rotated = (item.x < item.y) != (part['viewBox'].width < part['viewBox'].height)
    part['xml'].attrib['transform'] = transform(item.CornerPoint, part['viewBox'], part_rotated)
    new_svg.append(part['xml'])

ET = ElementTree(new_svg)
xml.etree.ElementTree.register_namespace('', namespace_string)
ET.write('output.svg', encoding='utf-8', xml_declaration=True)

# with open('output.svg', 'w') as fd:
#     ElementTree(new_svg).write(fd)

print(new_svg)
print(part_map.keys())
