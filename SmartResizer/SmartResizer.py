#
# SmartResizer.py
#
# This is a standalone custom node for ComfyUI.
# It intelligently resizes an image based on its aspect ratio and a user-selected preset,
# with an option to either pad (letterbox) or crop the image to the final dimensions.
# All resizing operations use the high-quality Lanczos filter.
#
# Author: slivik
# Version: 1.4.0 (Fixed padding logic to correctly upscale small images)
#

import torch
import numpy as np
from PIL import Image

class SmartResizer:
    """
    A node that resizes an image to a target resolution preset.
    It checks if the image is closer to a 1:1 or 16:9 aspect ratio and applies
    sizing rules, with a toggle to either pad or crop the image to fit.
    """

    RESOLUTIONS = ["480p", "720p"]
    # Define the resampling filter as a class attribute for consistency and quality.
    # PIL.Image.Resampling.LANCZOS is the modern way to specify this high-quality filter.
    RESAMPLING_METHOD = Image.Resampling.LANCZOS

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "resolution_preset": (s.RESOLUTIONS,),
                "pad_image": ("BOOLEAN", {"default": True, "label_on": "Pad (Letterbox)", "label_off": "Crop to Fit"}),
            }
        }

    RETURN_TYPES = ("IMAGE", "INT", "INT",)
    RETURN_NAMES = ("image", "width", "height",)
    FUNCTION = "process"
    CATEGORY = "slikvik/Image"

    def process(self, image: torch.Tensor, resolution_preset: str, pad_image: bool):
        # The first dimension is the batch size, which we don't need for logic
        # but we need to handle it in the loop.
        _, original_height, original_width, _ = image.shape

        # --- 1. Determine if the image is "Square-ish" ---
        if original_height == 0 or original_width == 0:
            aspect_ratio = 1.0
        else:
            aspect_ratio = original_width / original_height
        
        ar_square = 1.0
        ar_wide_landscape = 16 / 9
        ar_wide_portrait = 9 / 16
        diff_to_square = abs(aspect_ratio - ar_square)
        diff_to_wide = min(abs(aspect_ratio - ar_wide_landscape), abs(aspect_ratio - ar_wide_portrait))
        is_square_ish = diff_to_square < diff_to_wide
        
        print(f"SmartResizer: Original: {original_width}x{original_height}, AR: {aspect_ratio:.2f}, Is Square-ish: {is_square_ish}")

        # --- 2. Determine target dimensions for the NEW image ---
        target_width, target_height = 0, 0
        if resolution_preset == "480p":
            if is_square_ish:
                target_width, target_height = 512, 512
            else:
                if original_width < original_height: # Portrait
                    target_width, target_height = 480, 852
                else: # Landscape
                    target_width, target_height = 852, 480
        elif resolution_preset == "720p":
            if is_square_ish:
                target_width, target_height = 768, 768
            else:
                if original_width < original_height: # Portrait
                    target_width, target_height = 720, 1280
                else: # Landscape
                    target_width, target_height = 1280, 720
                    
        print(f"SmartResizer: Mode: {'Pad' if pad_image else 'Crop'}, Target: {target_width}x{target_height}, Resampling: Lanczos")

        # --- 3. Process the batch of images ---
        processed_images = []
        for img_tensor in image:
            # Note: The original_width/height from the tensor shape is for the whole batch.
            # For robustness, we get dimensions from each individual PIL image.
            pil_img = Image.fromarray(np.clip(255. * img_tensor.cpu().numpy(), 0, 255).astype(np.uint8))
            img_width, img_height = pil_img.size
            
            final_pil_img = None
            if pad_image:
                # --- CORRECTED PADDING LOGIC ---
                # This logic correctly scales the image up or down to fit within
                # the target dimensions while maintaining aspect ratio.
                
                # 1. Calculate the resize ratio
                original_aspect_ratio = img_width / img_height if img_height != 0 else 1
                target_aspect_ratio = target_width / target_height if target_height != 0 else 1

                if original_aspect_ratio > target_aspect_ratio:
                    # Original is wider than target: fit to target_width
                    scaled_width = target_width
                    scaled_height = int(target_width / original_aspect_ratio)
                else:
                    # Original is taller than or same as target: fit to target_height
                    scaled_height = target_height
                    scaled_width = int(target_height * original_aspect_ratio)

                # 2. Resize the image using the calculated dimensions and high-quality filter
                resized_img = pil_img.resize((scaled_width, scaled_height), self.RESAMPLING_METHOD)
                
                # 3. Create a new black background
                background = Image.new('RGB', (target_width, target_height), (0, 0, 0))
                
                # 4. Calculate coordinates to paste the resized image in the center
                paste_x = (target_width - scaled_width) // 2
                paste_y = (target_height - scaled_height) // 2
                
                # 5. Paste the image
                background.paste(resized_img, (paste_x, paste_y))
                final_pil_img = background
            else:
                # --- MANUAL CROPPING LOGIC ---
                # This logic scales to fill the target, then crops the excess.
                # It already handles upscaling correctly.
                if img_width / img_height > target_width / target_height:
                    new_height = target_height
                    new_width = int(img_width * (target_height / img_height))
                else:
                    new_width = target_width
                    new_height = int(img_height * (target_width / img_width))
                
                # Ensure the main resize operation uses the specified Lanczos filter.
                resized_img = pil_img.resize((new_width, new_height), self.RESAMPLING_METHOD)

                left = (new_width - target_width) / 2
                top = (new_height - target_height) / 2
                right = (new_width + target_width) / 2
                bottom = (new_height + target_height) / 2

                final_pil_img = resized_img.crop((left, top, right, bottom))
            
            output_np = np.array(final_pil_img).astype(np.float32) / 255.0
            output_tensor = torch.from_numpy(output_np)
            processed_images.append(output_tensor)
        
        final_batch = torch.stack(processed_images)

        return (final_batch, target_width, target_height,)


# --- ComfyUI Registration ---
NODE_CLASS_MAPPINGS = {
    "SmartResizerNode": SmartResizer
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "SmartResizerNode": "Smart Resizer"
}
