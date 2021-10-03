class CountryNotFoundError(ValueError):
    """Исключение. Используется, когда данная страна не найдена в базе."""
    def __init__(self, country_name):
        self.message = f"There is no country {country_name} in our database!"
        super().__init__(self.message)


class RegionNotFoundError(ValueError):
    """Исключение. Используется, когда данный регион не найден в базе."""
    def __init__(self, region):
        self.message = f"There is no region {region} in our database!"
        super().__init__(self.message)


class ArticleNotFoundError(ValueError):
    """Исключение. Используется, когда статья на сайте МИД с данным ключевым фрагментом отсутствует"""
    def __init__(self, article_name):
        self.message = f"There is no article with such key part of the name: {article_name}"
        super().__init__(self.message)


class CountryInfoNotFoundError(ValueError):
    """Исключение. Используется, когда информация о стране в данной статье отсутствует"""
    def __init__(self):
        self.message = f"There is no country info in the article"
        super().__init__(self.message)


class UnknownCoronaInfoType(ValueError):
    """Исключение. Используется, когда использовал неизвестный тип информации о коронавирусе в стране"""
    def __init__(self, info_type):
        self.message = f"Corona info type {info_type} is not supported"
        super().__init__(self.message)
