from datetime import timedelta
from email.policy import default

from django.db import models
from django.db.models import Sum, CASCADE
from django.utils import timezone

from bemor.models import Bemor
from shared.models import BaseModel


class MedicationType(BaseModel):
    name = models.CharField(max_length=100, unique=True)

    class Meta:

        verbose_name = "Dori Turi"
        verbose_name_plural = "Dori Turlari"

    def __str__(self):
        return self.name


from django.db import models
from django.db.models import Sum

class Medication(BaseModel):
    type = models.ForeignKey(
        MedicationType,
        verbose_name='Dori',
        on_delete=models.CASCADE,
        related_name='medications',
        null=True,  # Agar type ba'zan bo'sh bo'lishi mumkin bo'lsa
        blank=True
    )
    name = models.CharField(max_length=100)
    dosage = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    dosage_unit = models.CharField(max_length=10, default='mg')

    def __str__(self):
        dosage_str = f"{self.dosage}{self.dosage_unit}" if self.dosage is not None else "No dosage"
        return f"{self.name} {dosage_str}"

    def total_input(self):
        return self.inventory_transactions.filter(transaction_type='INPUT').aggregate(
            total=Sum('quantity'))['total'] or 0

    def total_output(self):
        return self.inventory_transactions.filter(transaction_type='OUTPUT').aggregate(
            total=Sum('quantity'))['total'] or 0

    def balance(self):
        return self.total_input() - self.total_output()

    def warehouse_quantity(self):
        return self.balance()

    class Meta:
        verbose_name = "Dori"
        verbose_name_plural = "Dorilar"




class InventoryTransaction(BaseModel):
    TRANSACTION_TYPES = [
        ('INPUT', 'Kirim'),
        ('OUTPUT', 'Chiqim'),
    ]

    medication = models.ForeignKey(Medication, on_delete=models.CASCADE, related_name='inventory_transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    quantity = models.PositiveIntegerField()
    date = models.DateTimeField()
    notes = models.TextField(blank=True, null=True)
    archived = models.BooleanField(default=False)
    patient = models.ForeignKey(Bemor, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='medication_transactions')

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.medication.name} - {self.quantity}"

    class Meta:
        ordering = ['-date']
        verbose_name = "Kirim Chiqim"
        verbose_name_plural = "Kirim Chiqimlar"


class MedicationDetails(BaseModel):
    """Additional details about medications that can be displayed in the info panel"""
    medication = models.OneToOneField(Medication, on_delete=models.CASCADE, related_name='details')
    description = models.TextField(blank=True)
    usage_instructions = models.TextField(blank=True)
    side_effects = models.TextField(blank=True)
    contraindications = models.TextField(blank=True)
    storage_instructions = models.TextField(blank=True)

    def __str__(self):
        return f"Details for {self.medication}"

    class Meta:
        verbose_name = "Dori detail"
        verbose_name_plural = "Dori details"

class MedicationPrescription(BaseModel):
    patient = models.ForeignKey(Bemor, on_delete=models.CASCADE, related_name='prescriptions')
    prescription_date = models.DateField()
    prescription_number = models.CharField(max_length=20)
    institution = models.CharField(max_length=100)
    doctor = models.CharField(max_length=100)
    reason = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"#{self.prescription_number}"

    class Meta:
        ordering = ['-prescription_date']
        verbose_name = "Qabul qilish bo'yicha malumot"
        verbose_name_plural = "Qabul qilish bo'yicha malumotlar"

class TavsiyaEtilganDori(BaseModel):
    # dori_turi = models.ForeignKey(MedicationType, on_delete=models.CASCADE, related_name='medications_type')
    bemor = models.ForeignKey(Bemor, on_delete=CASCADE, related_name='tavsiya_etilgan_dori')
    dori_nomi = models.ForeignKey(Medication, on_delete=models.CASCADE)
    kunlik_doza = models.FloatField()
    miqdori = models.PositiveIntegerField()
    seria_raqam = models.CharField(max_length=20, blank=True)
    qabul_qilish_muddati = models.PositiveIntegerField(help_text="Duration in days")
    boshlanish = models.DateField()
    tugallanish = models.DateField()
    yaroqlilik_muddati = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.dori_nomi.name} - {self.kunlik_doza}{self.dori_nomi.dosage_unit}"

    @property
    def is_active(self):
        today = timezone.now().date()
        return self.boshlanish <= today <= self.tugallanish

class QabulQilishYakuniy(BaseModel):

    preparatni_qabul_qilish_sanasi = models.DateTimeField(
        verbose_name="Preparatni qabul qilish sanasi",

    )
    preparatni_qabul_qilish_muddati = models.PositiveIntegerField(
        verbose_name="Preparatni qabul qilish muddati (kun)",
        default=1
    )
    oxirgi_qabul_qilish_sanasi = models.DateTimeField(
        verbose_name="Preparatni oxirgi qabul qilish sanasi",

    )

    def save(self, *args, **kwargs):

        if not self.oxirgi_qabul_qilish_sanasi:
            self.oxirgi_qabul_qilish_sanasi = (
                self.preparatni_qabul_qilish_sanasi +
                timezone.timedelta(days=self.preparatni_qabul_qilish_muddati)
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Medication Acceptance from {self.preparatni_qabul_qilish_sanasi}"

    class Meta:
        verbose_name = "Dori qabul qilish yakuniy ma'lumot"
        verbose_name_plural = "Dori qabul qilish yakuniy ma'lumotlar"
#  Notifications
class Notification(BaseModel):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('accepted', 'Qabul qilindi'),
        ('rejected', 'Rejected'),
    )

    TYPE_CHOICES = (
        ('entry', 'Entry'),
        ('exit', 'Exit'),
    )

    id = models.AutoField(primary_key=True)
    notification_type = models.CharField("Notification Type", max_length=10, choices=TYPE_CHOICES, default='entry')
    message = models.CharField("Ma'lumot", max_length=255)
    quantity = models.IntegerField("Miqdori", default=10)
    status = models.CharField(
        "Status",
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    # Fields for detailed view
    medication = models.ForeignKey(
        Medication,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name="Medication"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        return f"{self.id} - {self.message}"


class Attachment(BaseModel):

    # notification = models.ForeignKey(
    #     Notification,
    #     on_delete=models.CASCADE,
    #     related_name='attachments',
    #     verbose_name="Notification"
    # )
    file = models.FileField("File", upload_to='notifications/')
    name = models.CharField("Name", max_length=255)
    uploaded_at = models.DateTimeField("Uploaded At", auto_now_add=True)

    def __str__(self):
        return self.name








