from flask import Flask, render_template, request
import hashlib

app = Flask(__name__)

# ✅ THIS FUNCTION MUST BE PRESENT
def calculate_hashes(file):
    md5 = hashlib.md5()
    sha1 = hashlib.sha1()
    sha256 = hashlib.sha256()

   chunk = file.read(4096)
while chunk:
    md5.update(chunk)
    sha1.update(chunk)
    sha256.update(chunk)
    chunk = file.read(4096)

    return {
        "md5": md5.hexdigest(),
        "sha1": sha1.hexdigest(),
        "sha256": sha256.hexdigest()
    }


@app.route('/', methods=['GET', 'POST'])
def index():
    hashes = None

    if request.method == 'POST':
        file = request.files['file']
        if file:
            hashes = calculate_hashes(file)  # ✅ SAME NAME

    return render_template('index.html', hashes=hashes)



import os

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
