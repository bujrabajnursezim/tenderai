"""Готовый предиктор — импортируй в Streamlit"""
import pickle, re, numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import MinMaxScaler
from extract_requirements import extract_requirements, REQUIREMENT_LABELS
from winner_history import check_winner_history
from legal_compliance import check_legal_compliance, get_legal_summary
embedder = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
with open("model.pkl", "rb") as f: model = pickle.load(f)
with open("scaler.pkl", "rb") as f: scaler = pickle.load(f)

def extract_features(text):
    brand_model_patterns = [
        r"(Dell|HP|Lenovo|Apple|Samsung|Philips|Siemens|Toyota|BMW|Mercedes)\s+\w+[\s\-]\w+",
        r"(строго|исключительно|только)\s+[А-ЯA-Z]\w+",
        r"артикул\s+[\w\-]+",
        r"серийн\w+\s+номер\s+[\w\-]+",
        r"модель\s+[A-Z\d][\w\-]+",
    ]
    brand_count = sum(len(re.findall(p, text, re.IGNORECASE)) for p in brand_model_patterns)
    brand_score = min(brand_count / 3, 1.0)

    restriction_words = ["строго","исключительно","только","авторизованный дилер","официальный представитель","аналоги не принимаются"]
    restriction_score = min(sum(1 for w in restriction_words if w.lower() in text.lower()) / 3, 1.0)

    tight_deadline = bool(re.search(r"(в течени[еи]\s*[1-3]\s*(рабоч|календар)\w+|[1-3]\s*(рабочих|календарных|жұмыс|күнтізбелік)?\s*(дн|день|күн)|за\s*1\s*день|1\s*рабочего\s*дня)", text, re.IGNORECASE))
    
    precise_patterns = [r"\d+[,.]?\d*\s*(ГГц|МГц|ГБ|МБ|GB|дюйм|мм|кг)", r"версия\s+\d+\.\d+", r"\d{3,}[xX×]\d{3,}", r"артикул\s+[\w\-]{4,}", r"[A-Z]{2,}\d{4,}[\w\-]*"]
    precise_score = min(sum(len(re.findall(p, text, re.IGNORECASE)) for p in precise_patterns) / 5, 1.0)

    supplier_patterns = [r"ТОО\s+[\w\s]+", r"БИН\s+\d{12}", r"ИП\s+[\w\s]+"]
    supplier_score = min(sum(len(re.findall(p, text, re.IGNORECASE)) for p in supplier_patterns) / 2, 1.0)

    return {"brand_model": brand_score, "restriction": restriction_score, "tight_deadline": 1.0 if tight_deadline else 0.0, "precise_params": precise_score, "supplier_lock": supplier_score}

def predict_single(text):
    vec = embedder.encode([text])
    raw = model.decision_function(vec)[0]
    anomaly = float(scaler.transform([[-raw]])[0][0])
    feats = extract_features(text)

    # Увеличили веса бренды + ограничители
    risk = round((
        0.10 * anomaly +
        0.35 * feats["brand_model"] +
        0.30 * feats["restriction"] +
        0.10 * feats["tight_deadline"] +
        0.05 * feats["precise_params"] +
        0.10 * feats["supplier_lock"]
    ) * 100, 1)

    if risk >= 70: level, color, rec = "🔴 ВЫСОКИЙ", "red", "Требуется детальная проверка. Возможны признаки ограничения конкуренции."
    elif risk >= 40: level, color, rec = "🟡 СРЕДНИЙ", "orange", "Отдельные признаки специфичности. Рекомендуется дополнительная экспертиза."
    else: level, color, rec = "🟢 НИЗКИЙ", "green", "Документ соответствует стандартным требованиям."

    sentences = re.split(r"[.!?\n]", text)
    suspicious = [s.strip() for s in sentences if len(s.strip()) > 20 and (
        re.search(r"\d+[.,]\d+", s) or
        re.search(r"строго|исключительно|только", s, re.IGNORECASE) or
        re.search(r"[A-Z]{2,}\d+", s)
    )][:5]

    result = {
        "risk_score": risk,
        "level": level,
        "color": color,
        "recommendation": rec,
        "components": {
            "Аномальность текста": round(anomaly*100,1),
            "Бренды и модели": round(feats["brand_model"]*100,1),
            "Слова-ограничители": round(feats["restriction"]*100,1),
            "Жёсткие сроки": round(feats["tight_deadline"]*100,1),
            "Точные параметры": round(feats["precise_params"]*100,1)
        },
        "suspicious_sentences": suspicious,
        "stats": {
            "total_chars": len(text),
            "precise_numbers": len(re.findall(r"\d+[.,]\d+", text)),
            "sentences": len(sentences)
        }
    }

    result['legal'] = check_legal_compliance(text)
    result['legal_summary'] = get_legal_summary(result['legal'])
    result['requirements'] = extract_requirements(text)
    result['requirement_labels'] = REQUIREMENT_LABELS
    result['winners'] = check_winner_history(text)
    return result