from django.db.models import Model, FloatField, ForeignKey, CASCADE, DateField, CharField, BooleanField, FileField, \
    TextField, IntegerField

from shared.models import BaseModel


class AnalizNatijalar(BaseModel):
    gemoglabin = FloatField()
    trombosit = FloatField()
    leykosit = FloatField()
    eritrosit = FloatField()
    limfosit = FloatField()
    korik = ForeignKey('Korik', CASCADE, related_name='analiz_natijalari')




class Korik(BaseModel):
    bemor = ForeignKey('bemor.Bemor', CASCADE, related_name='seanslar')
    korik_otkazilgan_sana = DateField(auto_now=True)
    murojat_turi = CharField(max_length=255)
    qon_olingan_sana = DateField(auto_now=True)
    qon_analiz_qilingan_sana = DateField(auto_now=True)
    reagent_ishlatildi = BooleanField(db_default=False)
    shifokor = ForeignKey('shifokor.Shifokorlar', CASCADE, related_name='koriklar')
    # biriktirilgan_fayllar = FileField()
    description = TextField()

    def __str__(self):
        return f"{self.id}"


class KorikFile(Model):
    file = FileField()
    korik = ForeignKey('seans.Korik', CASCADE, related_name='files')


class TavsiyaQilinganDorilar(BaseModel):
    dori = ForeignKey('dori.MedicationType', CASCADE)
    korik = ForeignKey('Korik', CASCADE, 'korik_dorilari')
    dozasi = IntegerField()


