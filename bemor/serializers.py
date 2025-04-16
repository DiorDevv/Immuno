from rest_framework import serializers

from .models import BemorQoshish, Manzil, OperatsiyaBolganJoy, BemorningHolati, Bemor, Viloyat, Tuman
import re
from django.utils import timezone
import os


class ViloyatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Viloyat
        fields = "__all__"


class TumanSerializer(serializers.ModelSerializer):
    viloyat_nomi = serializers.CharField(source="viloyat.nomi", read_only=True)

    class Meta:
        model = Tuman
        fields = ["id", "nomi", "viloyat", "viloyat_nomi", "tuman_tibbiyot_birlashmasi"]


class BemorQoshishSerializer(serializers.ModelSerializer):
    class Meta:
        model = BemorQoshish
        fields = ['JSHSHIR', 'ism', 'familiya', 'tugilgan_sana', 'jinsi']

    def validate_JSHSHIR(self, value):
        if not value.isdigit() or len(value) != 14:
            raise serializers.ValidationError("JSHSHIR faqat 14 ta raqamfdan iborat bo‘lishi kerak!")

        return value

    def validate(self, attrs):
        JSHSHIR = attrs.get("JSHSHIR")
        ism = attrs.get("ism")
        familiya = attrs.get("familiya")
        tugilgan_sana = attrs.get("tugilgan_sana")

        bemor = BemorQoshish.objects.filter(JSHSHIR=JSHSHIR).first()
        if bemor:
            return {
                "JSHSHIR": bemor.JSHSHIR,
                "ism": bemor.ism,
                "familiya": bemor.familiya,
                "tugilgan_sana": bemor.tugilgan_sana,
                "jinsi": bemor.jinsi,
            }

        if BemorQoshish.objects.filter(ism=ism, familiya=familiya, tugilgan_sana=tugilgan_sana).exists():
            raise serializers.ValidationError(
                {"detail": "Bunday ism, familiya va tug‘ilgan sanaga ega bemor allaqachon mavjud!"}
            )

        return attrs


class ManzilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manzil
        fields = "__all__"

    def validate_mamlakat(self, value):
        ruxsat_berilgan_davlatlar = ["O'zbekiston", "Rossiya", "AQSh", "Qozog'iston", "Turkiya"]
        if value not in ruxsat_berilgan_davlatlar:
            raise serializers.ValidationError("Bu davlatga ruxsat berilmagan.")
        return value

    def validate_hudud(self, value):
        if not re.match(r"^[a-zA-Z\s'-]+$", value):
            raise serializers.ValidationError("Hudud faqat harflardan iborat bo‘lishi kerak.")
        return value

    def validate_kocha_nomi(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Ko'cha nomi kamida 3 ta belgidan iborat bo‘lishi kerak.")
        return value

    def validate_biriktirilgan_tuman(self, value):
        if not value.strip():
            raise serializers.ValidationError("Biriktirilgan tuman maydoni bo‘sh bo‘lishi mumkin emas.")
        return value


class OperatsiyaBolganJoySerializer(serializers.ModelSerializer):
    class Meta:
        model = OperatsiyaBolganJoy
        fields = '__all__'


class BemorningHolatiSerializer(serializers.ModelSerializer):
    class Meta:
        model = BemorningHolati
        fields = '__all__'


class BemorSerializer(serializers.ModelSerializer):
    # ID larni faqat yozish uchun ishlatamiz (write_only=True)
    bemor = serializers.PrimaryKeyRelatedField(queryset=BemorQoshish.objects.all(), write_only=True)
    bemor_holati = serializers.PrimaryKeyRelatedField(queryset=BemorningHolati.objects.all(), write_only=True)
    manzil = serializers.PrimaryKeyRelatedField(queryset=Manzil.objects.all(), required=False, allow_null=True,
                                                write_only=True)
    operatsiya_bolgan_joy = serializers.PrimaryKeyRelatedField(queryset=OperatsiyaBolganJoy.objects.all(),
                                                               required=False, allow_null=True, write_only=True)

    # Ob'ektlarni olish uchun serializerlar (read_only=True)
    bemor_detail = BemorQoshishSerializer(source='bemor', read_only=True)
    bemor_holati_detail = BemorningHolatiSerializer(source='bemor_holati', read_only=True)
    manzil_detail = ManzilSerializer(source='manzil', read_only=True)
    operatsiya_bolgan_joy_detail = OperatsiyaBolganJoySerializer(source='operatsiya_bolgan_joy', read_only=True)

    class Meta:
        model = Bemor
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')

        if request and request.method == 'POST':
            # POST so‘rovdan so‘ng yangi ID qaytarish
            return {
                "id": instance.id,  # Nechanchi bemor bo‘lib qo‘shilgani
                "bemor": data.get('bemor_detail'),
                "bemor_holati": data.get('bemor_holati_detail'),
                "manzil": data.get('manzil_detail'),
            }
        elif request and request.parser_context['kwargs'].get('pk'):
            # Detail (ID bilan)
            data['bemor'] = data.pop('bemor_detail', None)
            data['bemor_holati'] = data.pop('bemor_holati_detail', None)

        else:
            # List (ID'siz faqat `bemor` va `bemor_holati`)
            data = {
                "bemor": data.pop('bemor_detail', None),
                "bemor_holati": data.pop('bemor_holati_detail', None)
            }
        return data

    def validate_biriktirilgan_file(self, value):
        if value:
            ext = os.path.splitext(value.name)[1].lower()
            allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
            max_size = 5 * 1024 * 1024  # 5MB gacha ruxsat
            if ext not in allowed_extensions:
                raise serializers.ValidationError("Faqat PDF yoki JPG formatdagi fayllarga ruxsat berilgan!")
            if value.size > max_size:
                raise serializers.ValidationError("Fayl hajmi 5MB dan oshib ketdi!")
        return value

    def validate(self, data):
        errors = {}

        if not data.get('bemor'):
            errors['bemor'] = "Bemor maydoni bo‘sh bo‘lishi mumkin emas!"

        if errors:
            raise serializers.ValidationError(errors)

        return data
