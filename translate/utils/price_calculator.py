def calculate_price(text_length: int, rate_per_word: float = 0.000075) -> dict:
    price = round(text_length * rate_per_word,2)
    print(text_length)
    return {"price": price, "text length":text_length}
