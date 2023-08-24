from enum import Enum


class I18nLang(str, Enum):
    ZH_CN = "zh-cn"
    ZH_TW = "zh-tw"
    DE_DE = "de-de"
    EN_US = "en-us"
    ES_ES = "es-es"
    FR_FR = "fr-fr"
    ID_ID = "id-id"
    IT_IT = "it-it"
    JA_JP = "ja-jp"
    KO_KR = "ko-kr"
    PT_PT = "pt-pt"
    RU_RU = "ru-ru"
    TH_TH = "th-th"
    TR_TR = "tr-tr"
    VI_VN = "vi-vn"


i18n_alias = {
    "zh": I18nLang.ZH_CN,
    "tw": I18nLang.ZH_TW,
    "de": I18nLang.DE_DE,
    "en": I18nLang.EN_US,
    "es": I18nLang.ES_ES,
    "fr": I18nLang.FR_FR,
    "id": I18nLang.ID_ID,
    "it": I18nLang.IT_IT,
    "ja": I18nLang.JA_JP,
    "ko": I18nLang.KO_KR,
    "pt": I18nLang.PT_PT,
    "ru": I18nLang.RU_RU,
    "th": I18nLang.TH_TH,
    "tr": I18nLang.TR_TR,
    "vi": I18nLang.VI_VN,
}
i18n_map = {
    I18nLang.ZH_CN: {
        "view": "查看原文",
        "author": "作者信息",
    },
    I18nLang.ZH_TW: {
        "view": "查看原文",
        "author": "作者信息",
    },
    I18nLang.DE_DE: {
        "view": "Originaltext anzeigen",
        "author": "Informationen zum Autor",
    },
    I18nLang.EN_US: {
        "view": "View Original",
        "author": "Author Information",
    },
    I18nLang.ES_ES: {
        "view": "Ver original",
        "author": "Información del autor",
    },
    I18nLang.FR_FR: {
        "view": "Voir l'original",
        "author": "Informations sur l'auteur",
    },
    I18nLang.ID_ID: {
        "view": "Lihat aslinya",
        "author": "Informasi penulis",
    },
    I18nLang.IT_IT: {
        "view": "Visualizza originale",
        "author": "Informazioni sull'autore",
    },
    I18nLang.JA_JP: {
        "view": "元の記事を見る",
        "author": "作者情報",
    },
    I18nLang.KO_KR: {
        "view": "원본 보기",
        "author": "작성자 정보",
    },
    I18nLang.PT_PT: {
        "view": "Ver original",
        "author": "Informações do autor",
    },
    I18nLang.RU_RU: {
        "view": "Посмотреть оригинал",
        "author": "Информация об авторе",
    },
    I18nLang.TH_TH: {
        "view": "ดูต้นฉบับ",
        "author": "ข้อมูลผู้เขียน",
    },
    I18nLang.TR_TR: {
        "view": "Orijinali Görüntüle",
        "author": "Yazar Bilgisi",
    },
    I18nLang.VI_VN: {
        "view": "Xem bản gốc",
        "author": "Thông tin tác giả",
    },
}


class I18n:
    def __init__(self, lang: str = "zh-cn"):
        self.lang = I18nLang(lang)

    def get_property(self, name: str):
        return i18n_map.get(self.lang, {}).get(name, "")

    def __getitem__(self, item):
        return self.get_property(item)

    @property
    def lang_alias(self) -> str:
        for k, v in i18n_alias.items():
            if v == self.lang:
                return k
