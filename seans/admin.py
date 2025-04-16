from django.contrib import admin

from bemor.admin import BemorAdmin
from dori.admin import MedicationAdmin
from seans.models import AnalizNatijalar, TavsiyaQilinganDorilar, Korik


@admin.register(AnalizNatijalar)
class AnalizNatijalariModelAdmin(admin.ModelAdmin):
    list_display = ("gemoglabin","trombosit","leykosit","eritrosit","limfosit")


@admin.register(Korik)
class KorikModelAdmin(admin.ModelAdmin):
    bemor = BemorAdmin
    list_display = ("bemor", "korik_otkazilgan_sana", "murojat_turi", "qon_olingan_sana", "qon_analiz_qilingan_sana",
                    "reagent_ishlatildi", "shifokor", "description")


@admin.register(TavsiyaQilinganDorilar)
class TavsiyaQilinganDorilarModelAdmin(admin.ModelAdmin):
    dori = MedicationAdmin
    korik = KorikModelAdmin
    list_display = ("dori", "korik", "dozasi" )
