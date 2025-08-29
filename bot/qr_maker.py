from PIL import Image, ImageDraw
import qrcode
import io


def generate_qr(url: str, bg_path: str = "../assets/qr_bg.png") -> bytes:
    """
    Generate a QR code with rounded edges, placed inside the white box on a background image.
    Returns image binary (PNG format).
    """

    bg = Image.open(bg_path).convert("RGBA")

    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        border=1
    )
    qr.add_data(url)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")

    box_x, box_y, box_w, box_h = 220, 220, 768, 768
    margin = 25
    qr_size = box_w - 2 * margin
    qr_img = qr_img.resize((qr_size, qr_size), Image.NEAREST)

    radius = 40
    mask = Image.new("L", qr_img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle(
        [(0, 0), qr_img.size],
        radius=radius,
        fill=255
    )
    qr_img.putalpha(mask)

    pos_x = box_x + (box_w - qr_size) // 2
    pos_y = box_y + (box_h - qr_size) // 2
    bg.paste(qr_img, (pos_x, pos_y), qr_img)

    output = io.BytesIO()
    bg.save(output, format="PNG")
    return output.getvalue()
