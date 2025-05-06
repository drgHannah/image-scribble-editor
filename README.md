# Image Scribble Editor

A lightweight Gradio-based application to browse a directory of images, draw binary scribble masks over them, and save those masks for later use (e.g., segmentation, annotation).
<div align="center">
  <img src="demo.gif" width="600px" />
</div>







## 🚀 Getting Started


1. **Clone this repository**  
   ```bash
   git clone https://github.com/yourusername/image-scribble-editor.git
   cd image-scribble-editor
   ```


2. **Install dependencies in an environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

    Requires: `gradio`, `Pillow`, `numpy`




## ✏️ Usage

1. **Prepare your images**
   
   Place all your source images in `[path_to_dataset]/images/`.
   Example:

   ```
   [path_to_dataset]/images/cat1.jpg
   [path_to_dataset]/images/dog2.png
   ```

2. **Run the editor**

   ```bash
   python main.py --datapath [path_to_dataset]
   ```

   * `--datapath` points to the folder containing the two subfolders `images/` and `alpha/`.
   * If `alpha/` does not exist, it will be created automatically.

3. **Draw and save**

   * Use the left‐right arrows to navigate between images.
   * Draw scribbles in the left “Draw Scribbles” panel.
   * Click **Save Scribbles** to export a mask (`alpha/imagename.png`) and update the overlay on the right.



## Directory Structure

```
dataset-root/
├── images/    # Put your source images here (png/jpg/jpeg/bmp)
└── alpha/     # Mask output directory (created automatically)
```

