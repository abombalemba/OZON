class Card:
    def __init__(self, id: int, url: str, title: str, description: str, price: int,
                 rating_value: float, rating_counter: float, image_url: str):
        self.id: int = id
        self.url: str = url
        self.title: str = title
        self.description: str = description
        self.price: int = price
        self.rating_value: float = rating_value
        self.rating_counter: float = rating_counter
        self.image_url: str = image_url

    __doc__ = 'Карточка товара на маркетплейсе Ozon'
