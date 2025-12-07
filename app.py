from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from backgroundremover.bg import remove
import io
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"  # flash messages ke liye

# Max upload size (approx 8 MB)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/remove", methods=["POST"])
def remove_bg():
    if "file" not in request.files:
        flash("No file part")
        return redirect(url_for("index"))

    file = request.files["file"]

    if file.filename == "":
        flash("No selected file")
        return redirect(url_for("index"))

    if not allowed_file(file.filename):
        flash("Only JPG, JPEG and PNG images are allowed.")
        return redirect(url_for("index"))

    try:
        input_bytes = file.read()

        # Background remove call
        output_bytes = remove(
            input_bytes,
            model_name="u2net",              # general objects
            alpha_matting=True,
            alpha_matting_foreground_threshold=240,
            alpha_matting_background_threshold=10,
            alpha_matting_erode_structure_size=10,
            alpha_matting_base_size=1000
        )

        return send_file(
            io.BytesIO(output_bytes),
            mimetype="image/png",
            as_attachment=True,
            download_name="no-bg.png"
        )
    except Exception as e:
        print("Error:", e)
        flash("Error while processing image. Try a smaller/clearer image.")
        return redirect(url_for("index"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
