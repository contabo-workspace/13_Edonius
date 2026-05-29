from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0008_userprofile"),
    ]

    operations = [
        migrations.CreateModel(
            name="GlobalSettings",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "active_school_year",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="global_settings_entries",
                        to="core.schoolyear",
                        verbose_name="Aktivní školní rok",
                    ),
                ),
            ],
            options={
                "verbose_name": "Globální nastavení",
                "verbose_name_plural": "Globální nastavení",
            },
        ),
    ]
