from flask import Flask, render_template, request, send_file
import hashlib
import os
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

import pandas as pd
def detect_rules(df):
    df["rule_high_amount"] = df["amount"] > 50000
    df["rule_night_time"] = df["time"].astype(str).str.contains("00:|01:|02:|03:")
    df["rule_refund_large"] = (df["type"] == "refund") & (df["amount"] > 10000)

    df["suspicious"] = df[[
        "rule_high_amount",
        "rule_night_time",
        "rule_refund_large"
    ]].any(axis=1)

    return df
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    hash_result = None

    if request.method == "POST":
        file = request.files.get("file")

        if file:
            filename = file.filename

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
                "filename": filename,
                "md5": hash_md5.hexdigest(),
                "sha1": hash_sha1.hexdigest(),
                "sha256": hash_sha256.hexdigest(),
                "time": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            }

            # Store data for certificate
            app.config["LAST_RESULT"] = hash_result

    return render_template("index.html", hash_result=hash_result)


@app.route("/download")
def download():
    data = app.config.get("LAST_RESULT")

    if not data:
        return "No data available. Please generate hash first."

    file_path = "certificate.pdf"

    doc = SimpleDocTemplate(file_path)
    styles = getSampleStyleSheet()

    content = []

    content.append(Paragraph("CERTIFICATE UNDER SECTION 65B OF INDIAN EVIDENCE ACT, 1872", styles["Title"]))
    content.append(Spacer(1, 20))

    content.append(Paragraph("1. I hereby certify that the electronic record was produced from a computer system in the ordinary course of its operation.", styles["Normal"]))
    content.append(Spacer(1, 10))

    content.append(Paragraph(f"2. File Name: {data['filename']}", styles["Normal"]))
    content.append(Paragraph(f"MD5 Hash: {data['md5']}", styles["Normal"]))
    content.append(Paragraph(f"SHA1 Hash: {data['sha1']}", styles["Normal"]))
    content.append(Paragraph(f"SHA256 Hash: {data['sha256']}", styles["Normal"]))
    content.append(Spacer(1, 10))

    content.append(Paragraph(f"3. Date & Time: {data['time']}", styles["Normal"]))
    content.append(Spacer(1, 20))

    content.append(Paragraph("4. This certificate is issued under Section 65B of the Indian Evidence Act, 1872.", styles["Normal"]))
    content.append(Spacer(1, 40))

    content.append(Paragraph("Place: Gwalior", styles["Normal"]))
    content.append(Spacer(1, 20))

    content.append(Paragraph("Adv. Vipul Jain", styles["Normal"]))
    content.append(Paragraph("Cyber Law Consultant", styles["Normal"]))

    doc.build(content)

    return send_file(file_path, as_attachment=True)
    
@app.route("/download_freeze_pdf")
def download_freeze_pdf():
    file_path = "freeze_application.pdf"

    doc = SimpleDocTemplate(file_path)
    styles = getSampleStyleSheet()

    content = []

    content.append(Paragraph("APPLICATION FOR BANK ACCOUNT FREEZE", styles["Title"]))
    content.append(Spacer(1, 20))

    content.append(Paragraph("To,", styles["Normal"]))
    content.append(Paragraph("The Branch Manager,", styles["Normal"]))
    content.append(Paragraph("[Bank Name]", styles["Normal"]))

    content.append(Spacer(1, 10))

    content.append(Paragraph("Subject: Request for freezing of bank account.", styles["Normal"]))

    content.append(Spacer(1, 20))

    content.append(Paragraph("Adv. Vipul Jain", styles["Normal"]))

    doc.build(content)

    return send_file(file_path, as_attachment=True)
    

@app.route("/freeze", methods=["GET", "POST"])
def freeze_tool():
    result = None

    if request.method == "POST":
        file = request.files.get("file")

        if file:
            df = pd.read_csv(file)

            df = detect_rules(df)
            suspicious = df[df["suspicious"]]

            result = suspicious.to_html()

    return render_template("freeze.html", result=result)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

