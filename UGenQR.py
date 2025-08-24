import qrcode
from PIL import Image, ImageDraw, ImageColor, ImageFilter

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


# --------- Background Cropping (9:16 center crop) ----------
def crop_to_aspect(img, aspect_w=9, aspect_h=16):
    """Crop an image to a specific aspect ratio, centered"""
    w, h = img.size
    target_ratio = aspect_w / aspect_h
    current_ratio = w / h
    if current_ratio > target_ratio:  # too wide → crop width
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        return img.crop((left, 0, left + new_w, h))
    else:  # too tall → crop height
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        return img.crop((0, top, w, top + new_h))


# --------- QR Rendering with Gradient + Shadow + Safe Logo Block ----------
def render_gradient_qr(matrix, color1, color2, shape="square", scale=20, logo_path=None):
    size = len(matrix)
    img_size = size * scale

    # Create QR with solid white background
    qr_img = Image.new("RGBA", (img_size, img_size), "white")
    draw = ImageDraw.Draw(qr_img)

    # Convert colors to RGB
    c1 = ImageColor.getrgb(color1)
    c2 = ImageColor.getrgb(color2)

    # Define safe zone for logo (central blank block)
    safe_size = size // 4        # central area reserved (~25%)
    safe_start = (size - safe_size) // 2
    safe_end = safe_start + safe_size

    for y in range(size):
        for x in range(size):
            # skip central safe area
            if safe_start <= x < safe_end and safe_start <= y < safe_end:
                continue
            if matrix[y][x]:
                ratio = (x + y) / (2 * size)
                r = int(c1[0] + (c2[0]-c1[0]) * ratio)
                g = int(c1[1] + (c2[1]-c1[1]) * ratio)
                b = int(c1[2] + (c2[2]-c1[2]) * ratio)

                x1, y1 = x*scale, y*scale
                x2, y2 = (x+1)*scale, (y+1)*scale
                draw_shape(draw, shape, x1, y1, x2, y2, fill=(r, g, b))

    # Add shadow
    shadow = Image.new("RGBA", (img_size+40, img_size+40), (0,0,0,220))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rectangle([20, 20, img_size+20, img_size+20], fill=(0,0,0,180))
    shadow = shadow.filter(ImageFilter.GaussianBlur(15))

    # Composite shadow + QR
    final_qr = Image.new("RGBA", shadow.size, (255,255,255,0))
    final_qr.paste(shadow, (0,0), shadow)
    final_qr.paste(qr_img, (20,20), qr_img)

    # Place logo in the safe zone
    if logo_path:
        logo = Image.open(logo_path).convert("RGBA")
        logo_size = img_size // 5   # logo ~20% of QR width
        logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)

        # optional: put white background behind logo for visibility
        bg_box = Image.new("RGBA", (logo_size+20, logo_size+20), (255,255,255,230))
        bx = (final_qr.size[0] - bg_box.size[0]) // 2
        by = (final_qr.size[1] - bg_box.size[1]) // 2
        final_qr.paste(bg_box, (bx, by), bg_box)

        # paste logo on top
        lx = (final_qr.size[0] - logo_size) // 2
        ly = (final_qr.size[1] - logo_size) // 2
        final_qr.paste(logo, (lx, ly), logo)

    return final_qr


# --------- Main Program ----------
if __name__ == "__main__":
    text = input("Enter text for QR: ")
    color1 = input("Enter first gradient color (e.g. 'navy' or '#0000ff'): ")
    color2 = input("Enter second gradient color (darker is safer): ")

    print("\nAvailable shapes:")
    shapes = ["square", "rounded_square", "circle", "diamond", "hexagon"]
    print(", ".join(shapes))
    shape = input("Choose a shape: ").strip().lower()
    if shape not in shapes:
        print("⚠ Invalid choice, defaulting to 'square'")
        shape = "square"

    bg_path = input("Enter background image path: ")
    extra_img_path = input("Enter your logo place above QR (leave blank to skip): ").strip()
    logo_path = "my_logo.png"  # <-- replace with your logo file

    # Load & crop background
    bg = Image.open(bg_path).convert("RGB")
    bg = crop_to_aspect(bg, 9, 16)

    # Generate QR matrix
    qr = qrcode.QRCode(
        version=5,  # larger version for safe zone
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4
    )
    qr.add_data(text)
    qr.make(fit=True)
    matrix = qr.get_matrix()

    # Render QR with gradient + shadow + safe logo block
    qr_img = render_gradient_qr(matrix, color1, color2, shape=shape, scale=20, logo_path=logo_path)

    # Resize QR to fit well on background (40% of width)
    qr_size = int(bg.size[0]*0.8)
    qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)

    # Paste QR at center of background
    offset_y = 50
    pos = ((bg.size[0] - qr_size)//2, (bg.size[1] - qr_size)//2 + offset_y)
    bg.paste(qr_img, pos, qr_img)
    # If extra image provided, paste it above the QR
    if extra_img_path:
        extra_img = Image.open(extra_img_path).convert("RGBA")

        # Resize header image to fit width (90% of background width)
        header_w = int(bg.size[0] * 0.3)
        header_h = int(extra_img.size[1] * (header_w / extra_img.size[0]))
        extra_img = extra_img.resize((header_w, header_h), Image.Resampling.LANCZOS)

        # Position above the QR
        qr_x, qr_y = pos
        header_x = (bg.size[0] - header_w) // 2
        header_y = qr_y - header_h - 100   # 20px gap above QR

        # Only paste if there’s space (otherwise overlap occurs)
        if header_y < 0:
            header_y = 0

        bg.paste(extra_img, (header_x, header_y), extra_img)


    bg.save("final_qr_composite.png")
    print("✅ Final QR with background + safe logo saved as final_qr_composite.png")