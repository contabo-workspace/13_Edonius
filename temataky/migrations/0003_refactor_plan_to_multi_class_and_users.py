from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def forward_copy_subject_and_class_links(apps, schema_editor):
    TematickyPlan = apps.get_model("temataky", "TematickyPlan")
    TematickyPlanTrida = apps.get_model("temataky", "TematickyPlanTrida")

    for plan in TematickyPlan.objects.select_related("predmet_trida_ve_skolnim_roce").all().iterator():
        subject_class_link = plan.predmet_trida_ve_skolnim_roce
        plan.predmet_ve_skolnim_roce_id = subject_class_link.predmet_ve_skolnim_roce_id
        plan.save(update_fields=["predmet_ve_skolnim_roce"])

        TematickyPlanTrida.objects.get_or_create(
            tematicky_plan_id=plan.id,
            trida_id=subject_class_link.trida_id,
        )


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0004_subjectclassinschoolyear_and_more"),
        ("temataky", "0002_remove_tematickyplan_unique_plan_name_per_subject_class_in_school_year_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="TematickyPlanTrida",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "tematicky_plan",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tridy",
                        to="temataky.tematickyplan",
                        verbose_name="Tematický plán",
                    ),
                ),
                (
                    "trida",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="tematicke_plany",
                        to="core.schoolclass",
                        verbose_name="Třída",
                    ),
                ),
            ],
            options={
                "verbose_name": "Třída tematického plánu",
                "verbose_name_plural": "Třídy tematického plánu",
                "ordering": ["trida__name"],
            },
        ),
        migrations.AddField(
            model_name="tematickyplan",
            name="predmet_ve_skolnim_roce",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="tematicke_plany",
                to="core.subjectinschoolyear",
                verbose_name="Předmět ve školním roce",
            ),
        ),
        migrations.AddField(
            model_name="tematickyplan",
            name="ucitele",
            field=models.ManyToManyField(blank=True, related_name="tematicke_plany", to=settings.AUTH_USER_MODEL, verbose_name="Učitelé"),
        ),
        migrations.RunPython(forward_copy_subject_and_class_links, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="tematickyplan",
            name="predmet_ve_skolnim_roce",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="tematicke_plany",
                to="core.subjectinschoolyear",
                verbose_name="Předmět ve školním roce",
            ),
        ),
        migrations.RemoveConstraint(
            model_name="tematickyplan",
            name="unique_plan_name_per_subject_class_link_in_school_year",
        ),
        migrations.AddConstraint(
            model_name="tematickyplantrida",
            constraint=models.UniqueConstraint(fields=("tematicky_plan", "trida"), name="unique_class_per_thematic_plan"),
        ),
        migrations.AddConstraint(
            model_name="tematickyplan",
            constraint=models.UniqueConstraint(fields=("predmet_ve_skolnim_roce", "nazev"), name="unique_plan_name_per_subject_in_school_year"),
        ),
        migrations.RemoveField(
            model_name="tematickyplan",
            name="predmet_trida_ve_skolnim_roce",
        ),
    ]
