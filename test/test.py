import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from image_processor import process_image


def main():
    image_path = Path(__file__).resolve().parent.parent / "road.jpeg"

    with open(image_path, "rb") as image:
        image_bytes = image.read()

    description = process_image(
        image_bytes=image_bytes,
        mime_type="image/jpeg"
    )

    print("\n--- IMAGE DESCRIPTION ---\n")
    print(description)


if __name__ == "__main__":
    main()