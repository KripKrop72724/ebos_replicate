from datetime import datetime

from django.core.validators import MaxValueValidator, MinValueValidator


def validate_year():
    return [MinValueValidator(1900), MaxValueValidator(datetime.now().year + 10)]


def validate_month():
    return [MinValueValidator(1), MaxValueValidator(12)]
