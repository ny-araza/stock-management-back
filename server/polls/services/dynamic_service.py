from django.apps import apps


def get_model_by_table(table_name: str):
    model = next(
        (m for m in apps.get_models() if m._meta.db_table == table_name),
        None
    )
    return model


def create_dynamic_instance(table_name: str, data: dict):
    model = get_model_by_table(table_name)

    if not model:
        raise ValueError(f"Table {table_name} introuvable")

    instance = model.objects.create(**data)
    return instance
