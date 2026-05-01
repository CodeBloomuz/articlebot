from aiogram.fsm.state import State, StatesGroup

class ArticleStates(StatesGroup):
    # Maqola turi tanlash
    choosing_type = State()

    # === ODDIY MAQOLA ===
    article_title = State()
    article_language = State()
    article_fullname = State()
    article_university = State()
    article_faculty = State()
    article_direction = State()
    article_course = State()
    article_supervisor = State()
    article_contact = State()
    article_email = State()
    article_confirm = State()
    article_check = State()  # chek yuborish

    # === SCOPUS MAQOLA ===
    scopus_fullname = State()
    scopus_university = State()
    scopus_faculty = State()
    scopus_city_country = State()
    scopus_email = State()
    scopus_orcid = State()
    scopus_confirm = State()
    scopus_check = State()  # chek yuborish
