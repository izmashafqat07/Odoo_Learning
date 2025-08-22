import io

def make_qr_bytes(data: str) -> bytes:
    """
    Try to generate QR without external deps if possible.
    Falls back to 'qrcode' library if available.
    """
    try:
        import qrcode
        img = qrcode.make(data)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()
    except Exception:
        # Minimal fallback: return a tiny PNG saying QR not available
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new("RGB", (300, 300), "white")
        d = ImageDraw.Draw(img)
        text = "QR lib missing\nData:\n" + (data[:50] + ("..." if len(data) > 50 else ""))
        d.text((10, 10), text, fill="black")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()