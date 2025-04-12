import django_filters
from .models import Bemor


class BemorFilter(django_filters.FilterSet):
    tibbiyot_birlashmasi = django_filters.CharFilter(
        field_name='manzil__tuman__tuman_tibbiyot_birlashmasi',
        lookup_expr='icontains',
        label="Tibbiyot birlashmasi"
    )

    class Meta:
        model = Bemor
        fields = ['tibbiyot_birlashmasi']
