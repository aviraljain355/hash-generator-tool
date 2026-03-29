from flask import Flask, render_template, request
import hashlib

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    hash_result = None

    if request.method == "POST":
        file = request.files.get("file")

        if file:
            hash_md5 = hashlib.md5()
            hash_sha1 = hashlib.sha1()
            hash_sha256 = hashlib.sha256()

            while True:
                chunk = file.read(4096)
                if not chunk:
                    break
                hash_md5.update(chunk)
                hash_sha1.update(chunk)
                hash_sha256.update(chunk)

            hash_result = {
                "md5": hash_md5.hexdigest(),
                "sha1": hash_sha1.hexdigest(),
                "sha256": hash_sha256.hexdigest()
            }

    return render_template("index.html", hash_result=hash_result)


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
            
