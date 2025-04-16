from modeltranslation.translator import  register, TranslationOptions

from .models import ShifokorQoshish, Shifokorlar


@register(ShifokorQoshish)
class ShifokorQoshishTranslationOption(TranslationOptions):
    fields = ('ismi', 'familya')


@register(Shifokorlar)
class ShifokorlarTranlationOption(TranslationOptions):
    fields = ('lavozimi', 'mutaxasislik_toifasi', 'oxirgi_malaka_oshirgan_joyi', )