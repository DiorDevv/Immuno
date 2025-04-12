import datetime

from django.db.models import Model, CharField, IntegerField, DateField, OneToOneField, CASCADE, ForeignKey
from django.db.models.fields import TextField, BooleanField

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
        return f"{self.ismi} {self.familya} {self.otasining_ismi}"


class Shifokorlar(BaseModel):
    shifokor = OneToOneField('ShifokorQoshish', CASCADE, related_name='shifokor')
    lavozimi = CharField(max_length=100)
    mutaxasislik_toifasi = CharField(max_length=100)
    telefon_raqami = CharField(max_length=13)
    biriktirilgan_muassasa = ForeignKey('users.CustomUser', CASCADE, 'shifokorlar')
    ish_staji = IntegerField()
    oxirgi_malaka_oshirgan_joyi = CharField(max_length=150)
    qayta_malaka_oshirish_vaqti = DateField(auto_now=True)
    active = BooleanField(default=False)
    arxiv_sababi = TextField(null=True)
    viloyat = ForeignKey('bemor.Viloyat', CASCADE, 'shifokorlar')

    def __str__(self):
        return f"{self.shifokor}"
