import os
import re
from functools import lru_cache


GLOSSARY = {
    "自動運転": "自动驾驶",
    "運転支援": "驾驶辅助",
    "安全性": "安全性",
    "車両": "车辆",
    "道路": "道路",
    "実証実験": "实证试验",
    "センサー": "传感器",
    "試験": "测试",
    "異常": "异常",
    "ログ": "日志",
}


def configure_argos(model_root: str) -> None:
    base = os.path.abspath(model_root)
    os.environ.setdefault("ARGOS_PACKAGES_DIR", os.path.join(base, "packages"))
    os.environ.setdefault("XDG_DATA_HOME", os.path.join(base, ".argos", "data"))
    os.environ.setdefault("XDG_CONFIG_HOME", os.path.join(base, ".argos", "config"))
    os.environ.setdefault("XDG_CACHE_HOME", os.path.join(base, ".argos", "cache"))
    os.environ.setdefault("ARGOS_CHUNK_TYPE", "MINISBD")


def _normalize(text: str) -> str:
    """统一离线模型的常见译法，不把占位符送入模型。"""
    corrections = {
        "自主驾驶": "自动驾驶",
        "自驾": "自动驾驶",
        "网络安保": "网络安全",
        "准则": "指南",
        "自动驾驶系统维护Daikan": "自动驾驶相关制度建设纲要",
        "QQed区域": "限定区域",
        "humanella": "人为因素",
    }
    result = text
    for old, new in corrections.items():
        result = result.replace(old, new)
    result = re.sub(r"\s*QQ\d*\b", "", result)
    return result.replace(" .", "。").replace(".", "。").replace(",", "，")


@lru_cache(maxsize=512)
def translate_ja_zh(text: str) -> str:
    if not text.strip():
        return text
    from argostranslate import translate

    translated = translate.translate(text.strip(), "ja", "zh")
    return _normalize(translated)
