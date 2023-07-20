

import model_loader as ml

# To detect spam
def isspam(string: str) -> bool:
    """Checks for spam in the given string

    Args:
      string: A string to be checked

    Returns:
      Boolean

    """
    string = [string]
    sen_trans = ml.spam_vect.transform(string)
    prediction = ml.spam_model.predict(sen_trans)[0]  # 0->ham 1->spam
    return True if prediction else False

# -----------------------------------------------#

# To detect hate speech
def ishate(string: str) -> bool:
    """Checks for hate speech in the given string

    Args:
      string: A string to be checked

    Returns:
      Boolean

    """
    string = [string]
    sen_trans = ml.hate_vect.transform(string)
    prediction = ml.hate_model.predict(sen_trans)[0]  # 0->normal 1->toxic
    return True if prediction else False
