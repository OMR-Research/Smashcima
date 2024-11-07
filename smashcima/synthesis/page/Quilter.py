import numpy as np
import random
import heapq


class Quilter:
    """Service that can be used to quilt small textures up to large dimensions"""
    def __init__(
        self,
        rng: random.Random,
        source_texture_block_size_ratio=1/3,
        overlap_ratio=1/10
    ):
        self.rng = rng
        "Random number generator used for patch sampling"

        self.source_texture_block_size_ratio = source_texture_block_size_ratio
        """How large blocks should be cut from the source texture as a ratio
        of the source texture size"""

        self.overlap_ratio = overlap_ratio
        "How much do the sampled blocks overlap when quilting them together"

    def quilt_texture_to_dimensions(
        self,
        source_texture: np.ndarray,
        target_width_px: int,
        target_height_px: int
    ) -> np.ndarray:
        """
        Given a source texture, it quilts the texture up to the desired size.
        """
        # how large square blocks (in pixels) do we cut from the source texture
        block_size_px = int(
            (min(source_texture.shape[0], source_texture.shape[1]) - 1) \
            * self.source_texture_block_size_ratio
        )

        # how much will the blocks overlap (in pixels)
        overlap_px = int(block_size_px * self.overlap_ratio)
        if overlap_px == 0:
            raise Exception("Quilting block overlap is 0px.")
        
        # how many blocks are there going to be in each direction
        # (make the resulting texture slightly larger and then crop it)
        num_blockHigh = target_height_px // (block_size_px - overlap_px) + 2
        num_blockWide = target_width_px // (block_size_px - overlap_px) + 2

        # prepare the resulting texture (the canvas)
        h = (num_blockHigh * block_size_px) - (num_blockHigh - 1) * overlap_px
        w = (num_blockWide * block_size_px) - (num_blockWide - 1) * overlap_px
        canvas = np.zeros(
            shape=(h, w, source_texture.shape[2]),
            dtype=np.uint8
        )

        # place all blocks
        for i in range(num_blockHigh):
            for j in range(num_blockWide):
                y = i * (block_size_px - overlap_px)
                x = j * (block_size_px - overlap_px)

                # Fast sample and clean cut.
                patch = self.random_patch(source_texture, block_size_px)
                patch = self.overlap_canvas_over_patch(
                    patch, overlap_px, canvas, y, x
                )
                
                canvas[y:y+block_size_px, x:x+block_size_px] = patch
        
        # crop out the desired size randomly from the slightly larger canvas
        over_height = canvas.shape[0] - target_height_px
        over_width = canvas.shape[1] - target_width_px
        offset_height = self.rng.randint(0, over_height)
        offset_width = self.rng.randint(0, over_width)
        return canvas[
            offset_height:target_height_px + offset_height,
            offset_width:target_width_px + offset_width
        ]
    
    def overlap_canvas_over_patch(
        self,
        patch: np.ndarray, 
        overlap: int, 
        canvas: np.ndarray, 
        y: int, 
        x: int
    ) -> np.ndarray:
        patch = patch.copy()
        dy, dx, _ = patch.shape
        minCut = np.zeros_like(patch, dtype=bool)

        if x > 0:
            left = (patch[:, :overlap] - canvas[y:y+dy, x:x+overlap]) / 255.0
            leftL2 = np.sum(left**2, axis=2)
            for i, j in enumerate(self.dijkstra_path(leftL2)):
                minCut[i, :j] = True

        if y > 0:
            up = (patch[:overlap, :] - canvas[y:y+overlap, x:x+dx]) / 255.0
            upL2 = np.sum(up**2, axis=2)
            for j, i in enumerate(self.dijkstra_path(upL2.T)):
                minCut[:i, j] = True

        np.copyto(patch, canvas[y:y+dy, x:x+dx], where=minCut)

        return patch

    def dijkstra_path(
        self,
        errors: np.ndarray
    ):
        """
        Dijkstra's algorithm for finding the shortest path in a graph vertically.
        """
        pq = [(error, [i]) for i, error in enumerate(errors[0])]
        heapq.heapify(pq)

        h, w = errors.shape
        seen = set()

        while pq:
            error, path = heapq.heappop(pq)
            curDepth = len(path)
            curIndex = path[-1]

            if curDepth == h:
                return path

            for delta in -1, 0, 1:
                nextIndex = curIndex + delta

                if 0 <= nextIndex < w:
                    if (curDepth, nextIndex) not in seen:
                        cumError = error + errors[curDepth, nextIndex]
                        heapq.heappush(pq, (cumError, path + [nextIndex]))
                        seen.add((curDepth, nextIndex))
    
    def random_patch(self, source_texture: np.ndarray, block_size_px: int):
        """Take a random square block patch from the source texture"""
        h, w, _ = source_texture.shape
        i = np.random.randint(h - block_size_px)
        j = np.random.randint(w - block_size_px)
        return source_texture[i:i+block_size_px, j:j+block_size_px]
