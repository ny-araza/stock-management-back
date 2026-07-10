from django.db import models
from django_filters import rest_framework as filters
from .models import TVente


class VenteFilter(filters.FilterSet):

    vte_valide = filters.NumberFilter()
    vte_paye = filters.NumberFilter()
    vte_datecre_year = filters.NumberFilter(
        field_name="vte_datecre", lookup_expr="year")
    vte_datecre_month = filters.NumberFilter(
        field_name="vte_datecre", lookup_expr="month")

    vte_datemd_year = filters.NumberFilter(
        field_name="vte_datemd", lookup_expr="year")
    vte_datemd_month = filters.NumberFilter(
        field_name="vte_datemd", lookup_expr="month")

    vte_datevalide_year = filters.NumberFilter(
        field_name="vte_datevalide", lookup_expr="year")
    vte_datevalide_month = filters.NumberFilter(
        field_name="vte_datevalide", lookup_expr="month")

    vte_datepay_year = filters.NumberFilter(
        field_name="vte_datepay", lookup_expr="year")
    vte_datepay_month = filters.NumberFilter(
        field_name="vte_datepay", lookup_expr="month")

    ve_dateecheance_year = filters.NumberFilter(
        field_name="ve_dateecheance", lookup_expr="year")
    ve_dateecheance_month = filters.NumberFilter(
        field_name="ve_dateecheance", lookup_expr="month")

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
                "filter_class": filters.DateFilter,
                "extra": lambda f: {
                    "lookup_expr": "date"
                },
            },
        }
