from django.db import models
from django_filters import rest_framework as filters
from .models import TVente


class VenteFilter(filters.FilterSet):

    vte_valide = filters.NumberFilter()
    vte_paye = filters.NumberFilter()

    class Meta:
        model = TVente
        exclude = [
            "vte_id",
            "ve_proforma",
            "ve_remise",
        ]

        filter_overrides = {
            models.CharField: {
                "filter_class": filters.CharFilter,
                "extra": lambda f: {
                    "lookup_expr": "icontains"
                },
            },

            models.DecimalField: {
                "filter_class": filters.NumberFilter,
            },

            models.DateField: {
                "filter_class": filters.DateFilter,
            },

            models.DateTimeField: {
                "filter_class": filters.DateTimeFilter,
            },
        }
