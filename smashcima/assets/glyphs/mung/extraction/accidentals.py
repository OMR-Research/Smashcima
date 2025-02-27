from typing import Callable, Optional, List

import cv2
import numpy as np
from mung.graph import NotationGraph
from mung.node import Node

from smashcima.geometry import Point


def _get_center_of_mass(mask: np.ndarray) -> Point:
    """Computes the center of mass for a given True/False image
    and returns it as a Point(x, y) pixel coordinate in the image."""
    assert mask.dtype == np.uint8 or mask.dtype == np.bool
    assert len(mask.shape) == 2
    # note: values must be 0/1, despite being uint8

    m = cv2.moments(mask.astype(np.uint8))
    # add 1e-5 to avoid division by zero
    x = int(m["m10"] / (m["m00"] + 1e-5))
    y = int(m["m01"] / (m["m00"] + 1e-5))
    return Point(x, y)


def _get_components_not_touching_image_border(
    mask: np.ndarray
) -> List[np.ndarray]:
    """
    Takes a binary image and finds all components (areas with value 1)
    that don't touch the image border.
    """
    assert mask.dtype == np.uint8
    assert len(mask.shape) == 2
    # note: values must be 0/1, despite being uint8

    height, width = mask.shape
    ret, labels = cv2.connectedComponents(mask)

    indices_to_remove = set()
    for x in range(width):
        indices_to_remove.add(labels[0, x])
        indices_to_remove.add(labels[height - 1, x])
    for y in range(height):
        indices_to_remove.add(labels[y, 0])
        indices_to_remove.add(labels[y, width - 1])
    indices = set(range(1, ret)) - indices_to_remove

    out_masks: List[np.ndarray] = []
    for i in indices:
        out_masks.append(labels == i)
    return out_masks


def _sort_components_by_proximity_to_point(
    components: List[np.ndarray], point: Point
) -> List[np.ndarray]:
    distance: Callable[[np.ndarray], float] = lambda c: \
        (point.vector - _get_center_of_mass(c).vector).magnitude_squared
    components_with_distances = [(c, distance(c)) for c in components]
    components_with_distances.sort(key=lambda x: x[1])
    return [x[0] for x in components_with_distances]


def get_accidental_center_from_central_hole(
    accidental: Node
) -> Optional[Point]:
    """Extracts the sprite origin point for an accidental by finding the
    central hole in the mask (the center component) and getting its center.
    If no such hole is fonud, None is returned."""
    # obtain sprite from the center of the inner component
    # and handle open accidentals by repeatedly dilating
    # (dilate vertically twice as much)

    # get the center of the whole accidental by mass
    # (better then just the 0.5 center)
    object_com = _get_center_of_mass(accidental.mask)

    # prepare the accidental mask as a grayscale uint8 image
    mask = (accidental.mask * 255).astype(dtype=np.uint8)

    # repeatedly dilate the image, until a component (a hole) gets
    # created in the middle (the middle = closest one to the object_com)
    # and once such is created, return its center
    # (dilation is done to close off gaps in accidentals that are scribbled
    # fast and have the inner hole barely open)
    for _ in range(5): # dilate 5-times by 1 pixel
        # get holes in the mask
        components = _get_components_not_touching_image_border(
            1 - (mask // 255)
        )
        components = _sort_components_by_proximity_to_point(
            components, object_com
        )

        # if no hole, dilate and repeat
        if len(components) == 0:
            kernel = np.ones((5, 3), np.uint8)
            mask = cv2.dilate(mask, kernel, iterations=1)
            continue

        # we have a hole now! Get it's center and return
        component_com = _get_center_of_mass(
            components[0]
        )
        return Point(
            component_com.x / accidental.width,
            component_com.y / accidental.height
        )
    
    # we did not find a hole despite dilating couple of times
    return None


def get_accidental_center_from_notehead(
    accidental: Node,
    graph: NotationGraph
) -> Optional[Point]:
    """Extracts the sprite origin point for an accidental by aligning the point
    vertically with the attached notehead. Returns None if there is no attached
    notehead (happens for key signatures)."""
    
    # get the attached notehead
    noteheads = graph.parents(
        accidental,
        ["noteheadFull", "noteheadHalf"]
    )
    if len(noteheads) == 0:
        return None
    notehead = noteheads[0]

    # compute the origin point, taking the center of the notehead as a reference
    return Point(
        x=0.5,
        y=(
            # "notehead center - accidental top" in pixels
            ((notehead.top + notehead.bottom) / 2) - accidental.top
        ) / accidental.height # relativized to 0-1 scale
    )
