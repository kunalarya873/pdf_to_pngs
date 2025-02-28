import os
import fitz  # PyMuPDF
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "extracted_images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Configure Flask to serve images
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["OUTPUT_FOLDER"] = OUTPUT_FOLDER

# Base URL for accessing images
BASE_URL = "https://pdf-to-pngs.onrender.com/media/"  # Change if deploying on a server


def extract_images(pdf_path, output_folder):
    """Extracts images from a PDF and saves them to a folder."""
    doc = fitz.open(pdf_path)
    extracted_files = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        images = page.get_images(full=True)

        for img_index, img in enumerate(images):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]

            image_filename = f"page_{page_num + 1}_img_{img_index + 1}.{image_ext}"
            image_path = os.path.join(output_folder, image_filename)

            with open(image_path, "wb") as img_file:
                img_file.write(image_bytes)

            extracted_files.append(BASE_URL + image_filename)

    return extracted_files


@app.route("/upload", methods=["POST"])
def upload_pdf():
    """Handles PDF upload and image extraction."""
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    pdf_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(pdf_path)

    extracted_images = extract_images(pdf_path, app.config["OUTPUT_FOLDER"])

    return jsonify({"extracted_images": extracted_images})


@app.route("/media/<filename>")
def serve_image(filename):
    """Serves extracted images."""
    return send_from_directory(app.config["OUTPUT_FOLDER"], filename)


if __name__ == "__main__":
    app.run(debug=True)
