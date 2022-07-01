# Generated by Django 4.0.5 on 2022-07-01 14:40

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
            name='ClassTax',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('key', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='CommonNames',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Family',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('key', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Genus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('key', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('key', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Phylum',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('key', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Species',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('key', models.IntegerField()),
                ('description', models.TextField()),
                ('genus', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='subspecies', to='taxonomy.genus')),
            ],
        ),
        migrations.AddConstraint(
            model_name='phylum',
            constraint=models.UniqueConstraint(django.db.models.functions.text.Lower('name'), name='phylum_unique_name'),
        ),
        migrations.AddField(
            model_name='order',
            name='classtax',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='suborders', to='taxonomy.classtax'),
        ),
        migrations.AddField(
            model_name='genus',
            name='family',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='subgenera', to='taxonomy.family'),
        ),
        migrations.AddField(
            model_name='family',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='subfamilies', to='taxonomy.order'),
        ),
        migrations.AddField(
            model_name='commonnames',
            name='species',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='common_names', to='taxonomy.species'),
        ),
        migrations.AddField(
            model_name='classtax',
            name='phylum',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='subclasses', to='taxonomy.phylum'),
        ),
        migrations.AddConstraint(
            model_name='species',
            constraint=models.UniqueConstraint(django.db.models.functions.text.Lower('name'), name='species_unique_name'),
        ),
        migrations.AddConstraint(
            model_name='order',
            constraint=models.UniqueConstraint(django.db.models.functions.text.Lower('name'), name='order_unique_name'),
        ),
        migrations.AddConstraint(
            model_name='genus',
            constraint=models.UniqueConstraint(django.db.models.functions.text.Lower('name'), name='genus_unique_name'),
        ),
        migrations.AddConstraint(
            model_name='family',
            constraint=models.UniqueConstraint(django.db.models.functions.text.Lower('name'), name='family_unique_name'),
        ),
        migrations.AddConstraint(
            model_name='commonnames',
            constraint=models.UniqueConstraint(django.db.models.functions.text.Lower('name'), django.db.models.expressions.F('species'), name='commonnames_unique_name'),
        ),
        migrations.AddConstraint(
            model_name='classtax',
            constraint=models.UniqueConstraint(django.db.models.functions.text.Lower('name'), name='class_unique_name'),
        ),
    ]
