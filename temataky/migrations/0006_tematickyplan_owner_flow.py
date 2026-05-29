from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def assign_owner_to_existing_plans(apps, schema_editor):
    TematickyPlan = apps.get_model("temataky", "TematickyPlan")
    User = apps.get_model(*settings.AUTH_USER_MODEL.split("."))

    db_alias = schema_editor.connection.alias

    all_users = User.objects.using(db_alias).order_by("id")
    fallback_owner = all_users.filter(is_superuser=True).first() or all_users.first()

    plans = TematickyPlan.objects.using(db_alias).all()
    if plans.exists() and fallback_owner is None:
        raise RuntimeError("Nelze doplnit vlastníka tematického plánu: v databázi není žádný uživatel.")

    for plan in plans:
        owner = plan.ucitele.order_by("id").first() or fallback_owner
        plan.owner_id = owner.id
        plan.save(update_fields=["owner"])

        if not plan.ucitele.filter(id=owner.id).exists():
            plan.ucitele.add(owner)


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("temataky", "0005_remove_tematickyplan_unique_plan_name_per_subject_in_school_year_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="tematickyplan",
            name="owner",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="owned_tematicke_plany",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Vlastník",
            ),
        ),
        migrations.RunPython(assign_owner_to_existing_plans, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="tematickyplan",
            name="owner",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="owned_tematicke_plany",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Vlastník",
            ),
        ),
    ]
