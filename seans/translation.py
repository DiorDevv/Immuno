from modeltranslation.translator import TranslationOptions, register

from .models import Korik


@register(Korik)
class KorikTranslationOptions(TranslationOptions):
    fields = ('murojat_turi', 'description')
