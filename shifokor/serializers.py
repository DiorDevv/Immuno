from rest_framework.serializers import ModelSerializer, CharField

from shifokor.models import Shifokorlar, ShifokorQoshish
from rest_framework.serializers import ValidationError

class ShifokorQoshishModelSerializer(ModelSerializer):
    class Meta:
        model = ShifokorQoshish
        fields = ['jshshir',]



    def validate_jshshir(self, value):
        if not value.isdigit() or len(value) != 14:
            raise ValidationError("JSHSHIR faqat 14 ta raqamdan iborat bo‘lishi kerak!")

        return value

    def validate(self, attrs):
        jshshir = attrs.get("jshshir")

        shifokor = ShifokorQoshish.objects.filter(jshshir=jshshir).first()
        if shifokor:
            return {
                "jshshir": shifokor.jshshir
            }

        raise ValidationError(
            "Bunday jshshirga ega shifokor mavjud emas"
        )

    def is_valid(self, *, raise_exception=True):
        return super().is_valid(raise_exception=raise_exception)




class ShifokorModelSerializer(ModelSerializer):
    class Meta:
        model = Shifokorlar
        fields = ("shifokor","lavozimi","mutaxasislik_toifasi","telefon_raqami",
                   "ish_staji", "oxirgi_malaka_oshirgan_joyi", 'biriktirilgan_muassasa', 'viloyat')


class ShaxsiyMalumotlarModelSerializer(ModelSerializer):
    class Meta:
        model = ShifokorQoshish
        fields = ('id', 'ismi', 'familya', 'otasining_ismi', 'tugilgan_sana')


class ShifokorListSerializer(ModelSerializer):
    shifokor = ShaxsiyMalumotlarModelSerializer()
    viloyat = CharField(source='viloyat__name')
    class Meta:
        model = Shifokorlar
        fields = ('shifokor', 'lavozimi', 'mutaxasislik_toifasi',
                  'telefon_raqami', 'viloyat')


class ShifokorDetailUpdateModelSerializer(ModelSerializer):
    shifokor = ShaxsiyMalumotlarModelSerializer()

    class Meta:
        model = Shifokorlar
        fields = ('shifokor', 'ish_staji', 'oxirgi_malaka_oshirgan_joyi', 'qayta_malaka_oshirish_vaqti',
                  'mutaxasislik_toifasi')


class ArxivShifokorModelSerializer(ModelSerializer):
    shifokor = ShaxsiyMalumotlarModelSerializer
    class Meta:
        model = Shifokorlar
        fields = ('shifokor', 'lavozimi', 'mutaxasislik_toifasi', 'telefon_raqami', 'arxivga_olingan_sana')









