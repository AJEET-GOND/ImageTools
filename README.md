# ImageTools — by AJEET-GOND

A Python command-line utility to resize images and compress them toward a target file size. Built for practical image-preparation tasks such as application forms and document uploads.

**Maintainer profile:** [AJEET-GOND](https://github.com/AJEET-GOND)  
**Repository:** [AJEET-GOND/ImageTools](https://github.com/AJEET-GOND/ImageTools) *(use this URL if you create the repository with this name)*

## Features

- Resize images to a chosen width and height
- Compress images toward a target size in KB
- Interactive prompts for input and output paths
- Supports JPEG, PNG, and WebP images
- Handles common image-mode conversion when exporting JPEG

> **Note:** A target file size is an approximation, not a guarantee. Compression behavior depends on the image and output format. The optional noise step may alter pixels slightly; review the output before submitting important documents.

## Requirements

- Python 3.7+
- Pillow
- NumPy

## Setup

```bash
git clone https://github.com/AJEET-GOND/ImageTools.git
cd ImageTools
python -m pip install -r requirements.txt
python image-tools.py
```

If you have not created the repository on GitHub yet, download or extract this project locally and create a new repository named `ImageTools` under your account first. Then use the matching clone URL above.

## How to use

Run the script:

```bash
python image-tools.py
```

Follow the prompts to enter:

1. Input image path
2. Target width in pixels (`0` to keep the original width)
3. Target height in pixels (`0` to keep the original height)
4. Target file size in KB (`0` to skip size targeting)
5. Optional output path

By default, the processed image is saved with `_modified` added to the original filename.

## Example

```text
Enter the image file path: photo.jpg
Enter target width (pixels): 300
Enter target height (pixels): 400
Enter target file size (KB): 50
```

The script reports the resulting dimensions and file size. Check the output yourself to confirm it meets the requirements of the website or form you are using.

## Project structure

```text
ImageTools/
├── image-tools.py
├── requirements.txt
├── README.md
└── LICENSE
```

## Author and attribution

Personalized project packaging and documentation by **AJEET-GOND**. This project is adapted from the upstream ImageTools project by **Aditya S.** The upstream MIT license and copyright notice are retained in `LICENSE`; see that file for the applicable terms.

- GitHub profile: https://github.com/AJEET-GOND
- Upstream project: https://github.com/xditya/ImageTools

## Contributing

Suggestions and bug reports are welcome through the Issues tab of your repository once it is published.
