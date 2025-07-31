from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import base64
from io import BytesIO

def handler(request):
    try:
        # Dummy Data for test
        products = [{"name": "Pen", "price": 10}, {"name": "Book", "price": 100}]
        total = sum(p["price"] for p in products)

        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)

        pdf.drawString(100, 800, "🧾 Receipt")
        y = 760
        for p in products:
            pdf.drawString(100, y, f"{p['name']} - ৳{p['price']}")
            y -= 20

        pdf.drawString(100, y - 10, f"Total: ৳{total}")
        pdf.showPage()
        pdf.save()

        buffer.seek(0)
        encoded_pdf = base64.b64encode(buffer.read()).decode("utf-8")

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": f'{{"pdf": "{encoded_pdf}"}}'
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Error: {str(e)}"
        }
