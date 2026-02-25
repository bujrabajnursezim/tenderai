import re

def extract_tech_specs(text):
    specs = {}
    patterns = {
        "RAM": [r"(оперативн\w+\s+памят[ьи]|RAM)[^\d]*(\d+)\s*(ГБ|GB|МБ|MB)"],
        "Накопитель": [r"(накопитель|SSD|HDD)[^\d]*(\d+)\s*(ГБ|GB|ТБ|TB)"],
        "Процессор": [r"(Core\s+i[3579]|Ryzen\s+\d|Celeron|Pentium|Xeon)\s*[\-\s]?\w+", r"(процессор|CPU)[:\s]+([^\n,\.]{5,40})"],
        "Видеокарта": [r"(GTX|RTX|Radeon|GeForce)\s+[\w\s]+", r"(видеокарт\w+)[^\d]*(\d+)\s*(ГБ|GB)"],
        "Дисплей": [r"(\d+[,.]?\d*)\s*(дюйм\w*|\'\'|″)"],
        "Разрешение": [r"(\d{3,4}\s*[xX×]\s*\d{3,4})", r"(Full HD|FHD|4K|UHD|HD\+)"],
        "Аккумулятор": [r"(\d+)\s*(мА\*?ч|mAh)"],
        "ОС": [r"(Windows\s+\d+\s*\w*|Linux\s*\w*|Android\s*\d*)"],
        "Камера": [r"(\d+)\s*(Mpx|МП|Mp)"],
        "Частота": [r"(\d+[,.]?\d*)\s*(ГГц|GHz)"],
        "Ядра": [r"(\d+)\s*(ядер|ядра|core\w*)"],
        "Связь": [r"(5G|4G|LTE|Bluetooth\s*\d+[,.]?\d*|Wi-Fi\s*[\d\.]+)"],
        "Защита": [r"(IP\d{2,3}|пыле.*влаго\w*)"],
    }
    for spec_name, spec_patterns in patterns.items():
        for pattern in spec_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                specs[spec_name] = match.group(0).strip()
                break
    return specs


def extract_requirements(text):
    requirements = {}

    product_match = re.search(r"(предмет закупки|наименование товара|лоттың атауы|сатып алудың атауы)[:\s]+([^\n\.]{5,60})", text, re.IGNORECASE)
    if product_match:
        requirements["product"] = product_match.group(2).strip()

    brand_match = re.search(r"\b(Dell|HP|Lenovo|Apple|Samsung|Philips|Siemens|Toyota|BMW|Mercedes|Xerox|Canon|Cisco|Huawei|Asus|Acer)\b", text, re.IGNORECASE)
    if brand_match:
        requirements["brand"] = brand_match.group(1)

    model_match = re.search(r"(модель|model)[:\s]+([A-Z0-9][\w\s\-]{2,30})", text, re.IGNORECASE)
    if model_match:
        requirements["model"] = model_match.group(2).strip()

    article_match = re.search(r"(артикул|арт\.)[:\s]*([\w\-]{4,20})", text, re.IGNORECASE)
    if article_match:
        requirements["article"] = article_match.group(2).strip()

    tech_specs = extract_tech_specs(text)
    if tech_specs:
        requirements["tech_specs"] = tech_specs

    delivery_match = re.search(r"(срок\s+поставки|жеткізу\s+мерзімі|в\s+течени[еи])[:\s]*([^\n\.]{3,80})", text, re.IGNORECASE)
    if delivery_match:
        requirements["delivery_deadline"] = delivery_match.group(2).strip()[:80]

    submission_match = re.search(r"(срок\s+подачи\s+заявок?|өтінімдерді\s+ұсыну\s+мерзімі)[:\s]*([^\n\.]{3,50})", text, re.IGNORECASE)
    if submission_match:
        requirements["submission_deadline"] = submission_match.group(2).strip()

    experience_match = re.search(r"опыт\s+работы[^\d]*(\d+)\s*лет", text, re.IGNORECASE)
    if experience_match:
        requirements["experience"] = f"не менее {experience_match.group(1)} лет"

    cert_match = re.search(r"(авторизованн\w+\s+дилер|уполномоченн\w+\s+партнер|сертификат\s+партнера)[^\n\.]{0,60}", text, re.IGNORECASE)
    if cert_match:
        requirements["certificate"] = cert_match.group(0).strip()[:80]

    price_match = re.search(r"(цена|стоимость|баға)[^\d]*(\d[\d\s,\.]+)\s*(тенге|тг|₸)", text, re.IGNORECASE)
    if price_match:
        price_str = re.sub(r"\s", "", price_match.group(2))
        requirements["price"] = f"{price_str} тенге"

    qty_match = re.search(r"(количество|саны|кол-во)[:\s]*(\d+)\s*(штук|шт|единиц|дана|ед\.)?", text, re.IGNORECASE)
    if qty_match:
        unit = qty_match.group(3) or "шт"
        requirements["quantity"] = f"{qty_match.group(2)} {unit}"

    warranty_match = re.search(r"гарантия[^\d]*(\d+)\s*(лет|год|месяц\w*|ай)", text, re.IGNORECASE)
    if warranty_match:
        requirements["warranty"] = f"{warranty_match.group(1)} {warranty_match.group(2)}"

    return requirements


REQUIREMENT_LABELS = {
    "product": ("📦", "Предмет закупки"),
    "brand": ("🏷️", "Бренд"),
    "model": ("💻", "Модель"),
    "article": ("🔢", "Артикул"),
    "tech_specs": ("⚙️", "Технические характеристики"),
    "delivery_deadline": ("⏱️", "Срок поставки"),
    "submission_deadline": ("📅", "Срок подачи заявки"),
    "experience": ("🏆", "Опыт работы"),
    "certificate": ("📜", "Сертификат/Авторизация"),
    "price": ("💰", "Цена"),
    "quantity": ("📊", "Количество"),
    "warranty": ("🛡️", "Гарантия"),
}

TECH_SPEC_LABELS = {
    "RAM": "💾 RAM",
    "Накопитель": "🗄️ Накопитель",
    "Процессор": "🔲 Процессор",
    "Видеокарта": "🎮 Видеокарта",
    "Дисплей": "🖥️ Дисплей",
    "Разрешение": "📐 Разрешение",
    "Аккумулятор": "🔋 Аккумулятор",
    "ОС": "💿 ОС",
    "Камера": "📷 Камера",
    "Частота": "⚡ Частота",
    "Ядра": "🔩 Ядра",
    "Связь": "📡 Связь",
    "Защита": "🛡️ Защита",
}


if __name__ == "__main__":
    test_text = """
    Предмет закупки: Ноутбуки для учебных классов
    Модель: Dell XPS 13 Plus
    Артикул: XPS9320-7565SLV-PUS
    Процессор: Intel Core i7-1260P 2.1 ГГц 12 ядер
    Оперативная память: 16 GB DDR5
    Накопитель SSD 512 GB
    Видеокарта: GeForce RTX 3060 6 GB
    Дисплей 13.4 дюйма разрешение 3456x2160
    Аккумулятор 5000 мАч
    Windows 11 Pro
    Связь: 5G, Bluetooth 5.3
    Срок поставки: в течение 1 рабочего дня
    Опыт работы не менее 7 лет
    Цена за единицу: 850,000 тенге
    Количество: 15 единиц
    Гарантия 3 года
    """
    reqs = extract_requirements(test_text)
    print("📋 ЧТО НУЖНО ДЛЯ УЧАСТИЯ:\n")
    for key, value in reqs.items():
        if key == "tech_specs":
            print("⚙️  Технические характеристики:")
            for spec_name, spec_value in value.items():
                label = TECH_SPEC_LABELS.get(spec_name, spec_name)
                print(f"    {label}: {spec_value}")
        else:
            icon, label = REQUIREMENT_LABELS.get(key, ("•", key))
            print(f"{icon} {label}: {value}")
