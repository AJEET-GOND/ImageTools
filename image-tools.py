from PIL import Image
import os
import numpy as np


"""ImageTools — personalized project package for AJEET-GOND.

Adapted from the upstream ImageTools project by Aditya S.
See LICENSE and README.md for attribution and usage terms.
"""


def get_file_size_kb(filepath):
    """Get file size in kilobytes"""
    return os.path.getsize(filepath) / 1024


def add_invisible_noise(img, noise_level=1):
    """
    Add imperceptible noise to an image to increase file size slightly.

    Args:
        img: PIL Image object
        noise_level: Intensity of noise (1-3, where 1 is barely visible)

    Returns:
        PIL Image with added noise
    """
    # Convert image to numpy array
    img_array = np.array(img)

    # Generate random noise with very low amplitude
    noise = np.random.randint(
        -noise_level, noise_level + 1, img_array.shape, dtype=np.int16
    )

    # Add noise to image (with clipping to valid range)
    noisy_array = np.clip(img_array.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    # Convert back to PIL Image
    return Image.fromarray(noisy_array, mode=img.mode)


def resize_and_compress_image(
    input_path, output_path, target_width, target_height, target_size_kb
):
    """
    Resize and compress an image to specified dimensions and file size

    Args:
        input_path: Path to input image
        output_path: Path to save output image
        target_width: Desired width in pixels
        target_height: Desired height in pixels
        target_size_kb: Target file size in kilobytes
    """
    try:
        # Open the image
        img = Image.open(input_path)
        print(f"Original image size: {img.size[0]}x{img.size[1]} pixels")
        print(f"Original file size: {get_file_size_kb(input_path):.2f} KB")

        # Resize the image
        if target_width > 0 and target_height > 0:
            img_resized = img.resize((target_width, target_height), Image.LANCZOS)
            print(f"Resized to: {target_width}x{target_height} pixels")
        else:
            img_resized = img
            print("Keeping original dimensions")

        # Determine the output format
        file_ext = os.path.splitext(output_path)[1].lower()
        if file_ext in [".jpg", ".jpeg"]:
            save_format = "JPEG"
        elif file_ext == ".png":
            save_format = "PNG"
        elif file_ext == ".webp":
            save_format = "WEBP"
        else:
            save_format = "JPEG"
            output_path = os.path.splitext(output_path)[0] + ".jpg"

        # Convert RGBA to RGB if saving as JPEG
        if save_format == "JPEG" and img_resized.mode in ("RGBA", "LA", "P"):
            background = Image.new("RGB", img_resized.size, (255, 255, 255))
            if img_resized.mode == "P":
                img_resized = img_resized.convert("RGBA")
            background.paste(
                img_resized,
                mask=img_resized.split()[-1] if img_resized.mode == "RGBA" else None,
            )
            img_resized = background

        # Compress to target file size using iterative quality adjustment
        if target_size_kb > 0:
            # Start with high quality and fine-tune to get as close as possible
            quality = 95
            tolerance_kb = target_size_kb * 0.02  # 2% tolerance

            # First pass: binary search to get in the ballpark
            min_q, max_q = 1, 95
            while min_q <= max_q:
                mid_q = (min_q + max_q) // 2
                img_resized.save(
                    output_path, format=save_format, quality=mid_q, optimize=True
                )
                current_size = get_file_size_kb(output_path)

                if abs(current_size - target_size_kb) <= tolerance_kb:
                    quality = mid_q
                    break
                elif current_size < target_size_kb:
                    min_q = mid_q + 1
                    quality = mid_q
                else:
                    max_q = mid_q - 1

            # Second pass: fine-tune by testing nearby quality values
            best_quality = quality
            best_size = get_file_size_kb(output_path)
            best_diff = abs(best_size - target_size_kb)

            # Test quality values around the initial estimate
            for test_q in range(max(1, quality - 3), min(96, quality + 4)):
                img_resized.save(
                    output_path, format=save_format, quality=test_q, optimize=True
                )
                test_size = get_file_size_kb(output_path)
                test_diff = abs(test_size - target_size_kb)

                # Prefer results closest to target, with slight preference for staying under
                if test_diff < best_diff or (
                    test_diff == best_diff and test_size <= target_size_kb
                ):
                    best_quality = test_q
                    best_size = test_size
                    best_diff = test_diff

            # Final save with best quality
            img_resized.save(
                output_path, format=save_format, quality=best_quality, optimize=True
            )
            final_size = get_file_size_kb(output_path)

            # If file is significantly smaller than target, add invisible noise
            if final_size < target_size_kb * 0.95:  # More than 5% smaller
                print(
                    f"\nFile size ({final_size:.2f} KB) is smaller than target. Adding invisible noise..."
                )

                noise_level = 1
                max_attempts = 5

                for attempt in range(max_attempts):
                    img_noisy = add_invisible_noise(img_resized, noise_level)
                    img_noisy.save(
                        output_path,
                        format=save_format,
                        quality=best_quality,
                        optimize=True,
                    )
                    new_size = get_file_size_kb(output_path)

                    if new_size >= target_size_kb * 0.98:  # Within 2% of target
                        final_size = new_size
                        print(f"Noise added successfully (level: {noise_level})")
                        break
                    elif new_size > final_size:
                        final_size = new_size
                        img_resized = img_noisy

                    noise_level += 1
                    if noise_level > 3:  # Cap noise level to keep it invisible
                        break

                # If still smaller than target, ask user if they want to add more noise
                while final_size < target_size_kb:
                    print(
                        f"\nCurrent size: {final_size:.2f} KB | Target: {target_size_kb} KB"
                    )
                    user_input = (
                        input(
                            "Add more noise to increase size? (y/yes or n/no/q/0 to stop): "
                        )
                        .strip()
                        .lower()
                    )

                    if user_input in ["n", "no", "q", "0", ""]:
                        print("Stopping noise addition.")
                        break

                    if user_input in ["y", "yes"]:
                        noise_level += 1
                        img_noisy = add_invisible_noise(img_resized, noise_level)
                        img_noisy.save(
                            output_path,
                            format=save_format,
                            quality=best_quality,
                            optimize=True,
                        )
                        new_size = get_file_size_kb(output_path)

                        if new_size > final_size:
                            final_size = new_size
                            img_resized = img_noisy
                            print(
                                f"Added noise (level: {noise_level}) - New size: {final_size:.2f} KB"
                            )
                        else:
                            print(
                                "No significant size increase. Cannot add more noise effectively."
                            )
                            break

                        if final_size >= target_size_kb:
                            print(f"✓ Target size reached!")
                            break
                    else:
                        print("Invalid input. Please enter y/yes or n/no/q/0")

            print(f"Compressed to {final_size:.2f} KB (quality: {best_quality})")
            print(
                f"Target: {target_size_kb} KB - Difference: {abs(final_size - target_size_kb):.2f} KB"
            )
        else:
            # Just save with good quality if no size target
            img_resized.save(output_path, format=save_format, quality=90, optimize=True)
            current_size = get_file_size_kb(output_path)
            print(f"Saved with quality 90: {current_size:.2f} KB")

        print(f"\nImage saved successfully to: {output_path}")
        return True

    except Exception as e:
        print(f"Error processing image: {e}")
        return False


def main():
    print("=" * 60)
    print("IMAGETOOLS | AJEET-GOND")
    print("=" * 60)

    # Get input image path
    input_path = input("\nEnter the image file path: ").strip().strip('"')

    if not os.path.exists(input_path):
        print("Error: File not found!")
        return

    if not os.path.isfile(input_path):
        print("Error: Path is not a file!")
        return

    # Get target dimensions
    print("\n--- Target Dimensions ---")
    print("(Enter 0 for width or height to keep original dimensions)")

    try:
        target_width = int(input("Enter target width (pixels): ").strip() or "0")
        target_height = int(input("Enter target height (pixels): ").strip() or "0")
    except ValueError:
        print("Error: Invalid dimension input!")
        return

    # Get target file size
    print("\n--- Target File Size ---")
    print("(Enter 0 to skip file size compression)")

    try:
        target_size_kb = float(input("Enter target file size (KB): ").strip() or "0")
    except ValueError:
        print("Error: Invalid file size input!")
        return

    # Generate output filename
    base_name = os.path.splitext(input_path)[0]
    extension = os.path.splitext(input_path)[1]
    output_path = f"{base_name}_modified{extension}"

    # Allow user to specify custom output path
    custom_output = (
        input(f"\nOutput file path (press Enter for '{output_path}'): ")
        .strip()
        .strip('"')
    )
    if custom_output:
        output_path = custom_output

    print("\n" + "=" * 60)
    print("PROCESSING IMAGE...")
    print("=" * 60)

    # Process the image
    success = resize_and_compress_image(
        input_path, output_path, target_width, target_height, target_size_kb
    )

    if success:
        print("\n✓ Image processing completed successfully!")
    else:
        print("\n✗ Image processing failed!")


if __name__ == "__main__":
    main()
