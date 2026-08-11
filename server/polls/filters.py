from django.db import models
from django_filters import rest_framework as filters
import django_filters

from .models import (
    TArticle,
    TClient,
    TCmdFournis,
    TEntree,
    TFournis,
    TInStock,
    TMvtStock,
    TOutStock,
    TRetourClient,
    TRetourFournis,
    TVente,
)


class ClientFilter(filters.FilterSet):
    cli_enabled = filters.NumberFilter()
    cli_datecre_year = filters.NumberFilter(
        field_name="cli_datecre", lookup_expr="year"
    )
    cli_datecre_month = filters.NumberFilter(
        field_name="cli_datecre", lookup_expr="month"
    )

    cli_datemd_year = filters.NumberFilter(field_name="cli_datemdf", lookup_expr="year")
    cli_datemd_month = filters.NumberFilter(
        field_name="cli_datemdf", lookup_expr="month"
    )

    class Meta:
        model = TClient
        exclude = ["cli_id", "cli_nif", "cli_stat", "cli_rcs", "cli_type"]

        filter_overrides = {
            models.CharField: {
                "filter_class": filters.CharFilter,
                "extra": lambda f: {"lookup_expr": "icontains"},
            },
            models.DecimalField: {
                "filter_class": filters.NumberFilter,
            },
            models.DateField: {
                "filter_class": filters.DateFilter,
            },
            models.DateTimeField: {
                "filter_class": filters.DateFilter,
                "extra": lambda f: {"lookup_expr": "date"},
            },
        }


class VenteFilter(filters.FilterSet):
    vte_valide = filters.NumberFilter()
    vte_paye = filters.NumberFilter()
    vte_datecre_year = filters.NumberFilter(
        field_name="vte_datecre", lookup_expr="year"
    )
    vte_datecre_month = filters.NumberFilter(
        field_name="vte_datecre", lookup_expr="month"
    )

    vte_datemd_year = filters.NumberFilter(field_name="vte_datemd", lookup_expr="year")
    vte_datemd_month = filters.NumberFilter(
        field_name="vte_datemd", lookup_expr="month"
    )

    vte_datevalide_year = filters.NumberFilter(
        field_name="vte_datevalide", lookup_expr="year"
    )
    vte_datevalide_month = filters.NumberFilter(
        field_name="vte_datevalide", lookup_expr="month"
    )

    vte_datepay_year = filters.NumberFilter(
        field_name="vte_datepay", lookup_expr="year"
    )
    vte_datepay_month = filters.NumberFilter(
        field_name="vte_datepay", lookup_expr="month"
    )

    ve_dateecheance_year = filters.NumberFilter(
        field_name="ve_dateecheance", lookup_expr="year"
    )
    ve_dateecheance_month = filters.NumberFilter(
        field_name="ve_dateecheance", lookup_expr="month"
    )

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
                "extra": lambda f: {"lookup_expr": "icontains"},
            },
            models.DecimalField: {
                "filter_class": filters.NumberFilter,
            },
            models.DateField: {
                "filter_class": filters.DateFilter,
            },
            models.DateTimeField: {
                "filter_class": filters.DateFilter,
                "extra": lambda f: {"lookup_expr": "date"},
            },
        }


class BcFilter(filters.FilterSet):
    cmf_isLivre = filters.NumberFilter()
    cmf_enabled = filters.NumberFilter()
    cmf_datecre_year = filters.NumberFilter(
        field_name="cmf_datecre", lookup_expr="year"
    )
    cmf_datecre_month = filters.NumberFilter(
        field_name="cmf_datecre", lookup_expr="month"
    )

    cmf_datemd_year = filters.NumberFilter(field_name="cmf_datemdf", lookup_expr="year")
    cmf_datemd_month = filters.NumberFilter(
        field_name="cmf_datemdf", lookup_expr="month"
    )

    cmf_dateliv_year = filters.NumberFilter(
        field_name="cmf_dateliv", lookup_expr="year"
    )
    cmf_dateliv_month = filters.NumberFilter(
        field_name="cmf_dateliv", lookup_expr="month"
    )

    cmf_date_year = filters.NumberFilter(field_name="cmf_date", lookup_expr="year")
    cmf_date_month = filters.NumberFilter(field_name="cmf_date", lookup_expr="month")

    class Meta:
        model = TCmdFournis
        exclude = [
            "cmf_id",
        ]

        filter_overrides = {
            models.CharField: {
                "filter_class": filters.CharFilter,
                "extra": lambda f: {"lookup_expr": "icontains"},
            },
            models.DecimalField: {
                "filter_class": filters.NumberFilter,
            },
            models.DateField: {
                "filter_class": filters.DateFilter,
            },
            models.DateTimeField: {
                "filter_class": filters.DateFilter,
                "extra": lambda f: {"lookup_expr": "date"},
            },
        }


class FournisseurFilter(filters.FilterSet):
    fou_enabled = filters.NumberFilter()
    fou_datecre_year = filters.NumberFilter(
        field_name="fou_datecre", lookup_expr="year"
    )
    fou_datecre_month = filters.NumberFilter(
        field_name="fou_datecre", lookup_expr="month"
    )

    fou_datemdf_year = filters.NumberFilter(
        field_name="fou_datemdf", lookup_expr="year"
    )
    fou_datemdf_month = filters.NumberFilter(
        field_name="fou_datemdf", lookup_expr="month"
    )

    class Meta:
        model = TFournis
        exclude = [
            "fou_id",
        ]

        filter_overrides = {
            models.CharField: {
                "filter_class": filters.CharFilter,
                "extra": lambda f: {"lookup_expr": "icontains"},
            },
            models.DecimalField: {
                "filter_class": filters.NumberFilter,
            },
            models.DateField: {
                "filter_class": filters.DateFilter,
            },
            models.DateTimeField: {
                "filter_class": filters.DateFilter,
                "extra": lambda f: {"lookup_expr": "date"},
            },
        }


class ArticleFilter(filters.FilterSet):
    art_enabled = filters.NumberFilter()
    art_datecre_year = filters.NumberFilter(
        field_name="art_datecre", lookup_expr="year"
    )
    art_datecre_month = filters.NumberFilter(
        field_name="art_datecre", lookup_expr="month"
    )

    art_datemdf_year = filters.NumberFilter(
        field_name="art_datemdf", lookup_expr="year"
    )
    art_datemdf_month = filters.NumberFilter(
        field_name="art_datemdf", lookup_expr="month"
    )

    class Meta:
        model = TArticle
        exclude = [
            "art_id",
        ]

        filter_overrides = {
            models.CharField: {
                "filter_class": filters.CharFilter,
                "extra": lambda f: {"lookup_expr": "icontains"},
            },
            models.DecimalField: {
                "filter_class": filters.NumberFilter,
            },
            models.DateField: {
                "filter_class": filters.DateFilter,
            },
            models.DateTimeField: {
                "filter_class": filters.DateFilter,
                "extra": lambda f: {"lookup_expr": "date"},
            },
        }


class EntreeFilter(filters.FilterSet):
    ent_enabled = filters.NumberFilter()
    ent_datecre_year = filters.NumberFilter(
        field_name="ent_datecre", lookup_expr="year"
    )
    ent_datecre_month = filters.NumberFilter(
        field_name="ent_datecre", lookup_expr="month"
    )

    ent_datemdf_year = filters.NumberFilter(
        field_name="ent_datemdf", lookup_expr="year"
    )
    ent_datemdf_month = filters.NumberFilter(
        field_name="ent_datemdf", lookup_expr="month"
    )

    class Meta:
        model = TEntree
        exclude = [
            "ent_id",
        ]

        filter_overrides = {
            models.CharField: {
                "filter_class": filters.CharFilter,
                "extra": lambda f: {"lookup_expr": "icontains"},
            },
            models.DecimalField: {
                "filter_class": filters.NumberFilter,
            },
            models.DateField: {
                "filter_class": filters.DateFilter,
            },
            models.DateTimeField: {
                "filter_class": filters.DateFilter,
                "extra": lambda f: {"lookup_expr": "date"},
            },
        }


class RtfFilter(filters.FilterSet):
    rtf_enabled = filters.NumberFilter()
    rtf_datecre_year = filters.NumberFilter(
        field_name="rtf_datecre", lookup_expr="year"
    )
    rtf_datecre_month = filters.NumberFilter(
        field_name="rtf_datecre", lookup_expr="month"
    )

    rtf_datemdf_year = filters.NumberFilter(
        field_name="rtf_datemdf", lookup_expr="year"
    )
    rtf_datemdf_month = filters.NumberFilter(
        field_name="rtf_datemdf", lookup_expr="month"
    )

    class Meta:
        model = TRetourFournis
        exclude = [
            "rtf_id",
        ]

        filter_overrides = {
            models.CharField: {
                "filter_class": filters.CharFilter,
                "extra": lambda f: {"lookup_expr": "icontains"},
            },
            models.DecimalField: {
                "filter_class": filters.NumberFilter,
            },
            models.DateField: {
                "filter_class": filters.DateFilter,
            },
            models.DateTimeField: {
                "filter_class": filters.DateFilter,
                "extra": lambda f: {"lookup_expr": "date"},
            },
        }

class RtcFilter(filters.FilterSet):
    rtc_enabled = filters.NumberFilter()
    rtc_datecre_year = filters.NumberFilter(
        field_name="rtc_datecre", lookup_expr="year"
    )
    rtc_datecre_month = filters.NumberFilter(
        field_name="rtc_datecre", lookup_expr="month"
    )

    rtc_datemdf_year = filters.NumberFilter(
        field_name="rtc_datemdf", lookup_expr="year"
    )
    rtc_datemdf_month = filters.NumberFilter(
        field_name="rtc_datemdf", lookup_expr="month"
    )

    class Meta:
        model = TRetourClient
        exclude = [
            "rtc_id",
        ]

        filter_overrides = {
            models.CharField: {
                "filter_class": filters.CharFilter,
                "extra": lambda f: {"lookup_expr": "icontains"},
            },
            models.DecimalField: {
                "filter_class": filters.NumberFilter,
            },
            models.DateField: {
                "filter_class": filters.DateFilter,
            },
            models.DateTimeField: {
                "filter_class": filters.DateFilter,
                "extra": lambda f: {"lookup_expr": "date"},
            },
        }

class SortitFilter(filters.FilterSet):
    out_enabled = filters.NumberFilter()
    out_datecre_year = filters.NumberFilter(
        field_name="out_datecre", lookup_expr="year"
    )
    out_datecre_month = filters.NumberFilter(
        field_name="out_datecre", lookup_expr="month"
    )

    out_datemdf_year = filters.NumberFilter(
        field_name="out_datemdf", lookup_expr="year"
    )
    out_datemdf_month = filters.NumberFilter(
        field_name="out_datemdf", lookup_expr="month"
    )

    class Meta:
        model = TOutStock
        exclude = [
            "out_id",
        ]

        filter_overrides = {
            models.CharField: {
                "filter_class": filters.CharFilter,
                "extra": lambda f: {"lookup_expr": "icontains"},
            },
            models.DecimalField: {
                "filter_class": filters.NumberFilter,
            },
            models.DateField: {
                "filter_class": filters.DateFilter,
            },
            models.DateTimeField: {
                "filter_class": filters.DateFilter,
                "extra": lambda f: {"lookup_expr": "date"},
            },
        }


class InStockFilter(filters.FilterSet):
    int_enabled = filters.NumberFilter()
    int_datecre_year = filters.NumberFilter(
        field_name="int_datecre", lookup_expr="year"
    )
    int_datecre_month = filters.NumberFilter(
        field_name="int_datecre", lookup_expr="month"
    )

    int_datemdf_year = filters.NumberFilter(
        field_name="int_datemdf", lookup_expr="year"
    )
    int_datemdf_month = filters.NumberFilter(
        field_name="int_datemdf", lookup_expr="month"
    )

    class Meta:
        model = TInStock
        exclude = [
            "in_id",
        ]

        filter_overrides = {
            models.CharField: {
                "filter_class": filters.CharFilter,
                "extra": lambda f: {"lookup_expr": "icontains"},
            },
            models.DecimalField: {
                "filter_class": filters.NumberFilter,
            },
            models.DateField: {
                "filter_class": filters.DateFilter,
            },
            models.DateTimeField: {
                "filter_class": filters.DateFilter,
                "extra": lambda f: {"lookup_expr": "date"},
            },
        }


class MvtStockFilter(filters.FilterSet):
    mvt_enabled = filters.NumberFilter()
    mvt_datecre_year = filters.NumberFilter(
        field_name="mvt_datecre", lookup_expr="year"
    )
    mvt_datecre_month = filters.NumberFilter(
        field_name="mvt_datecre", lookup_expr="month"
    )

    mvt_datemdf_year = filters.NumberFilter(
        field_name="mvt_datemdf", lookup_expr="year"
    )
    mvt_datemdf_month = filters.NumberFilter(
        field_name="mvt_datemdf", lookup_expr="month"
    )

    class Meta:
        model = TMvtStock
        exclude = [
            "mvt_id",
        ]

        filter_overrides = {
            models.CharField: {
                "filter_class": filters.CharFilter,
                "extra": lambda f: {"lookup_expr": "icontains"},
            },
            models.DecimalField: {
                "filter_class": filters.NumberFilter,
            },
            models.DateField: {
                "filter_class": filters.DateFilter,
            },
            models.DateTimeField: {
                "filter_class": filters.DateFilter,
                "extra": lambda f: {"lookup_expr": "date"},
            },
        }

class MvtStockFilterr(django_filters.FilterSet):
    class Meta:
        model = TMvtStock
        fields = {
            "mvt_id": ["exact"],
            "mvt_action": ["exact", "icontains"],
            "mvt_origine": ["exact", "icontains"],
            "mvt_code_org": ["exact", "icontains"],
            "mvt_qte": ["exact", "gte", "lte"],
            "mvt_art_code": ["exact", "icontains"],
            "mvt_pri_id": ["exact"],
            "mvt_lot_code": ["exact", "icontains"],
            "mvt_date": ["exact", "gte", "lte"],
            "mvt_datecre": ["exact", "gte", "lte"],
            "mvt_datemdf": ["exact", "gte", "lte"],
            "mvt_usercre": ["exact", "icontains"],
            "mvt_usermdf": ["exact", "icontains"],
        }
