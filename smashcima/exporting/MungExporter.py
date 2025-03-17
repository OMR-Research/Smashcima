import xml.etree.ElementTree as ET

from .image.ImageLayer import ImageLayer


class MungExporter:
    def export(self, final_layer: ImageLayer) -> ET.Element:
        """Exports the final layer from a compositor
        into a MuNG XML element tree"""

        # build the root SVG element
        root_element = ET.Element("Nodes")
        root_element.attrib = {
            #"dataset": "foo", # TODO: set these attributes
            #"document": "bar",
        }

        # TODO: assign IDs and construct graph links before exporting
        # (maybe construct the mung graph in the mung package and then use its
        # methods to export into an XML file?)

        # convert each region into a MuNG node
        for id, region in enumerate(final_layer.regions):
            node_element = ET.Element("Node")
            node_element.text = ""

            id_element = ET.Element("Id")
            id_element.text = str(id)
            node_element.append(id_element)
            
            classname_element = ET.Element("ClassName")
            classname_element.text = region.label # TODO: map label names
            node_element.append(classname_element)

            bbox = region.get_bbox_in_space(final_layer.space)

            top_element = ET.Element("Top")
            top_element.text = str(bbox.top)
            node_element.append(top_element)

            left_element = ET.Element("Left")
            left_element.text = str(bbox.left)
            node_element.append(left_element)

            width_element = ET.Element("Width")
            width_element.text = str(bbox.width)
            node_element.append(width_element)

            height_element = ET.Element("Height")
            height_element.text = str(bbox.height)
            node_element.append(height_element)

            root_element.append(node_element)
        
        return root_element
