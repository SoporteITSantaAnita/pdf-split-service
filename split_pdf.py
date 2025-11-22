from PyPDF2 import PdfReader, PdfWriter
import io, base64
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/splitpdf", methods=["POST"])
def split_pdf():
    data = request.json
    pdf_base64 = data.get("pdf")
    ranges = data.get("ranges", [])

    if not pdf_base64 or not ranges:
        return jsonify({"error": "Payload inválido. Esperado: { pdf: <base64>, ranges: ['1-2','3'] }"}), 400

    pdf_bytes = base64.b64decode(pdf_base64)
    reader = PdfReader(io.BytesIO(pdf_bytes))

    results = []
    for r in ranges:
        writer = PdfWriter()
        if "-" in r:
            start, end = map(int, r.split("-"))
            for p in range(start-1, end):
                if p < len(reader.pages):
                    writer.add_page(reader.pages[p])
        else:
            page = int(r)-1
            if page < len(reader.pages):
                writer.add_page(reader.pages[page])

        output = io.BytesIO()
        writer.write(output)
        results.append({
            "filename": f"split_{r.replace('-', '_')}.pdf",
            "content": base64.b64encode(output.getvalue()).decode("utf-8")
        })

    return jsonify({"documents": results})
