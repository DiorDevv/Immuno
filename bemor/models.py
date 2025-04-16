from django.contrib.auth import get_user_model
from shared.models import BaseModel
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

User = get_user_model()
from django.db import models


class Viloyat(models.Model):
    nomi = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nomi


class Tuman(models.Model):
    viloyat = models.ForeignKey(Viloyat, on_delete=models.CASCADE, related_name="tumanlar")
    nomi = models.CharField(max_length=50)
    tuman_tibbiyot_birlashmasi = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        verbose_name = "Tuman"
        verbose_name_plural = "Tumanlar"
        unique_together = ("viloyat", "nomi")  # Bir viloyatda faqat 1 xil tuman bo‘lishi mumkin

    def __str__(self):
        return f"{self.nomi} ({self.viloyat.nomi})"


class Manzil(models.Model):
    mamlakat = models.CharField(max_length=255, default="O'zbekiston")
    viloyat = models.ForeignKey(Viloyat, on_delete=models.SET_NULL, null=True, blank=True)
    tuman = models.ForeignKey(Tuman, on_delete=models.SET_NULL, null=True, blank=True, related_name="manzil_tumanlari")
    mahalla = models.CharField(max_length=255)
    kocha_nomi = models.CharField(max_length=50)

    class Meta:
        verbose_name = "Manzil"
        verbose_name_plural = "Manzillar"

    def __str__(self):
        return f"{self.mamlakat}, {self.viloyat} - {self.tuman}, {self.mahalla}, {self.kocha_nomi}"


class OperatsiyaBolganJoy(BaseModel):
    mamlakat = models.CharField(max_length=255)
    operatsiya_bolgan_joy = models.CharField(max_length=255)
    transplantatsiya_sana = models.DateField()
    transplantatsiya_operatsiyasi = models.CharField(max_length=255)
    operatsiya_oxirlangan_sana = models.DateField()
    ishlatilgan_miqdor = models.PositiveSmallIntegerField()

    class Meta:
        verbose_name = "Operatsiya joyi"
        verbose_name_plural = "Operatsiya joylari"

    def __str__(self):
        return self.mamlakat


class BemorningHolati(BaseModel):
    holati = models.CharField(max_length=255)
    ozgarish = models.TextField()

    class Meta:
        verbose_name = "Bemor holati"
        verbose_name_plural = "Bemorlar holati"

    def __str__(self):
        return self.holati


class BemorQoshish(BaseModel):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]

    JSHSHIR = models.CharField(
        max_length=14,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\d{14}$',
                message="JSHSHIR faqat 14 ta raqamdan iborat bo‘lishi kerak!"
            )
        ]
    )
    ism = models.CharField(max_length=255)
    familiya = models.CharField(max_length=255)
    tugilgan_sana = models.DateField()
    jinsi = models.CharField(max_length=1, choices=GENDER_CHOICES)

    class Meta:
        verbose_name = "Bemor JSHSHIR"
        verbose_name_plural = "Bemor Bemor JSHSHIR"
        constraints = [
            models.UniqueConstraint(fields=['ism', 'familiya', 'tugilgan_sana'], name='unique_bemor')
        ]

    def __str__(self):
        return f"{self.ism} {self.familiya} - {self.JSHSHIR}"


class Bemor(BaseModel):
    bemor = models.OneToOneField(BemorQoshish, on_delete=models.CASCADE)
    manzil = models.ForeignKey(Manzil, on_delete=models.SET_NULL, null=True, blank=True)
    bemor_holati = models.ForeignKey(BemorningHolati, on_delete=models.CASCADE, null=True, blank=True)
    operatsiya_bolgan_joy = models.ForeignKey(OperatsiyaBolganJoy, on_delete=models.CASCADE, null=True, blank=True)
    biriktirilgan_file = models.FileField(upload_to='media/biriktirilgan/%Y/%m/%d', null=True, blank=True)
    qoshimcha_malumotlar = models.TextField(null=True, blank=True)
    arxivlangan = models.BooleanField(default=True)
    arxiv_sababi = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Bemor"
        verbose_name_plural = "Bemorlar"

    def __str__(self):
        return f"{self.bemor.ism} {self.bemor.familiya} - {self.bemor.JSHSHIR}"


