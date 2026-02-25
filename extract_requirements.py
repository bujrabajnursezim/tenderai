import re


REQUIREMENT_LABELS = {
    "product": ("📦", "Предмет закупки"),
    "brand": ("🏷️", "Бренд"),
    "model": ("💻", "Модель"),
    "article": ("🔢", "Артикул"),
    "cpu": ("🧠", "Процессор"),
    "gpu": ("🎮", "Видеокарта"),
    "ram": ("💾", "Оперативная память"),
    "storage": ("🗄️", "Накопитель"),
    "display": ("🖥️", "Дисплей"),
    "resolution": ("📐", "Разрешение"),
    "os": ("💿", "ОС"),
    "delivery_deadline": ("⏱️", "Срок поставки"),
    "submission_deadline": ("📅", "Срок подачи заявки"),
    "experience": ("🏆", "Опыт работы"),
    "certificate": ("📜", "Сертификат/Авторизация"),
    "price": ("💰", "Цена"),
    "quantity": ("📊", "Количество"),
    "warranty": ("🛡️", "Гарантия"),
}


def _clean(value):
    return re.sub(r"\s+", " ", value).strip(" ,;:.")


def _first_group(text, patterns, group=1, flags=re.IGNORECASE):
    for pattern in patterns:
        m = re.search(pattern, text, flags)
        if m:
            # Some patterns intentionally have no capturing groups.
            # Fall back to group(0) to avoid IndexError on mixed pattern sets.
            if m.lastindex is None or group > m.lastindex:
                return _clean(m.group(0))
            return _clean(m.group(group))
    return None


def _first_match(text, patterns, flags=re.IGNORECASE):
    for pattern in patterns:
        m = re.search(pattern, text, flags)
        if m:
            return _clean(m.group(0))
    return None


def _extract_tech_specs(text):
    specs = {}

    cpu = _first_match(
        text,
        [
            r"\bIntel\s+Core\s+i[3579][-\s]?\d{3,5}[A-Z]{0,2}\b",
            r"\bAMD\s+Ryzen\s+[3579]\s*\d{3,4}[A-Z]{0,2}\b",
            r"\bXeon\s+[A-Z0-9\-]{3,}\b",
            r"(?:процессор|cpu)\s*[:\-]?\s*([^\n,.;]{5,60})",
        ],
    )
    if cpu:
        specs["cpu"] = cpu

    gpu = _first_match(
        text,
        [
            r"\b(?:NVIDIA\s+)?(?:GeForce\s+)?RTX\s*\d{3,4}\s*(?:Ti|SUPER)?\b",
            r"\b(?:NVIDIA\s+)?(?:GeForce\s+)?GTX\s*\d{3,4}\s*(?:Ti)?\b",
            r"\b(?:AMD\s+)?Radeon\s+RX\s*\d{3,4}\s*(?:XT)?\b",
            r"(?:видеокарта|gpu)\s*[:\-]?\s*([^\n,.;]{3,60})",
        ],
    )
    if gpu:
        specs["gpu"] = gpu

    ram = _first_match(
        text,
        [
            r"\b(?:RAM|ОЗУ|оперативн\w+\s+памят\w*)\s*[:\-]?\s*\d{1,3}\s*(?:GB|ГБ)\s*(?:DDR[345])?\b",
            r"\b\d{1,3}\s*(?:GB|ГБ)\s*(?:DDR[345])?\s*(?:RAM|ОЗУ|оперативн\w+\s+памят\w*)\b",
        ],
    )
    if ram:
        specs["ram"] = ram

    storage = _first_match(
        text,
        [
            r"\b(?:SSD|HDD|NVMe)\s*[:\-]?\s*\d+(?:[.,]\d+)?\s*(?:TB|ТБ|GB|ГБ)\b",
            r"\bнакопител\w*\s*[:\-]?\s*(?:SSD|HDD|NVMe)?\s*\d+(?:[.,]\d+)?\s*(?:TB|ТБ|GB|ГБ)\b",
            r"\b\d+(?:[.,]\d+)?\s*(?:TB|ТБ|GB|ГБ)\s*(?:SSD|HDD|NVMe)\b",
        ],
    )
    if storage:
        specs["storage"] = storage

    display = _first_match(
        text,
        [
            r"\b\d{1,2}(?:[.,]\d)?\s*(?:\"|дюйм\w*)\b",
            r"(?:диспле\w*|экран)\s*[:\-]?\s*([^\n,.;]{3,40})",
        ],
    )
    if display:
        specs["display"] = display

    resolution = _first_match(
        text,
        [
            r"\b\d{3,4}\s*[xX×]\s*\d{3,4}\b",
            r"\b(?:Full\s*HD|FHD|QHD|UHD|4K|2K)\b",
        ],
    )
    if resolution:
        specs["resolution"] = resolution

    os_value = _first_match(
        text,
        [
            r"\bWindows\s*(?:10|11)\s*(?:Pro|Home|Enterprise)?\b",
            r"\bLinux\b",
            r"\bUbuntu\b",
            r"\bmacOS\b",
            r"\bAndroid\s*\d{0,2}\b",
            r"\biOS\s*\d{0,2}\b",
        ],
    )
    if os_value:
        specs["os"] = os_value

    return specs


def extract_requirements(text):
    requirements = {}

    product = _first_group(
        text,
        [
            r"(?:предмет закупки|наименование товара|описание товара)\s*[:\-]?\s*([^\n.]{5,120})",
            r"(?:закупка|поставка)\s*([^\n.]{5,80})",
        ],
    )
    if product:
        requirements["product"] = product

    brand = _first_group(
        text,
        [
            r"\b(Dell|HP|Lenovo|Apple|Samsung|Philips|Siemens|Xerox|Canon|Cisco|Huawei|Asus|Acer|MSI|Gigabyte|Intel|AMD|NVIDIA)\b",
        ],
    )
    if brand:
        requirements["brand"] = brand

    model = _first_group(
        text,
        [
            r"(?:модель|model)\s*[:\-]?\s*([A-Z0-9][\w\-/ ]{2,60})",
            r"\b(?:Dell|HP|Lenovo|Apple|Asus|Acer|MSI)\s+[A-Z0-9][\w\- ]{2,40}\b",
        ],
    )
    if model:
        requirements["model"] = model

    article = _first_group(
        text,
        [
            r"(?:артикул|арт\.)\s*[:\-]?\s*([A-Z0-9\-]{4,40})",
            r"\b[A-Z]{2,}[A-Z0-9\-]{4,}\b",
        ],
    )
    if article:
        requirements["article"] = article

    tech_specs = _extract_tech_specs(text)
    for key in ("cpu", "gpu", "ram", "storage", "display", "resolution", "os"):
        if key in tech_specs:
            requirements[key] = tech_specs[key]

    delivery_deadline = _first_group(
        text,
        [
            r"(?:срок\s+поставки|поставка)\s*[:\-]?\s*([^\n.]{3,120})",
            r"(в\s+течение\s+\d+\s+(?:рабоч\w+|календарн\w+)\s+дн\w+)",
        ],
    )
    if delivery_deadline:
        requirements["delivery_deadline"] = delivery_deadline

    submission_deadline = _first_group(
        text,
        [
            r"(?:срок\s+подачи\s+заяв\w+)\s*[:\-]?\s*([^\n.]{3,120})",
            r"(?:прием|приём)\s+заяв\w+\s*[:\-]?\s*([^\n.]{3,120})",
        ],
    )
    if submission_deadline:
        requirements["submission_deadline"] = submission_deadline

    experience = _first_group(
        text,
        [
            r"(?:опыт\s+работы)\s*(?:не\s+менее|от)?\s*(\d+)\s*лет",
            r"(?:опыт\s+работы)\s*[:\-]?\s*([^\n.]{3,60})",
        ],
    )
    if experience:
        requirements["experience"] = f"не менее {experience} лет" if experience.isdigit() else experience

    certificate = _first_match(
        text,
        [
            r"(?:авторизованн\w+\s+дилер|уполномоченн\w+\s+партнер|официальн\w+\s+дистрибьютор)[^\n.]{0,80}",
            r"(?:сертификат|certificate)[^\n.]{0,80}",
        ],
    )
    if certificate:
        requirements["certificate"] = certificate

    price = _first_group(
        text,
        [
            r"(?:цена|стоимость)\s*(?:за\s+единицу)?\s*[:\-]?\s*([\d\s.,]+)\s*(?:тенге|тг|₸)",
        ],
    )
    if price:
        requirements["price"] = f"{re.sub(r'\\s+', '', price)} тенге"

    quantity = _first_group(
        text,
        [
            r"(?:количество|кол-во)\s*[:\-]?\s*(\d+)\s*(?:штук|шт|единиц|ед\.)?",
            r"(\d+)\s*(?:штук|шт|единиц|ед\.)",
        ],
    )
    if quantity:
        requirements["quantity"] = f"{quantity} единиц"

    warranty = _first_group(
        text,
        [
            r"(?:гарантия|гарантийный\s+срок)\s*[:\-]?\s*([^\n.]{2,60})",
            r"(\d+)\s*(?:лет|года|год|месяц\w*)\s*(?:гарантии)?",
        ],
    )
    if warranty:
        requirements["warranty"] = warranty

    return requirements


if __name__ == "__main__":
    sample = """
    Предмет закупки: Ноутбуки для учебных классов
    Модель: Dell XPS 13 Plus
    Артикул: XPS9320-7565SLV-PUS
    Процессор: Intel Core i7-1260P
    Оперативная память: 16 GB DDR5 RAM
    Накопитель: SSD 512 GB
    Видеокарта: GeForce RTX 3060 6 GB
    Экран: 15.6 дюйма, разрешение 1920x1080
    ОС: Windows 11 Pro
    Срок поставки: в течение 1 рабочего дня
    Срок подачи заявки: в течение 2 календарных дней
    Опыт работы не менее 7 лет
    Требуется авторизованный дилер Dell Gold/Platinum
    Цена за единицу: 850,000 тенге
    Количество: 15 единиц
    Гарантия 3 года
    """
    print(extract_requirements(sample))
