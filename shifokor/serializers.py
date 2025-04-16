from rest_framework.serializers import ModelSerializer, CharField

from bemor.serializers import ViloyatSerializer
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
        fields = "__all__"


class ShaxsiyMalumotlarModelSerializer(ModelSerializer):
    class Meta:
        model = ShifokorQoshish
        fields = ('id', 'ismi', 'familya', 'otasining_ismi', 'tugilgan_sana', 'jshshir')


class ShifokorListSerializer(ModelSerializer):
    shifokor = ShaxsiyMalumotlarModelSerializer(read_only=True)
    # viloyat = ViloyatSerializer()
    class Meta:
        model = Shifokorlar
        fields = ('shifokor', 'lavozimi', 'mutaxasislik_toifasi',
                  'telefon_raqami', )

class ShifokorListAPISerializer(ModelSerializer):
    shifokor = ShaxsiyMalumotlarModelSerializer(read_only=True)
    # viloyat = ViloyatSerializer()
    birlashtirilgan_ttb = CharField(source='biriktirilgan_muassasa__nomi')
    class Meta:
        model = Shifokorlar
        fields = ('shifokor', 'lavozimi', 'mutaxasislik_toifasi',
                  'telefon_raqami', 'biriktirilgan_muassasa')



class ShifokorDetailModelSerializer(ModelSerializer):
    shifokor = ShaxsiyMalumotlarModelSerializer(read_only=True)

    class Meta:
        model = Shifokorlar
        fields = ('shifokor', 'ish_staji', 'oxirgi_malaka_oshirgan_joyi', 'qayta_malaka_oshirish_vaqti',
                  'mutaxasislik_toifasi', 'telefon_raqami', 'lavozimi')

class ShifokorCreateDetailModelserializer(ModelSerializer):
    shifokor = ShaxsiyMalumotlarModelSerializer(read_only=True)
    class Meta:
        model = Shifokorlar
        fields = ("shifokor","lavozimi","mutaxasislik_toifasi","telefon_raqami",
                   "ish_staji", "oxirgi_malaka_oshirgan_joyi", 'biriktirilgan_muassasa', 'qayta_malaka_oshirish_vaqti')


class ArxivShifokorModelSerializer(ModelSerializer):
    shifokor = ShaxsiyMalumotlarModelSerializer(read_only=True)
    class Meta:
        model = Shifokorlar
        fields = ('shifokor', 'lavozimi', 'mutaxasislik_toifasi', 'telefon_raqami', 'created_at')









