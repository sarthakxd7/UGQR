---

🎨 Custom QR Code Generator

This project generates beautiful QR codes with gradients, custom shapes, shadows and background images. It’s built with Python, using the qrcode and Pillow (PIL) libraries.
Qrcode library used for generating raw binary matrix for qr.
Pillow library used for rendering and designing the qr code.

---

✨ Features

🔳 Custom shapes for QR modules: square, rounded square, circle, diamond, hexagon.

🌈 Gradient coloring (between two colors).

🖼️ Background image support with automatic 9:16 center cropping.

💡 Drop shadow effect for depth.

🛡️ Safe central logo block to ensure QR remains scannable.

🖋️ Option to place an extra image above the QR (like a header or title).



---

📦 Requirements

Install dependencies with:

pip install qrcode[pil] pillow


---

🚀 Usage

Run the script:

python qr_generator.py

You will be asked for:

1. Text or URL for the QR code.


2. First and second gradient colors (e.g., navy, #0000ff, #ff5733).


3. Shape choice: square, rounded_square, circle, diamond, hexagon.


4. Path to background image (cropped automatically).


5. Optional user logo (placed above QR).




---

📂 Output

The script saves the final composite image as:

final_qr_composite.png

The result looks like:

Gradient-colored QR

Centered on a 9:16 background

Logo placed safely inside QR

Optional header image above QR



---

⚠️ Notes

Use high-contrast gradients (darker colors work better for scanning).

Keep logos small (20–25% of QR size max).

If the header image overlaps, script automatically adjusts position.

Use the required images for your own use

---
