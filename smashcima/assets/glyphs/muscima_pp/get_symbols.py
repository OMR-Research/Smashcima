from typing import Callable, Dict, List, Optional, Tuple

import cv2
import numpy as np
from muscima.io import CropObject

from smashcima.geometry import Point, Vector2
from smashcima.scene import ComposedGlyph, Glyph, LineGlyph, ScenePoint, Sprite
from smashcima.scene.AffineSpace import AffineSpace
from smashcima.scene.SmashcimaLabels import SmashcimaLabels
from smashcima.scene.SmuflLabels import SmuflLabels

from ..mung.extraction.get_line_endpoints import get_line_endpoints
from .MppGlyphMetadata import MppGlyphMetadata
from .MppPage import MppPage

# source:
# https://pages.cvc.uab.es/cvcmuscima/index_database.html
MUSCIMA_PP_DPI = 300

TALL_BARLINE_THRESHOLD_PX = 150
BEAM_HOOK_MAX_WIDTH_PX = 25


def _mpp_mask_to_sprite_bitmap(mask: np.ndarray):
    """True/False pixel mask to black on transparent BGRA uint8 bitmap"""
    assert len(mask.shape) == 2
    assert mask.dtype == np.uint8
    alpha = mask * 255
    color = np.zeros_like(mask)
    bitmap = np.stack([color, color, color, alpha], axis=2)
    return bitmap


def _crop_objects_to_single_sprite_glyphs(
    crop_objects: List[CropObject],
    page: MppPage,
    label: str,
    sprite_origin: Optional[Callable[[CropObject], Point]] = None
) -> List[Glyph]:
    glyphs: List[Glyph] = []

    for o in crop_objects:
        space = AffineSpace()
        sprite = Sprite(
            space=space,
            bitmap=_mpp_mask_to_sprite_bitmap(o.mask),
            bitmap_origin=(
                sprite_origin(o) if sprite_origin else Point(0.5, 0.5)
            ),
            dpi=MUSCIMA_PP_DPI
        )
        glyph = Glyph(
            space=space,
            region=Glyph.build_region_from_sprites_alpha_channel(
                label=label,
                sprites=[sprite]
            ),
            sprites=[sprite]
        )
        MppGlyphMetadata.stamp_glyph(glyph, page, int(o.objid))
        glyphs.append(glyph)

    return glyphs


def _get_y_position_of_staff_line(
    page: MppPage,
    obj: CropObject,
    line_from_top: int = 0
) -> int:
    """
    Given a CropObject it finds the y-coordinate of the corresponding staff line
    """
    staff = page.get_outlink_to(obj, "staff")
    staff_line = None
    line = 0
    for l in staff.outlinks:
        resolved_link = page.id_lookup[l]
        if resolved_link.clsname == "staff_line":
            if line == line_from_top:  # counted from top, from zero
                staff_line = resolved_link
                break
            line += 1
    assert staff_line is not None
    return (staff_line.top + staff_line.bottom) // 2


def _get_symbols_centered_on_line(
    page: MppPage,
    clsname: str,
    label: str,
    line_from_top: int,
    when_center_outside_recenter: bool = False
) -> List[Glyph]:
    """
    Returns list of symbols with given clsname centered on given line index
    """
    def _sprite_origin(obj: CropObject) -> Point:
        line_y = _get_y_position_of_staff_line(
            page,
            obj,
            line_from_top=line_from_top
        )
        origin_y = (line_y - obj.top) / obj.height
        if (origin_y < 0 or origin_y > 1) and when_center_outside_recenter:
            origin_y = 0.5
        return Point(0.5, origin_y)

    return _crop_objects_to_single_sprite_glyphs(
        crop_objects=[
            o for o in page.crop_objects
            if o.clsname == clsname
        ],
        page=page,
        label=label,
        sprite_origin=_sprite_origin
    )


def _crop_objects_to_line_glyphs(
    crop_objects: List[CropObject],
    page: MppPage,
    label: str,
    horizontal_line: bool,
    in_increasing_direction: bool,
) -> List[LineGlyph]:
    glyphs: List[LineGlyph] = []

    for o in crop_objects:
        # extract endpoints
        blurred_mask = cv2.medianBlur(o.mask, 5) # smooth out (5x5 window)
        points = get_line_endpoints(blurred_mask)
        points.sort(
            key=lambda p: p.x if horizontal_line else p.y,
            reverse=not in_increasing_direction
        )
        if len(points) < 2:
            # print(
            #     "Skipping line:", o.uid,
            #     "Has points:", len(points),
            #     "Is:", o.clsname
            # )
            continue

        # store the points in the point cloud
        page.point_cloud.set_points(o, [points[0], points[-1]])

        # construct the glyph
        space = AffineSpace()
        sprite = Sprite(
            space=space,
            bitmap=_mpp_mask_to_sprite_bitmap(o.mask),
            bitmap_origin=Point(0.5, 0.5),
            dpi=MUSCIMA_PP_DPI
        )
        start_point = ScenePoint(
            point=sprite.get_pixels_to_origin_space_transform().apply_to(points[0]),
            space=space
        )
        end_point = ScenePoint(
            point=sprite.get_pixels_to_origin_space_transform().apply_to(points[-1]),
            space=space
        )
        glyph = LineGlyph(
            space=space,
            region=Glyph.build_region_from_sprites_alpha_channel(
                label=label,
                sprites=[sprite]
            ),
            sprites=[sprite],
            start_point=start_point,
            end_point=end_point
        )
        MppGlyphMetadata.stamp_glyph(glyph, page, int(o.objid))

        # return the glyph
        glyphs.append(glyph)

    return glyphs


def get_connected_components_not_touching_image_border(
    mask: np.ndarray
) -> List[np.ndarray]:
    """
    Takes a binary image and finds all components (areas with value 1)
    that don't touch the image border.
    """
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


def get_center_of_component(mask: np.ndarray) -> Tuple[int, int]:
    m = cv2.moments(mask.astype(np.uint8))
    if m["m00"] == 0:
        import matplotlib.pyplot as plt
        plt.imshow(mask)
        plt.show()
    x = int(m["m10"] / m["m00"])
    y = int(m["m01"] / m["m00"])
    return x, y


def point_distance_squared(ax: int, ay: int, bx: int, by: int) -> int:
    """Returns distance between two points squared"""
    return (ax - bx) ** 2 + (ay - by) ** 2


def sort_components_by_proximity_to_point(
        components: List[np.ndarray], x: int, y: int
) -> List[np.ndarray]:
    with_distances = [
        {
            "component": c,
            "distanceSqr": point_distance_squared(
                *get_center_of_component(c),
                x, y
            )
        }
        for c in components
    ]
    with_distances.sort(key=lambda x: x["distanceSqr"])
    return [x["component"] for x in with_distances]


################################################
# Code that actually extracts required symbols #
################################################


def get_full_noteheads(page: MppPage) -> List[Glyph]:
    return _crop_objects_to_single_sprite_glyphs(
        crop_objects=[
            o for o in page.crop_objects
            if o.clsname == "notehead-full"
            and not page.has_outlink_to(o, "ledger_line")
        ],
        page=page,
        label=SmuflLabels.noteheadBlack.value
    )


def get_empty_noteheads(page: MppPage) -> List[Glyph]:
    return _crop_objects_to_single_sprite_glyphs(
        crop_objects=[
            o for o in page.crop_objects
            if o.clsname == "notehead-empty"
            and not page.has_outlink_to(o, "ledger_line")
        ],
        page=page,
        label=SmuflLabels.noteheadWhole.value
    )


def get_whole_rests(page: MppPage) -> List[Glyph]:
    glyphs = _get_symbols_centered_on_line(
        page,
        clsname="whole_rest",
        label=SmuflLabels.restWhole.value,
        line_from_top=1
    )
    # NOTE: these checks were in the old version, but they make situation
    # worse, because some rests are so big that they should be over the staff,
    # not touching the staff. So it's better to keep the original center.
    # for glyph in glyphs:
    #     origin = glyph.sprites[0].bitmap_origin
    #     if origin.y < -0.5 or origin.y > 0.5:
    #         glyph.sprites[0].bitmap_origin = Point(origin.x, 0.0)
    return glyphs


def get_half_rests(page: MppPage) -> List[Glyph]:
    glyphs = _get_symbols_centered_on_line(
        page,
        clsname="half_rest",
        label=SmuflLabels.restHalf.value,
        line_from_top=2
    )
    # NOTE: these checks were in the old version, but they make situation
    # worse, because some rests are so big that they should be over the staff,
    # not touching the staff. So it's better to keep the original center.
    # for glyph in glyphs:
    #     origin = glyph.sprites[0].bitmap_origin
    #     if origin.y < -1.5 or origin.y > 0.5:
    #         glyph.sprites[0].bitmap_origin = Point(origin.x, 1.0)
    return glyphs


def get_quarter_rests(page: MppPage) -> List[Glyph]:
    return _get_symbols_centered_on_line(
        page,
        clsname="quarter_rest",
        label=SmuflLabels.restQuarter.value,
        line_from_top=2,
        when_center_outside_recenter=True
    )


def get_eighth_rests(page: MppPage) -> List[Glyph]:
    return _get_symbols_centered_on_line(
        page,
        clsname="8th_rest",
        label=SmuflLabels.rest8th.value,
        line_from_top=2,
        when_center_outside_recenter=True
    )


def get_sixteenth_rests(page: MppPage) -> List[Glyph]:
    return _get_symbols_centered_on_line(
        page,
        clsname="16th_rest",
        label=SmuflLabels.rest16th.value,
        line_from_top=2,
        when_center_outside_recenter=True
    )


def get_normal_barlines(page: MppPage) -> List[Glyph]:
    _EXCLUDE = set([
        # this is a double barline, accidentally annotated as simple
        "MUSCIMA-pp_1.0___CVC-MUSCIMA_W-32_N-09_D-ideal___70"
    ])
    return _crop_objects_to_single_sprite_glyphs(
        crop_objects=[
            o for o in page.crop_objects
            if o.clsname in ["thin_barline"]
            and o.height < TALL_BARLINE_THRESHOLD_PX
            and o.uid not in _EXCLUDE
        ],
        page=page,
        label=SmuflLabels.barlineSingle.value
    )


def get_g_clefs(page: MppPage) -> List[Glyph]:
    return _get_symbols_centered_on_line(
        page,
        clsname="g-clef",
        label=SmuflLabels.gClef.value,
        line_from_top=3
    )


def get_f_clefs(page: MppPage) -> List[Glyph]:
    return _get_symbols_centered_on_line(
        page,
        clsname="f-clef",
        label=SmuflLabels.fClef.value,
        line_from_top=1
    )


def get_c_clefs(page: MppPage) -> List[Glyph]:
    return _crop_objects_to_single_sprite_glyphs(
        crop_objects=[
            o for o in page.crop_objects
            if o.clsname == "c-clef"
        ],
        page=page,
        label=SmuflLabels.cClef.value
    )


def get_stems(page: MppPage) -> List[LineGlyph]:
    return _crop_objects_to_line_glyphs(
        crop_objects=[
            o for o in page.crop_objects
            if o.clsname in ["stem"]
        ],
        page=page,
        label=SmuflLabels.stem.value,
        horizontal_line=False, # vertical line
        in_increasing_direction=False # pointing upwards
    )


def get_beams(page: MppPage) -> List[LineGlyph]:
    return _crop_objects_to_line_glyphs(
        crop_objects=[
            o for o in page.crop_objects
            if o.clsname in ["beam"]
            and o.width > BEAM_HOOK_MAX_WIDTH_PX
        ],
        page=page,
        label=SmashcimaLabels.beam.value,
        horizontal_line=True, # horizontal line
        in_increasing_direction=True # pointing to the right
    )


def get_beam_hooks(page: MppPage) -> List[LineGlyph]:
    return _crop_objects_to_line_glyphs(
        crop_objects=[
            o for o in page.crop_objects
            if o.clsname in ["beam"]
            and o.width <= BEAM_HOOK_MAX_WIDTH_PX
        ],
        page=page,
        label=SmashcimaLabels.beamHook.value,
        horizontal_line=True, # horizontal line
        in_increasing_direction=True # pointing to the right
    )


def get_leger_lines(page: MppPage) -> List[LineGlyph]:
    return _crop_objects_to_line_glyphs(
        crop_objects=[
            o for o in page.crop_objects
            if o.clsname in ["ledger_line"]
        ],
        page=page,
        label=SmashcimaLabels.legerLine.value,
        horizontal_line=True, # horizontal line
        in_increasing_direction=True # pointing to the right
    )


def get_flags(page: MppPage) -> Tuple[List[Glyph], List[Glyph]]:
    # NOTE: There are no 32nd flags in the whole MUSCIMA++ dataset.
    # Only 8th and 16th.

    # === extract stem-flag-flag triplets ===

    # stem-id --> (flag-8th, flag-16th)
    extracted_triplets: Dict[
        int,
        Tuple[Optional[CropObject], Optional[CropObject]]
    ] = dict()

    for o in page.crop_objects:
        if o.clsname not in ["8th_flag", "16th_flag"]:
            continue

        # get the stem through a notehead (any, of it's a chord)
        # (ignore empty noteheads, since there will not be flags)
        if not page.has_inlink_from(o, "notehead-full"):
            continue # ignore weird cases
        notehead = page.get_inlink_from(o, "notehead-full")

        # there will be only one stem, because there is no piece in MPP
        # that would have double-stemmed flag chords
        if not page.has_outlink_to(notehead, "stem"):
            continue # ignore weird cases
        stem = page.get_outlink_to(notehead, "stem")

        # store the flag in the triplets
        extracted_triplets.setdefault(stem.objid, (None, None))
        flag8th, flag16th = extracted_triplets[stem.objid]
        
        if o.clsname == "8th_flag":
            flag8th = o
        elif o.clsname == "16th_flag":
            flag16th = o
        
        extracted_triplets[stem.objid] = (flag8th, flag16th)
    
    # === convert stem-flag-flag triplets to composite flags ===

    glyphs_8th_flag: List[Glyph] = []
    glyphs_16th_flag: List[Glyph] = []
    
    for stem_objid, (flag8th, flag16th) in extracted_triplets.items():
        if flag8th is None:
            continue # due to some error, 8th flag was not present 

        _LABEL_LOOKUP: Dict[Tuple[bool, bool], str] = {
            # (16th?, upward?) -> smufl class
            (False, False): SmuflLabels.flag8thDown.value,
            (False, True): SmuflLabels.flag8thUp.value,
            (True, False): SmuflLabels.flag16thDown.value,
            (True, True): SmuflLabels.flag16thUp.value,
        }
        _ISOLATED_LABEL_LOOKUP: Dict[Tuple[bool, bool], str] = {
            # (16th?, upward?) -> smufl class
            (False, False): SmashcimaLabels.isolatedFlag8thDown.value,
            (False, True): SmashcimaLabels.isolatedFlag8thUp.value,
            (True, False): SmashcimaLabels.isolatedFlag16thDown.value,
            (True, True): SmashcimaLabels.isolatedFlag16thUp.value,
        }

        stem = page.get(stem_objid)

        # determine flag orientation
        stem_center_y = (stem.top + stem.bottom) // 2
        flag_center_y = (flag8th.top + flag8th.bottom) // 2
        is_upward_pointing = stem_center_y >= flag_center_y
        is_16th_flag = flag16th is not None

        # get the flag origin in global pixel coordinates
        stem_points = page.point_cloud.get_points(stem)
        if is_upward_pointing:
            stem_tip_point = stem_points[1]
        else:
            stem_tip_point = stem_points[0]
        global_flag_origin = stem_tip_point.vector + \
            Vector2(stem.left, stem.top)

        # create the composed glyph
        flag_subglyphs: List[Glyph] = []

        def _build_sub_glyph(flag: CropObject, label: str):
            local_flag_origin = (
                global_flag_origin - Vector2(flag.left, flag.top)
            )
            relative_flag_origin = Point(
                local_flag_origin.x / flag.width,
                local_flag_origin.y / flag.height
            )
            space = AffineSpace()
            sprite = Sprite(
                space=space,
                bitmap=_mpp_mask_to_sprite_bitmap(flag.mask),
                bitmap_origin=relative_flag_origin,
                dpi=MUSCIMA_PP_DPI
            )
            sub_glyph = Glyph(
                space=space,
                region=Glyph.build_region_from_sprites_alpha_channel(
                    label=label,
                    sprites=[sprite]
                ),
                sprites=[sprite]
            )
            MppGlyphMetadata.stamp_glyph(sub_glyph, page, int(flag.objid))
            flag_subglyphs.append(sub_glyph)
        
        # add sub-glyphs
        _build_sub_glyph(
            flag8th,
            _ISOLATED_LABEL_LOOKUP[False, is_upward_pointing]
        )
        if is_16th_flag:
            _build_sub_glyph(
                flag16th,
                _ISOLATED_LABEL_LOOKUP[True, is_upward_pointing]
            )

        # finalize the composed glyph
        flag_glyph = ComposedGlyph.build(
            label=_LABEL_LOOKUP[is_16th_flag, is_upward_pointing],
            sub_glyphs=flag_subglyphs
        )
        MppGlyphMetadata.stamp_glyph(
            flag_glyph,
            page,
            int(flag8th.objid) # the composite gets the same ID as the 8th flag
        )
        
        # collect up and split by type
        if flag16th is None:
            glyphs_8th_flag.append(flag_glyph)
        else:
            glyphs_16th_flag.append(flag_glyph)

    return glyphs_8th_flag, glyphs_16th_flag


def get_duration_dots(page: MppPage) -> List[Glyph]:
    return _crop_objects_to_single_sprite_glyphs(
        crop_objects=[
            o for o in page.crop_objects
            if o.clsname == "duration-dot"
        ],
        page=page,
        label=SmuflLabels.augmentationDot.value
    )


def get_staccato_dots(page: MppPage) -> List[Glyph]:
    return _crop_objects_to_single_sprite_glyphs(
        crop_objects=[
            o for o in page.crop_objects
            if o.clsname == "staccato-dot"
        ],
        page=page,
        label=SmuflLabels.articStaccatoBelow.value
    )


def get_accidentals(page: MppPage) -> List[Glyph]:
    _LABEL_LOOKUP: Dict[str, str] = {
        "sharp": SmuflLabels.accidentalSharp.value,
        "flat": SmuflLabels.accidentalFlat.value,
        "natural": SmuflLabels.accidentalNatural.value,
        "double_sharp": SmuflLabels.accidentalDoubleSharp.value,

        # NOTE: there are no double-flats in MUSCIMA++
        "double_flat": SmuflLabels.accidentalDoubleFlat.value
    }

    crop_objects = [
        o for o in page.crop_objects
        if o.clsname in list(_LABEL_LOOKUP.keys())
    ]

    glyphs: List[Glyph] = []
    
    for o in crop_objects:
        # obtain sprite from the center of the inner component
        # and handle open accidentals by repeatedly dilating
        # (dilate vertically twice as much)
        object_center_x, object_center_y = get_center_of_component(o.mask)
        mask = (o.mask * 255).astype(dtype=np.uint8)
        space = AffineSpace()
        sprite: Optional[Sprite] = None
        for i in range(5):
            components = get_connected_components_not_touching_image_border(
                1 - (mask // 255)
            )
            components = sort_components_by_proximity_to_point(
                components,
                object_center_x,
                object_center_y
            )

            if len(components) == 0:
                kernel = np.ones((5, 3), np.uint8)
                mask = cv2.dilate(mask, kernel, iterations=1)
                continue

            component_center_x, component_center_y = get_center_of_component(
                components[0]
            )
            sprite = Sprite(
                space=space,
                bitmap=_mpp_mask_to_sprite_bitmap(o.mask),
                bitmap_origin=Point(
                    component_center_x / o.width,
                    component_center_y / o.height
                ),
                dpi=MUSCIMA_PP_DPI
            )
            break

        # if it didn't succeed, try pulling the center out by the attached note
        if sprite is None and len(o.inlinks) == 1:
            link = page.get(o.inlinks[0])
            if "notehead" in link.clsname:
                sprite = Sprite(
                    space=space,
                    bitmap=_mpp_mask_to_sprite_bitmap(o.mask),
                    bitmap_origin=Point(
                        0.5,
                        (((link.top + link.bottom) / 2) - o.top) / o.height
                    ),
                    dpi=MUSCIMA_PP_DPI
                )

        # still nothing, so resort to the crudest method possible
        if sprite is None:
            if o.clsname in ["flat", "double_flat"]:
                sprite = Sprite(
                    space=space,
                    bitmap=_mpp_mask_to_sprite_bitmap(o.mask),
                    bitmap_origin=Point(0.5, 0.75),
                    dpi=MUSCIMA_PP_DPI
                )
            else:
                sprite = Sprite(
                    space=space,
                    bitmap=_mpp_mask_to_sprite_bitmap(o.mask),
                    bitmap_origin=Point(0.5, 0.5),
                    dpi=MUSCIMA_PP_DPI
                )
        
        glyph = Glyph(
            space=space,
            region=Glyph.build_region_from_sprites_alpha_channel(
                label=_LABEL_LOOKUP[o.clsname],
                sprites=[sprite]
            ),
            sprites=[sprite]
        )
        MppGlyphMetadata.stamp_glyph(glyph, page, o.objid)
        glyphs.append(glyph)

    return glyphs


def get_brackets_and_braces(page: MppPage) -> List[LineGlyph]:
    brackets = _crop_objects_to_line_glyphs(
        crop_objects=[
            o for o in page.crop_objects
            if o.clsname == "multi-staff_bracket"
        ],
        page=page,
        label=SmuflLabels.bracket.value,
        horizontal_line=False, # vertical line
        in_increasing_direction=True # drawn top-to-bottom
    )
    braces = _crop_objects_to_line_glyphs(
        crop_objects=[
            o for o in page.crop_objects
            if o.clsname == "multi-staff_brace"
        ],
        page=page,
        label=SmuflLabels.brace.value,
        horizontal_line=False, # vertical line
        in_increasing_direction=True # drawn top-to-bottom
    )
    glyphs = brackets + braces

    # mis-annotated classes
    _MISTAKES = set([
        # braces that are falsely labeled as brackets
        "MUSCIMA-pp_1.0___CVC-MUSCIMA_W-08_N-10_D-ideal___720",
        "MUSCIMA-pp_1.0___CVC-MUSCIMA_W-08_N-10_D-ideal___721",
        "MUSCIMA-pp_1.0___CVC-MUSCIMA_W-08_N-10_D-ideal___722",
        "MUSCIMA-pp_1.0___CVC-MUSCIMA_W-21_N-05_D-ideal___579",
        "MUSCIMA-pp_1.0___CVC-MUSCIMA_W-24_N-18_D-ideal___282",
        "MUSCIMA-pp_1.0___CVC-MUSCIMA_W-24_N-18_D-ideal___283",
        "MUSCIMA-pp_1.0___CVC-MUSCIMA_W-24_N-18_D-ideal___284",
        "MUSCIMA-pp_1.0___CVC-MUSCIMA_W-41_N-03_D-ideal___458",
        "MUSCIMA-pp_1.0___CVC-MUSCIMA_W-42_N-05_D-ideal___576",

        # brackets that are falsely labeled as braces
        "MUSCIMA-pp_1.0___CVC-MUSCIMA_W-04_N-20_D-ideal___693",
        "MUSCIMA-pp_1.0___CVC-MUSCIMA_W-04_N-20_D-ideal___694",
        "MUSCIMA-pp_1.0___CVC-MUSCIMA_W-21_N-05_D-ideal___580",
        "MUSCIMA-pp_1.0___CVC-MUSCIMA_W-21_N-05_D-ideal___581",
        "MUSCIMA-pp_1.0___CVC-MUSCIMA_W-39_N-20_D-ideal___712",
        "MUSCIMA-pp_1.0___CVC-MUSCIMA_W-39_N-20_D-ideal___713",
        "MUSCIMA-pp_1.0___CVC-MUSCIMA_W-41_N-03_D-ideal___459",
        "MUSCIMA-pp_1.0___CVC-MUSCIMA_W-41_N-03_D-ideal___466",
        "MUSCIMA-pp_1.0___CVC-MUSCIMA_W-42_N-05_D-ideal___577",
        "MUSCIMA-pp_1.0___CVC-MUSCIMA_W-42_N-05_D-ideal___578",
        "MUSCIMA-pp_1.0___CVC-MUSCIMA_W-46_N-20_D-ideal___604",
        "MUSCIMA-pp_1.0___CVC-MUSCIMA_W-46_N-20_D-ideal___714",
    ])
    for g in glyphs:
        meta = MppGlyphMetadata.of_glyph(g)
        if meta.mpp_crop_object_uid in _MISTAKES:
            if g.label == SmuflLabels.brace.value:
                g.label = SmuflLabels.bracket.value
            elif g.label == SmuflLabels.bracket.value:
                g.label = SmuflLabels.brace.value

    return glyphs


def get_time_marks(page: MppPage) -> List[Glyph]:
    _GLYPH_CLASS_LOOKUP: Dict[str, str] = {
        "numeral_0": SmuflLabels.timeSig0.value, # NOT PRESENT
        "numeral_1": SmuflLabels.timeSig1.value, # NOT PRESENT
        "numeral_2": SmuflLabels.timeSig2.value,
        "numeral_3": SmuflLabels.timeSig3.value,
        "numeral_4": SmuflLabels.timeSig4.value,
        "numeral_5": SmuflLabels.timeSig5.value,
        "numeral_6": SmuflLabels.timeSig6.value,
        "numeral_7": SmuflLabels.timeSig7.value,
        "numeral_8": SmuflLabels.timeSig8.value,
        "numeral_9": SmuflLabels.timeSig9.value, # NOT PRESENT
        "whole-time_mark": SmuflLabels.timeSigCommon.value,
        # cut time is not present in MUSCIMA++
    }

    crop_objects = [
        o for o in page.crop_objects
        if o.clsname == "time_signature"
    ]

    glyphs: List[Glyph] = []

    for o in crop_objects:
        for l in o.outlinks:
            outlink = page.get(l)
            if outlink.clsname == "staff":
                continue

            glyphs += _crop_objects_to_single_sprite_glyphs(
                crop_objects=[outlink],
                page=page,
                label=_GLYPH_CLASS_LOOKUP[outlink.clsname]
            )

    return glyphs
