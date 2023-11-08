from sqlalchemy import func
from sqlalchemy.orm.attributes import InstrumentedAttribute


def my_lower(attribute: InstrumentedAttribute):
    return func.replace(func.replace(func.replace(func.replace(func.replace(func.replace(func.replace(func.replace(func.replace(func.lower(attribute), "Á", "á"), "É", "é"), "Í", "í"), "Ó", "ó"), "Ö", "ö"), "Ő", "ő"), "Ú", "ú"), "Ü", "ü"), "Ű", "ű")
