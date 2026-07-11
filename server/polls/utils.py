from .models import TLien, TEnumeration
from django.apps import apps


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
    print(result)
    return result
