"""
Image Scribble Editor

A simple Gradio-based tool to browse a folder of images, draw binary scribbles
(mask overlays) on them, and save the resulting scribble masks alongside the originals.
"""

import gradio as gr
import argparse
import os
from PIL import Image
import numpy as np


def main():
    """
    Entry point for the Image Scribble Editor.

    Parses command-line arguments to locate the image directory, sets up the
    Gradio interface with navigation controls, an image editor for drawing
    scribbles, and buttons to navigate between images and save scribble masks.
    """
    parser = argparse.ArgumentParser(description="Image Scribble Editor")
    parser.add_argument(
        "--datapath",
        type=str,
        default="images",
        help="Path to root image directory containing 'images/' subfolder",
    )
    args = parser.parse_args()
    folder = args.datapath

    # Define image and scribble directories
    image_dir = os.path.join(folder, "images")
    scribble_dir = os.path.join(folder, "alpha")
    os.makedirs(scribble_dir, exist_ok=True)

    # Gather your images
    image_files = sorted(
        f for f in os.listdir(image_dir)
        if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp"))
    )
    if not image_files:
        raise ValueError(f"No images found in '{image_dir}'")

    # Count totals
    total_images = len(image_files)
    scribble_files = sorted(
        f for f in os.listdir(scribble_dir)
        if f.lower().endswith(".png")
    )
    scribble_count = len(scribble_files)

    with gr.Blocks() as demo:
        idx_state = gr.State(0)  # current image index

        def _scribble_path(name: str) -> str:
            """
            Construct the expected scribble-mask filepath for a given image name.

            Args:
                name: Filename of the original image.

            Returns:
                Full path to the corresponding scribble PNG in the alpha folder.
            """
            base, _ = os.path.splitext(name)
            return os.path.join(scribble_dir, f"{base}.png")

        def _has_scribble(name: str) -> bool:
            """
            Check whether a scribble mask already exists for the given image.

            Args:
                name: Filename of the original image.

            Returns:
                True if the mask file exists on disk, False otherwise.
            """
            return os.path.exists(_scribble_path(name))

        def _status_text(name: str) -> str:
            """
            Generate a status string indicating whether the scribble exists.

            Args:
                name: Filename of the original image.

            Returns:
                A green bullet if scribble exists, red if not.
            """
            return "🟢 Scribble exists" if _has_scribble(name) else "🔴 No scribble yet"

        def _overlay_image(
            rgb_img: Image.Image,
            scribble_img: Image.Image | None,
            alpha: float = 0.7
        ) -> Image.Image:
            """
            Blend the original image with its scribble mask for preview.

            Args:
                rgb_img: The original RGB image.
                scribble_img: The scribble mask as an RGB image (white strokes on gray).
                alpha: Blend factor (0 = only original, 1 = only mask).

            Returns:
                A PIL.Image showing the overlay.
            """
            if scribble_img is None:
                return rgb_img
            return Image.blend(rgb_img, scribble_img, alpha=alpha)

        # Load initial image + overlay
        initial_name = image_files[0]
        initial_img = Image.open(os.path.join(image_dir, initial_name)).convert("RGB")
        initial_scribble = (
            Image.open(_scribble_path(initial_name)).convert("RGB")
            if _has_scribble(initial_name)
            else None
        )
        initial_overlay = _overlay_image(initial_img, initial_scribble)

        # UI layout
        with gr.Row():
            filename_display = gr.Textbox(
                value=initial_name, label="Image", interactive=True
            )
            scribble_mark = gr.Textbox(
                value=_status_text(initial_name),
                label="Scribble Status",
                interactive=False
            )

        with gr.Row():
            editor = gr.ImageEditor(
                value={"background": initial_img, "layers": [], "composite": initial_img},
                type="pil",
                label="Draw Scribbles",
                brush=gr.Brush(colors=["#000000", "#CCCCCC"], color_mode="fixed"),
                height=868, scale=1.0, elem_id="custom-image-editor",
                layers=False,
                placeholder="Draw your scribbles on the image to the left..."
            )
            existing_display = gr.Image(
                value=initial_overlay,
                label="Overlay: Image + Scribble",
                interactive=False,
                height=868
            )

        with gr.Row():
            prev_btn = gr.Button("←")
            next_btn = gr.Button("→")
            save_btn = gr.Button("Save Scribbles")


        # New: load any image by typing its filename
        def load_by_name(name: str, idx: int):
            # if user typed something invalid, keep everything as-is and show error
            if name not in image_files:
                #return idx, gr.no_update, name, "❌ Image not found", gr.no_update
                return navigate(0, 0)
            # otherwise jump to that index (step=0 just reloads)
            return navigate(image_files.index(name), 0)

        # # wire it up
        # filename_display.change(
        #     fn=load_by_name,
        #     inputs=[filename_display, idx_state],
        #     outputs=[idx_state, editor, filename_display, scribble_mark, existing_display]
        # )
        filename_display.submit(
            fn=load_by_name,
            inputs=[filename_display, idx_state],
            outputs=[idx_state, editor, filename_display, scribble_mark, existing_display]
        )

        status = gr.Textbox(label="Status", interactive=False)
        output_text = gr.Textbox(
            label="Project Path",
            value=os.path.abspath(folder),
            interactive=False
        )

        with gr.Row():
            total_count_display = gr.Textbox(
                value=str(total_images),
                label="Total Images",
                interactive=False
            )
            scribble_count_display = gr.Textbox(
                value=str(scribble_count),
                label="Scribble Images",
                interactive=False
            )

        def navigate(idx: int, step: int):
            """
            Move forwards or backwards through the image list.

            Args:
                idx: Current index in image_files.
                step: +1 to go next, -1 to go previous.

            Returns:
                Tuple of (new_idx, editor_state, filename, status_text, overlay_image).
            """
            new_idx = max(0, min(idx + step, len(image_files) - 1))
            name = image_files[new_idx]
            img = Image.open(os.path.join(image_dir, name)).convert("RGB")

            has_sb = _has_scribble(name)
            sb_img = (
                Image.open(_scribble_path(name)).convert("RGB")
                if has_sb else None
            )
            overlay = _overlay_image(img, sb_img)

            editor_state = {"background": img, "layers": [], "composite": img}

            return new_idx, editor_state, name, _status_text(name), overlay

        prev_btn.click(
            fn=lambda idx: navigate(idx, -1),
            inputs=[idx_state],
            outputs=[idx_state, editor, filename_display, scribble_mark, existing_display]
        )
        next_btn.click(
            fn=lambda idx: navigate(idx, 1),
            inputs=[idx_state],
            outputs=[idx_state, editor, filename_display, scribble_mark, existing_display]
        )

        def save_scribbles(editor_value: dict, name: str):
            """
            Save the user’s scribble layers as a binary mask PNG.

            Args:
                editor_value: Dictionary containing 'layers' list of PIL images.
                name: Current image filename to base the mask filename on.

            Returns:
                A tuple of (status_message, new_overlay_image, updated_scribble_count).
            """
            layers = editor_value["layers"]
            # Count before save
            current = sorted(f for f in os.listdir(scribble_dir) if f.lower().endswith(".png"))
            before_count = len(current)

            if not layers:
                return "No scribbles to save.", None, str(before_count)

            # Merge all layers
            w, h = layers[0].size
            canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            for layer in layers:
                canvas = Image.alpha_composite(canvas, layer.convert("RGBA"))

            # Convert scribbles to white-on-transparent mask
            gray_bg = Image.new("RGBA", (w, h), (128, 128, 128, 255))
            flat = Image.alpha_composite(gray_bg, canvas).convert("RGB")
            arr = np.array(flat)
            bg_col = np.array([128, 128, 128])
            black_col = np.array([0, 0, 0])
            mask = np.any(arr != bg_col, axis=-1)
            non_black = ~np.all(arr == black_col, axis=-1)
            to_white = mask & non_black
            arr[to_white] = [255, 255, 255]
            final = Image.fromarray(arr)

            # Save mask
            base, _ = os.path.splitext(name)
            outpath = os.path.join(scribble_dir, f"{base}.png")
            final.save(outpath)

            # Create new overlay preview
            orig = Image.open(os.path.join(image_dir, name)).convert("RGB")
            overlay = _overlay_image(orig, final)

            # Count after save
            updated = sorted(f for f in os.listdir(scribble_dir) if f.lower().endswith(".png"))
            after_count = len(updated)

            return f"Scribbles saved to: {outpath}", overlay, str(after_count), _status_text(initial_name)

        save_btn.click(
            fn=save_scribbles,
            inputs=[editor, filename_display],
            outputs=[status, existing_display, scribble_count_display, scribble_mark]
        )

    demo.launch()


if __name__ == "__main__":
    main()
