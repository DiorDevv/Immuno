import datetime

from django.db.models import Model, CharField, IntegerField, DateField, OneToOneField, CASCADE, ForeignKey

from shared.models import BaseModel


class ShifokorQoshish(BaseModel):

    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]

    jshshir = CharField(max_length=14)
    familya = CharField(max_length=50)
    ismi = CharField(max_length=50)
    otasining_ismi = CharField(max_length=50)
    jinsi = CharField(max_length=1, choices=GENDER_CHOICES)
    tugilgan_sana = DateField()

    def __str__(self):
        return f"{self.ismi} {self.familya} {self.jshshir}"


class Shifokorlar(BaseModel):
    shifokor = OneToOneField('ShifokorQoshish', CASCADE, related_name='shifokor')
    lavozimi = CharField(max_length=100)
    mutaxasislik_toifasi = CharField(max_length=100)
    telefon_raqami = CharField(max_length=13)
    biriktirilgan_muassasa = CharField(null=True)
    ish_staji = IntegerField()
    oxirgi_malaka_oshirgan_joyi = CharField(max_length=150)
    qayta_malaka_oshirish_vaqti = DateField(auto_now=True)
    arxivga_olingan_sana = DateField(null=True)
    viloyat = ForeignKey('bemor.Viloyat', CASCADE, 'shifokorlar')

    def __str__(self):
        return f"{self.shifokor}"
