import qrcode
from PIL import Image, ImageDraw, ImageColor

# --------- Shape Functions ----------
def draw_shape(draw, shape, x1, y1, x2, y2, fill):
    """Draws a safe shape inside the bounding box"""
    if shape == "square":
        draw.rectangle([x1, y1, x2, y2], fill=fill)

    elif shape == "rounded_square":
        draw.rounded_rectangle([x1, y1, x2, y2], radius=(x2-x1)//4, fill=fill)

    elif shape == "circle":
        draw.ellipse([x1, y1, x2, y2], fill=fill)

    elif shape == "diamond":
        midx, midy = (x1+x2)//2, (y1+y2)//2
        draw.polygon([(midx, y1), (x2, midy), (midx, y2), (x1, midy)], fill=fill)
    
    elif shape == "hexagon":
        w, h = x2-x1, y2-y1
        draw.polygon([
            (x1+w*0.25, y1), (x1+w*0.75, y1),
            (x2, y1+h*0.5), (x1+w*0.75, y2),
            (x1+w*0.25, y2), (x1, y1+h*0.5)
        ], fill=fill)


# --------- QR Rendering with Gradient + Safe Background ----------
def render_gradient_qr(matrix, color1, color2, shape="square", scale=20, output="styled_qr.png", background_path=None):
    size = len(matrix)
    img_size = size * scale

    # Create QR image with solid white background
    qr_img = Image.new("RGB", (img_size, img_size), "white")
    draw = ImageDraw.Draw(qr_img)

    # Convert colors to RGB
    c1 = ImageColor.getrgb(color1)
    c2 = ImageColor.getrgb(color2)

    for y in range(size):
        for x in range(size):
            if matrix[y][x]:
                ratio = (x + y) / (2 * size)
                r = int(c1[0] + (c2[0]-c1[0]) * ratio)
                g = int(c1[1] + (c2[1]-c1[1]) * ratio)
                b = int(c1[2] + (c2[2]-c1[2]) * ratio)

                x1, y1 = x*scale, y*scale
                x2, y2 = (x+1)*scale, (y+1)*scale
                draw_shape(draw, shape, x1, y1, x2, y2, fill=(r, g, b))

    # If background is provided, paste QR on top (keeping white safe zone intact)
    if background_path:
        bg = Image.open(background_path).convert("RGB")

        # Make background larger than QR
        scale_factor = 1.5
        bg_size = int(img_size * scale_factor)
        bg = bg.resize((bg_size, bg_size), Image.Resampling.LANCZOS)

        # Center QR on background
        offset = ((bg_size - img_size) // 2, (bg_size - img_size) // 2)
        bg.paste(qr_img, offset)  # no mask → QR stays opaque (white safe zone preserved)
        final_img = bg
    else:
        final_img = qr_img

    final_img.save(output)
    print(f"✅ QR saved as {output}")


# --------- Main Program ----------
if __name__ == "__main__":
    text = input("Enter text for QR: ")
    color1 = input("Enter first gradient color (e.g. 'navy' or '#0000ff'): ")
    color2 = input("Enter second gradient color (darker is safer): ")

    print("\nAvailable safe shapes:")
    shapes = ["square", "rounded_square", "circle", "diamond", "hexagon"]
    print(", ".join(shapes))
    shape = input("Choose a shape: ").strip().lower()
    if shape not in shapes:
        print("⚠️ Invalid choice, defaulting to 'square'")
        shape = "square"

    bg_choice = input("Do you want to add a background image? (y/n): ").strip().lower()
    bg_path = None
    if bg_choice == "y":
        bg_path = input("Enter background image path: ")

    # Generate raw QR matrix
    qr = qrcode.QRCode(
        version=3,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4
    )
    qr.add_data(text)
    qr.make(fit=True)
    matrix = qr.get_matrix()

    # Render with gradient + shape + safe background
    render_gradient_qr(matrix, color1, color2, shape=shape, output="custom_qr.png", background_path=bg_path)
