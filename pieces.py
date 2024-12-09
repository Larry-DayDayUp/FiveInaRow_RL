from PIL import Image, ImageDraw


def create_and_save_piece_image(color, filename, size = 60):
    """
    Generate and save a Go piece image as a PNG file.

    Parameters:
    - color: 'black' or 'white'.
    - filename: Name of the file to save the image.
    - size: Image size (square side length).
    """
    # Create an image with transparent background
    image = Image.new("RGBA", (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)

    # Draw the piece (circle)
    radius = size // 2 - 2  # Padding
    if color == 'black':
        draw.ellipse((2, 2, size - 2, size - 2), fill = 'black', outline = 'black')
    elif color == 'white':
        draw.ellipse((2, 2, size - 2, size - 2), fill = 'white', outline = 'black')

    # Save the image as PNG
    image.save(filename, 'PNG')


# Create and save both black and white pieces
create_and_save_piece_image('black', 'black_piece.png')
create_and_save_piece_image('white', 'white_piece.png')

print("Images saved successfully!")
