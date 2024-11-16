import base64
import xml.etree.ElementTree as ET
from typing import Optional

import cv2

from smashcima.geometry import Transform
from smashcima.scene import (AffineSpace, AffineSpaceVisitor, LabeledRegion,
                             SceneObject, Sprite, ViewBox)

SVG_NS = "{http://www.w3.org/2000/svg}"
XLINK_NS = "{http://www.w3.org/1999/xlink}"


class SvgExporter:
    def __init__(
        self,
        background_fill: Optional[str] = None,
        render_labeled_regions: bool = False
    ):
        self.background_fill = background_fill
        self.render_labeled_regions = render_labeled_regions

    def export_string(self, view_box: ViewBox, pretty=False) -> str:
        """Exports the provided scene into an SVG string"""
        
        # build the element tree
        root = self.export(view_box)

        # prettify
        if pretty and hasattr(ET, "indent"):
            ET.indent(root, " ", 0)
        elif pretty:
            print(
                "WARNING: SVG pretty-printing is only supported " +
                "from Python 3.9 and up."
            )

        # register namespaces and stringify
        ET.register_namespace(
            prefix="",
            uri="http://www.w3.org/2000/svg"
        )
        ET.register_namespace(
            prefix="xlink",
            uri="http://www.w3.org/1999/xlink"
        )
        return str(ET.tostring(
            root,
            encoding="utf-8",
            xml_declaration=True
        ), "utf-8")

    def export(self, view_box: ViewBox) -> ET.Element:
        """Exports the provided scene into and SVG XML element tree"""
        
        # build the root SVG element
        root_element = ET.Element(SVG_NS + "svg")
        width = view_box.rectangle.width
        height = view_box.rectangle.height
        root_element.attrib = {
            "width": f"{width}mm",
            "height": f"{height}mm",
            "viewBox": f"0 0 {width} {height}",
            "version": "1.1",
        }

        # background fill color rectangle
        if self.background_fill is not None:
            background_element = ET.Element(SVG_NS + "rect")
            background_element.attrib = {
                "x": "0",
                "y": "0",
                "width": str(width),
                "height": str(height),
                "fill": self.background_fill,
                "id": "SvgBackgroundFill"
            }
            root_element.append(background_element)

        # get the root space and viewport transform
        root_space = view_box.space.get_root()
        root_to_view_transform = root_space.transform_from(view_box.space) \
            .inverse()
        
        # extract visible object hierarchy
        svg_visitor = SvgVisitor(space=root_space)
        svg_visitor.run()

        # set the viewport transofrm to the root space group
        # (i.e. position the whole scene so that it aligns with the viewport)
        svg_visitor.group_element.attrib = {
            "transform": svg_matrix_from_transform(root_to_view_transform),
            "id": "RootAffineSpace_" + str(id(root_space))
        }
        root_element.append(svg_visitor.group_element)

        # extract labeled regions overlay
        if self.render_labeled_regions:
            regions_svg_group = ET.Element(SVG_NS + "g")
            regions_svg_group.attrib = {
                "id": "LabeledRegion overlay"
            }
            region_visitor = RegionVisitor(
                space=root_space,
                regions_svg_group=regions_svg_group,
                transform_to_viewport=root_to_view_transform
            )
            region_visitor.run()
            root_element.append(regions_svg_group)

        return root_element


class SvgVisitor(AffineSpaceVisitor):
    """Visits an AffineSpace hierarchy and constructs an SVG tree"""
    
    def __init__(self, space: AffineSpace):
        super().__init__(space)

        self.group_element = ET.Element(SVG_NS + "g")
        self.group_element.attrib = {
            "transform": svg_matrix_from_transform(space.transform),
            "id": "AffineSpace_" + str(id(space))
        }
    
    def create_sub_visitor(self, sub_space: AffineSpace) -> "SvgVisitor":
        return SvgVisitor(sub_space)

    def accept_sub_visitor(self, sub_visitor: "SvgVisitor"):
        self.group_element.append(sub_visitor.group_element)

    def visit_scene_object(self, obj: SceneObject):
        if isinstance(obj, Sprite):
            self.group_element.append(
                sprite_to_image_element(sprite=obj)
            )
        # TODO: elif SVG elements in the scene


class RegionVisitor(AffineSpaceVisitor):
    """Constructs flattened SVG elements for labeled regions (because if they
    are part of the hierarchy, they will get rotated and transformed - we want
    them to be in the viewport space)"""

    def __init__(
        self,
        space: AffineSpace,
        regions_svg_group: ET.Element,
        transform_to_viewport: Transform
    ):
        super().__init__(space)

        self.regions_svg_group = regions_svg_group
        self.transform_to_viewport = transform_to_viewport
    
    def create_sub_visitor(self, sub_space: AffineSpace) -> "RegionVisitor":
        return RegionVisitor(
            space=sub_space,
            regions_svg_group=self.regions_svg_group,
            transform_to_viewport=sub_space.transform.then(
                self.transform_to_viewport
            )
        )

    def accept_sub_visitor(self, sub_visitor: "RegionVisitor"):
        pass # nothing needs to be done

    def visit_scene_object(self, obj: SceneObject):
        if isinstance(obj, LabeledRegion):
            self.regions_svg_group.append(
                labeled_region_to_svg_elements(
                    region=obj,
                    transform_to_viewport=self.transform_to_viewport
                )
            )


def svg_matrix_from_transform(t: Transform) -> str:
    """Formats a smashcima transform into the SVG transform attribute value"""
    a, b = t.matrix[:, 0]
    c, d = t.matrix[:, 1]
    e, f = t.matrix[:, 2]
    return f"matrix({a} {b} {c} {d} {e} {f})"


def sprite_to_image_element(sprite: Sprite) -> ET.Element:
    """Converts a Sprite instance to an SVG image element"""
    image_element = ET.Element(SVG_NS + "image")
    
    png_binary_data = cv2.imencode(".png", sprite.bitmap)[1].tobytes()
    base64_str_data = str(base64.b64encode(png_binary_data), "utf-8")

    width = sprite.physical_width
    height = sprite.physical_height

    image_element.attrib = {
        "transform": svg_matrix_from_transform(sprite.transform),
        "x": str(-width * sprite.bitmap_origin.x),
        "y": str(-height * sprite.bitmap_origin.y),
        "width": str(width),
        "height": str(height),
        XLINK_NS + "href": "data:image/png;base64," + base64_str_data,
        "id": "Sprite_" + str(id(sprite))
    }

    return image_element


def labeled_region_to_svg_elements(
    region: LabeledRegion,
    transform_to_viewport: Transform
) -> ET.Element:
    rectangle_element = ET.Element(SVG_NS + "rect")

    bbox = transform_to_viewport.apply_to(region.contours).bbox()

    # get a pseudo-random hue for the label
    hue = hash(region.label) % 360

    rectangle_element.attrib = {
        "x": str(bbox.x),
        "y": str(bbox.y),
        "width": str(bbox.width),
        "height": str(bbox.height),
        "fill": f"hsl({hue}, 100%, 50%)",
        "fill-opacity": "0.25",
        "stroke": f"hsl({hue}, 100%, 50%)",
        "stroke-opacity": "0.5",
        "stroke-width": "0.5",
        "id": "Region_" + str(id(region)) + "__" + region.label
    }

    return rectangle_element
