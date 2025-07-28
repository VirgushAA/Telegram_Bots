import qrcode

def make_qr(command):
    url = f"https://t.me/YourBotUsername?{command}"
    img = qrcode.make(url)
    img.save(f"{command}.png")

make_qr("QRcodes/q1")
make_qr("QRcodes/q2")
make_qr("QRcodes/q3")
