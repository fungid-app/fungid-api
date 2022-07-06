# Generated by Django 4.0.5 on 2022-07-05 20:26

from django.db import migrations, models
import django.db.models.deletion
import django.db.models.expressions
import django.db.models.functions.text


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CommonNames',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('language', models.CharField(max_length=5, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Species',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phylum', models.CharField(max_length=255, null=True)),
                ('classname', models.CharField(max_length=255, null=True)),
                ('order', models.CharField(max_length=255, null=True)),
                ('family', models.CharField(max_length=255, null=True)),
                ('genus', models.CharField(max_length=255, null=True)),
                ('species', models.CharField(max_length=255, unique=True)),
                ('description', models.TextField(null=True)),
                ('included_in_classifier', models.BooleanField(default=False)),
                ('number_of_observations', models.IntegerField()),
            ],
        ),
        migrations.AddConstraint(
            model_name='species',
            constraint=models.UniqueConstraint(django.db.models.functions.text.Lower('species'), name='taxonomy_species_unique_name'),
        ),
        migrations.AddField(
            model_name='commonnames',
            name='species',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='common_names', to='taxonomy.species'),
        ),
        migrations.AddIndex(
            model_name='commonnames',
            index=models.Index(fields=['species', 'language'], name='taxonomy_cn_species_lang_idx'),
        ),
        migrations.AddConstraint(
            model_name='commonnames',
            constraint=models.UniqueConstraint(django.db.models.functions.text.Lower('name'), django.db.models.expressions.F('language'), django.db.models.expressions.F('species'), name='taxonomy_commonnames_unique_name'),
        ),
    ]
