import os
import shutil
import tempfile
import uuid
from pathlib import Path

import pymupdf
from flask import Flask, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename

from local_translator import GLOSSARY, configure_argos, translate_ja_zh
from translate_xlsx_local import process_xlsx


ROOT = Path(__file__).resolve().parent
MODEL_ROOT = Path(os.environ.get("OFFERBOOK_MODEL_ROOT", r"D:\OfferBookLocalModels"))
OUTPUT_ROOT = ROOT / "outputs"
OUTPUT_ROOT.mkdir(exist_ok=True)
configure_argos(str(MODEL_ROOT))

app = Flask(__name__, static_folder=str(ROOT), static_url_path="")
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024


def find_font() -> str | None:
    for candidate in (
        Path(r"C:\Windows\Fonts\msyh.ttc"),
        Path(r"C:\Windows\Fonts\simhei.ttf"),
        Path(r"C:\Windows\Fonts\simsun.ttc"),
    ):
        if candidate.exists():
            return str(candidate)
    return None


def text_blocks(page):
    blocks = []
    for block in page.get_text("blocks"):
        text = " ".join(block[4].split())
        if text and any("\u3040" <= c <= "\u30ff" for c in text):
            blocks.append(text)
    return blocks


def add_text_page(doc, title, pairs, bilingual, font_file):
    page = doc.new_page(width=595, height=842)
    page.insert_font(fontname="cjk", fontfile=font_file)
    page.insert_text((42, 50), title, fontname="cjk", fontsize=15, color=(0.05, 0.2, 0.35))
    y = 78
    for ja, zh in pairs:
        content = f"原文：{ja}\n译文：{zh}" if bilingual else zh
        height = max(48, 18 * (len(content) // 38 + 2))
        if y + height > 810:
            page = doc.new_page(width=595, height=842)
            page.insert_font(fontname="cjk", fontfile=font_file)
            y = 45
        page.insert_textbox(
            pymupdf.Rect(42, y, 553, y + height), content,
            fontname="cjk", fontsize=9.5, lineheight=1.35,
            color=(0.08, 0.08, 0.08),
        )
        y += height + 8


def translate_pdf(source: Path, result_dir: Path):
    font_file = find_font()
    if not font_file:
        raise RuntimeError("未找到可用的中文字体")

    source_doc = pymupdf.open(source)
    translated_pages = []
    count = 0
    for page_number, page in enumerate(source_doc, start=1):
        pairs = []
        for text in text_blocks(page):
            pairs.append((text, translate_ja_zh(text)))
            count += 1
        translated_pages.append((page_number, pairs))

    bilingual = pymupdf.open()
    chinese = pymupdf.open()
    for page_number, pairs in translated_pages:
        if not pairs:
            continue
        add_text_page(bilingual, f"第 {page_number} 页｜日中对照", pairs, True, font_file)
        add_text_page(chinese, f"第 {page_number} 页｜中文翻译", pairs, False, font_file)

    stem = source.stem
    bilingual_name = f"{stem}_双语版.pdf"
    chinese_name = f"{stem}_中文版.pdf"
    (result_dir / bilingual_name).unlink(missing_ok=True)
    (result_dir / chinese_name).unlink(missing_ok=True)
    bilingual.save(result_dir / bilingual_name, deflate=True)
    chinese.save(result_dir / chinese_name, deflate=True)
    bilingual.close()
    chinese.close()
    source_doc.close()
    return bilingual_name, chinese_name, count, len(translated_pages)


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
        return jsonify({"error": "请先选择 PDF 文件"}), 400
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
        "glossary_count": len(GLOSSARY),
        "bilingual_url": f"/outputs/{task_id}/{Path(output['bilingual']).name}",
        "translated_url": f"/outputs/{task_id}/{Path(output['translated']).name}",
    })


@app.get("/outputs/<task_id>/<path:filename>")
def download(task_id, filename):
    return send_from_directory(OUTPUT_ROOT / task_id, filename, as_attachment=True)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("DEMO_PORT", "4173")), debug=False)
