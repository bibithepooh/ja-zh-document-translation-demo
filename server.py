import os
import shutil
import uuid
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename

from translate_xlsx_local import TERM_NORMALIZATION, process_xlsx


ROOT = Path(__file__).resolve().parent
OUTPUT_ROOT = ROOT / "outputs"
OUTPUT_ROOT.mkdir(exist_ok=True)

app = Flask(__name__, static_folder=str(ROOT), static_url_path="")
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024


@app.get("/")
def index():
    return app.send_static_file("index.html")


@app.get("/api/status")
def status():
    return jsonify({"ready": True, "engine": "公开样例在线翻译 + Excel 格式保留"})


@app.post("/api/translate")
def translate_document():
    upload = request.files.get("file")
    if not upload or not upload.filename:
        return jsonify({"error": "请先选择 XLSX 文件"}), 400
    if Path(upload.filename).suffix.lower() != ".xlsx":
        return jsonify({"error": "当前作品 Demo 使用 XLSX；请选择 Excel 文件"}), 400

    task_id = uuid.uuid4().hex[:12]
    result_dir = OUTPUT_ROOT / task_id
    result_dir.mkdir(parents=True)
    safe_name = secure_filename(upload.filename) or "source.xlsx"
    source = result_dir / safe_name
    upload.save(source)
    try:
        output = process_xlsx(source, result_dir)
    except Exception as exc:
        shutil.rmtree(result_dir, ignore_errors=True)
        return jsonify({"error": f"处理失败：{exc}"}), 500
    source.unlink(missing_ok=True)
    return jsonify({
        "task_id": task_id,
        "engine": "公开样例在线初译 + 术语校正",
        "sheets": output["sheets"],
        "text_count": output["translated_cells"],
        "glossary_count": len(TERM_NORMALIZATION),
        "bilingual_url": f"/outputs/{task_id}/{Path(output['bilingual']).name}",
        "translated_url": f"/outputs/{task_id}/{Path(output['translated']).name}",
    })


@app.get("/outputs/<task_id>/<path:filename>")
def download(task_id, filename):
    return send_from_directory(OUTPUT_ROOT / task_id, filename, as_attachment=True)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("DEMO_PORT", "4173")), debug=False)
