from modeltranslation.translator import register, TranslationOptions
from .models import (
    Viloyat, Tuman, Manzil, OperatsiyaBolganJoy, BemorningHolati,
    BemorQoshish, Bemor
)

@register(Viloyat)
class ViloyatTranslationOptions(TranslationOptions):
    fields = ('nomi',)

@register(Tuman)
class TumanTranslationOptions(TranslationOptions):
    fields = ('nomi', 'tuman_tibbiyot_birlashmasi')

@register(Manzil)
class ManzilTranslationOptions(TranslationOptions):
    fields = ('mamlakat', 'mahalla', 'kocha_nomi')

@register(OperatsiyaBolganJoy)
class OperatsiyaBolganJoyTranslationOptions(TranslationOptions):
    fields = ('mamlakat', 'operatsiya_bolgan_joy', 'transplantatsiya_operatsiyasi')

@register(BemorningHolati)
class BemorningHolatiTranslationOptions(TranslationOptions):
    fields = ('holati', 'ozgarish')

@register(BemorQoshish)
class BemorQoshishTranslationOptions(TranslationOptions):
    fields = ('JSHSHIR', 'ism', 'familiya')

@register(Bemor)
class BemorTranslationOptions(TranslationOptions):
    fields = ('qoshimcha_malumotlar',)


