from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("telemetry_app", "0024_dockstatus_alter_alarmcategory_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="dockstatus",
            name="airport_push",
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name="机场推流地址"),
        ),
        migrations.AddField(
            model_name="dockstatus",
            name="drone_push",
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name="无人机推流地址"),
        ),
    ]
