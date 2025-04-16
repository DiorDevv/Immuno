from rest_framework.fields import CharField, ListField, FloatField, FileField
from rest_framework.serializers import ModelSerializer
from .models import AnalizNatijalar, TavsiyaQilinganDorilar, Korik, KorikFile
from dori.serializers import MedicationTypeSerializer, MedicationSerializer
from bemor.models import Bemor

class TavsiyaQilinganDorilarModelSerializer(ModelSerializer):
    dori_turi = CharField(source='dori__name', read_only=True)
    class Meta:
        model = TavsiyaQilinganDorilar
        fields = 'dozasi', 'dori_turi'


class BemorSeansModelSerializer(ModelSerializer):
    ism = CharField(source='bemor.ism')
    familya = CharField(source='bemor.familiya')
    tugilgan_sana = CharField(source='bemor.tugilgan_sana')
    class Meta:
        model = Bemor
        fields = ('id', "ism", "familya", "tugilgan_sana")


class AnalizNatijalarModelSerializer(ModelSerializer):
    class Meta:
        model = AnalizNatijalar
        fields = ("gemoglabin","trombosit","leykosit","eritrosit","limfosit","korik")



class KorikFileModelSerializer(ModelSerializer):
    class Meta:
        model = KorikFile
        fields = 'id', 'file'

class KorikModelSerializer(ModelSerializer):
    bemor = BemorSeansModelSerializer(read_only=True)
    tavsiya_qilingan_dorilar = TavsiyaQilinganDorilarModelSerializer(source='korik_dorilari', many=True)
    analiz_natijalari = AnalizNatijalarModelSerializer(many=True, read_only=True)
    files = KorikFileModelSerializer(many=True)
    upload_files = ListField(
        child=FileField(),
        write_only=True,
        required=False
    )


    class Meta:
        model = Korik
        fields = ("bemor", "korik_otkazilgan_sana", "murojat_turi", "qon_olingan_sana", "qon_analiz_qilingan_sana",
                  "reagent_ishlatildi", "shifokor", "description", 'tavsiya_qilingan_dorilar',
                  'analiz_natijalari', 'upload_files', 'files')


    def create(self, validated_data):
        uploaded_files = validated_data.pop('uploaded_files', [])
        korik = Korik.objects.create(**validated_data)
        for file in uploaded_files:
            KorikFile.objects.create(korik=korik, file=file)
        return korik









