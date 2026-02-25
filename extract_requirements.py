import re

def extract_requirements(text):
    """
    Извлекает требования из текста тендера.
    Возвращает словарь с требованиями для участия.
    """
    requirements = {}

    # 1. Товар / предмет закупки
    product_match = re.search(
        r"(предмет закупки|наименование товара|лоттың атауы|сатып алудың атауы)[:\s]+([^\n\.]{5,60})",
        text, re.IGNORECASE
    )
    if product_match:
        requirements["product"] = product_match.group(2).strip()

    # 2. Бренд
    brand_match = re.search(
        r"\b(Dell|HP|Lenovo|Apple|Samsung|Philips|Siemens|Toyota|BMW|Mercedes|Xerox|Canon|Cisco)\b",
        text, re.IGNORECASE
    )
    if brand_match:
        requirements["brand"] = brand_match.group(1)

    # 3. Модель
    model_match = re.search(
        r"(модель|model)[:\s]+([A-Z0-9][\w\s\-]{2,30})",
        text, re.IGNORECASE
    )
    if model_match:
        requirements["model"] = model_match.group(2).strip()

    # 4. Артикул
    article_match = re.search(
        r"(артикул|арт\.)[:\s]*([\w\-]{4,20})",
        text, re.IGNORECASE
    )
    if article_match:
        requirements["article"] = article_match.group(2).strip()

    # 5. Срок поставки
    delivery_match = re.search(
        r"(срок\s+поставки|жеткізу\s+мерзімі|в\s+течени[еи])[:\s]*([^\n\.]{3,50})",
        text, re.IGNORECASE
    )
    if delivery_match:
        requirements["delivery_deadline"] = delivery_match.group(2).strip()

    # 6. Срок подачи заявок
    submission_match = re.search(
        r"(срок\s+подачи\s+заявок?|өтінімдерді\s+ұсыну\s+мерзімі)[:\s]*([^\n\.]{3,50})",
        text, re.IGNORECASE
    )
    if submission_match:
        requirements["submission_deadline"] = submission_match.group(2).strip()

    # 7. Опыт работы
    experience_match = re.search(
        r"опыт\s+работы[^\d]*(\d+)\s*лет",
        text, re.IGNORECASE
    )
    if experience_match:
        requirements["experience"] = f"не менее {experience_match.group(1)} лет"

    # 8. Сертификат / авторизация
    cert_match = re.search(
        r"(сертификат|авторизованн\w+\s+дилер|уполномоченн\w+\s+партнер)[^\n\.]{0,60}",
        text, re.IGNORECASE
    )
    if cert_match:
        requirements["certificate"] = cert_match.group(0).strip()[:80]

    # 9. Цена
    price_match = re.search(
        r"(цена|стоимость|баға)[^\d]*(\d[\d\s,\.]+)\s*(тенге|тг|₸)",
        text, re.IGNORECASE
    )
    if price_match:
        price_str = re.sub(r"\s", "", price_match.group(2))
        requirements["price"] = f"{price_str} тенге"

    # 10. Количество
    qty_match = re.search(
        r"(количество|саны|кол-во)[:\s]*(\d+)\s*(штук|шт|единиц|дана|ед\.)?",
        text, re.IGNORECASE
    )
    if qty_match:
        unit = qty_match.group(3) or "шт"
        requirements["quantity"] = f"{qty_match.group(2)} {unit}"

    # 11. Гарантия
    warranty_match = re.search(
        r"гарантия[^\d]*(\d+)\s*(лет|год|месяц\w*|ай)",
        text, re.IGNORECASE
    )
    if warranty_match:
        requirements["warranty"] = f"{warranty_match.group(1)} {warranty_match.group(2)}"

    return requirements


# Иконки для каждого поля
REQUIREMENT_LABELS = {
    "product": ("📦", "Предмет закупки"),
    "brand": ("🏷️", "Бренд"),
    "model": ("💻", "Модель"),
    "article": ("🔢", "Артикул"),
    "delivery_deadline": ("⏱️", "Срок поставки"),
    "submission_deadline": ("📅", "Срок подачи заявки"),
    "experience": ("🏆", "Опыт работы"),
    "certificate": ("📜", "Сертификат/Авторизация"),
    "price": ("💰", "Цена"),
    "quantity": ("📊", "Количество"),
    "warranty": ("🛡️", "Гарантия"),
}


# Тест
if __name__ == "__main__":
    test_text = """
    Предмет закупки: Ноутбуки для учебных классов
    Модель: Dell XPS 13 Plus (9320)
    Артикул: XPS9320-7565SLV-PUS
    Срок поставки: в течение 1 рабочего дня с момента подписания договора
    Срок подачи заявок: в течение 2 календарных дней
    Опыт работы не менее 7 лет
    Авторизованный дилер Dell Gold/Platinum Partner Certificate — обязательно
    Цена за единицу: 850,000 тенге
    Количество: 15 единиц
    Гарантия 3 года
    """

    reqs = extract_requirements(test_text)
    print("📋 ЧТО НУЖНО ДЛЯ УЧАСТИЯ:\n")
    for key, value in reqs.items():
        icon, label = REQUIREMENT_LABELS.get(key, ("•", key))
        print(f"{icon} {label}: {value}")
