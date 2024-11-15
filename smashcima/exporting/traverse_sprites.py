from smashcima.scene.AffineSpace import AffineSpace
from smashcima.geometry.Transform import Transform
from smashcima.scene.Sprite import Sprite
from typing import Iterator, Tuple


def traverse_sprites(
    space: AffineSpace,
    include_pixels_transform=True,
    include_sprite_transform=True,
    include_root_space_transform=False
) -> Iterator[Tuple[Sprite, Transform]]:
    """
    Given a starting (root) affine space, go through all the sprites in that
    space and return the sprite together with a transform that maps from
    that sprite's affine space (not the sprite space) to the root space.
    The sprite's transform as well as the root space's transform are ignored.
    If you want to include them, you need to chain them with the returned
    transform.
    """

    # yield all sprites in the root space
    for sprite in Sprite.many_of_space(space):
        transform = Transform.identity()
        
        if include_pixels_transform:
            transform = transform.then(
                sprite.get_pixels_to_scene_transform()
            )
        
        if include_sprite_transform:
            transform = transform.then(sprite.transform)
        
        if include_root_space_transform:
            yield (sprite, transform.then(space.transform))
        else:
            yield (sprite, transform)
    
    # recusion into all sub-spaces
    for subspace in space.get_children():
        for (sprite, sprite_transform) in traverse_sprites(
            subspace,
            include_pixels_transform=include_pixels_transform,
            include_sprite_transform=include_sprite_transform,
            include_root_space_transform=False
        ):
            transform = sprite_transform.then(subspace.transform)

            if include_root_space_transform:
                yield (sprite, transform.then(space.transform))
            else:
                yield (sprite, transform)
