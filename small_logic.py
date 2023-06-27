def rating(rating_as_num):
    pure_rating = int(rating_as_num)
    decimal_part = rating_as_num - pure_rating
    final_score = "●" * pure_rating
    if decimal_part >= 0.75:
        final_score += "●"
    elif decimal_part >= 0.25:
        final_score += "◐"
    need_to_five = 5 - len(final_score)
    final_score += '○' * need_to_five
    return final_score


