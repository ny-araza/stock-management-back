from .models import TLien, TEnumeration, TCode
from django.apps import apps
from django.utils import timezone


def get_table_prefix(table_name: str) -> str:
    """
    Retourne la valeur de lie_abs correspondant au nom de la table.

    Exemple:
        get_table_prefix("t_client") -> "CL"
        get_table_prefix("t_vente") -> "FA"
    """
    try:
        return TLien.objects.values_list("lie_abs", flat=True).get(
            lie_table=table_name
        )
    except TLien.DoesNotExist:
        return ""


def generate_reference(
        table_name: str, pk_field: str) -> str:
    """
    Génère une référence du type CL0005.
    """

    try:
        prefix = TLien.objects.values_list(
            "lie_abs", flat=True
        ).get(lie_table=table_name)
    except TLien.DoesNotExist:
        raise ValueError(f"Aucun préfixe trouvé pour la table '{table_name}'")

    model = next(
        (
            m
            for m in apps.get_models()
            if m._meta.db_table == table_name
        ),
        None,
    )

    if model is None:
        raise ValueError(
            f"Aucun modèle Django associé à la table '{table_name}'")

    last = (
        model.objects.order_by(f"-{pk_field}")
        .values_list(pk_field, flat=True)
        .first()
    )
    prefix = get_table_prefix(table_name)
    temp = int(last.replace(prefix, ""))

    next_id = 1 if temp is None else temp + 1

    return f"{prefix}{next_id:04d}"


def generate_enumeration_value(enu_code: str) -> list[dict[str, str]]:
    try:
        prefix = TEnumeration.objects.filter(
            enu_code=enu_code
        ).values_list("enu_nom", "enu_id")
        result = []
        for p in prefix:
            temp = {}
            temp.update({"enu_id": p[1], "enu_nom": p[0]})
            result.append(temp)
    except TLien.DoesNotExist:
        raise ValueError(f"Aucun préfixe trouvé pour la table '{enu_code}'")
    return result


# get code

def get_dernier_code(nom_table: str, isInsert: bool):
    """
    Retourne la dernière ligne correspondant à une table.
    Retourne None si aucune ligne n'existe.
    """

    maintenant = timezone.now()
    annee_actuelle = maintenant.year
    mois_actuel = maintenant.month

    dernier_code = TCode.objects \
                        .filter(cod_table=nom_table) \
                        .order_by("cod_annee", "cod_mois", "cod_id").last()

    if dernier_code is None:
        dernier_code = TCode.objects.create(
            cod_table=nom_table,
            cod_num=1,
            cod_annee=annee_actuelle,
            cod_mois=mois_actuel,
        )
    elif (
        dernier_code.cod_annee == annee_actuelle
        and dernier_code.cod_mois == mois_actuel
    ):
        if isInsert:
            dernier_code.cod_num = str(int(dernier_code.cod_num) + 1)
            dernier_code.save(update_fields=["cod_num"])
    else:
        dernier_code = TCode.objects.create(
            cod_table=nom_table,
            cod_num=1,
            cod_annee=annee_actuelle,
            cod_mois=mois_actuel,
        )

    return (
        {
            "cod_table": dernier_code.cod_table,
            "cod_num": dernier_code.cod_num,
            "cod_annee": dernier_code.cod_annee,
            "cod_mois": dernier_code.cod_mois
        }
    )


def generate_code_date(nom_table: str, isInsert: bool):
    dernier_code = get_dernier_code(nom_table, isInsert)
    prefix = get_table_prefix(nom_table)

    return (
        f"{prefix}{str(dernier_code['cod_annee'])[2:4]}"
        f"{dernier_code['cod_mois']}{int(dernier_code['cod_num']):04d}"
    )
