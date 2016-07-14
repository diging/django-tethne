# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-07-14 21:36
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Affiliation',
            fields=[
                ('id', models.PositiveIntegerField(primary_key=True, serialize=False)),
                ('confidence', models.FloatField(default=0.0)),
                ('methods', models.TextField()),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('occur_date', models.DateField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AffiliationInstance',
            fields=[
                ('id', models.PositiveIntegerField(primary_key=True, serialize=False)),
                ('confidence', models.FloatField(default=0.0)),
            ],
        ),
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.PositiveIntegerField(primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('initials', models.CharField(blank=True, max_length=255, null=True)),
                ('identifier', models.CharField(blank=True, max_length=255, null=True)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='AuthorIdentity',
            fields=[
                ('id', models.PositiveIntegerField(primary_key=True, serialize=False)),
                ('confidence', models.FloatField(default=0.0)),
                ('methods', models.TextField()),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='instantiations', to='tethneweb.Author')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AuthorInstance',
            fields=[
                ('id', models.PositiveIntegerField(primary_key=True, serialize=False)),
                ('first_name', models.CharField(blank=True, max_length=255, null=True)),
                ('last_name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='CitationIdentity',
            fields=[
                ('id', models.PositiveIntegerField(primary_key=True, serialize=False)),
                ('confidence', models.FloatField(default=0.0)),
                ('methods', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Corpus',
            fields=[
                ('id', models.PositiveIntegerField(primary_key=True, serialize=False)),
                ('source', models.CharField(choices=[(b'JSTOR', b'JSTOR DfR'), (b'WOS', b'Web of Science'), (b'ZOTERO', b'Zotero'), (b'SCOPUS', b'Scopus')], max_length=35)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('label', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='DisambiguationModel',
            fields=[
                ('id', models.PositiveIntegerField(primary_key=True, serialize=False)),
                ('label', models.CharField(max_length=255)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('methods', models.TextField()),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Identifier',
            fields=[
                ('id', models.PositiveIntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('value', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Institution',
            fields=[
                ('id', models.PositiveIntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('address', models.TextField()),
                ('state', models.CharField(blank=True, max_length=255, null=True)),
                ('city', models.CharField(blank=True, max_length=255, null=True)),
                ('zip', models.CharField(blank=True, max_length=10, null=True)),
                ('country', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='InstitutionIdentity',
            fields=[
                ('id', models.PositiveIntegerField(primary_key=True, serialize=False)),
                ('confidence', models.FloatField(default=0.0)),
                ('methods', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='InstitutionInstance',
            fields=[
                ('id', models.PositiveIntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('department', models.CharField(blank=True, max_length=255, null=True)),
                ('address', models.TextField()),
                ('state', models.CharField(blank=True, max_length=255, null=True)),
                ('city', models.CharField(blank=True, max_length=255, null=True)),
                ('zip', models.CharField(blank=True, max_length=10, null=True)),
                ('country', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Metadatum',
            fields=[
                ('id', models.PositiveIntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('value', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Paper',
            fields=[
                ('id', models.PositiveIntegerField(primary_key=True, serialize=False)),
                ('publication_date', models.IntegerField(blank=True, null=True)),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('volume', models.CharField(blank=True, max_length=40, null=True)),
                ('issue', models.CharField(blank=True, max_length=40, null=True)),
                ('journal', models.CharField(blank=True, max_length=255, null=True)),
                ('abstract', models.TextField(null=True)),
                ('concrete', models.BooleanField(default=True)),
                ('cited_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cited_references', to='tethneweb.Paper')),
                ('corpus', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='papers', to='tethneweb.Corpus')),
            ],
        ),
        migrations.AddField(
            model_name='metadatum',
            name='paper',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='metadata', to='tethneweb.Paper'),
        ),
        migrations.AddField(
            model_name='institutioninstance',
            name='paper',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='institutions', to='tethneweb.Paper'),
        ),
        migrations.AddField(
            model_name='institutionidentity',
            name='instance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='identities', to='tethneweb.InstitutionInstance'),
        ),
        migrations.AddField(
            model_name='institutionidentity',
            name='institution',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='instantiations', to='tethneweb.Institution'),
        ),
        migrations.AddField(
            model_name='institutionidentity',
            name='model',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tethneweb.DisambiguationModel'),
        ),
        migrations.AddField(
            model_name='identifier',
            name='paper',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='identifiers', to='tethneweb.Paper'),
        ),
        migrations.AddField(
            model_name='citationidentity',
            name='cited_reference',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='identities', to='tethneweb.Paper'),
        ),
        migrations.AddField(
            model_name='citationidentity',
            name='model',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tethneweb.DisambiguationModel'),
        ),
        migrations.AddField(
            model_name='citationidentity',
            name='paper',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='instantiations', to='tethneweb.Paper'),
        ),
        migrations.AddField(
            model_name='authorinstance',
            name='paper',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='author_instances', to='tethneweb.Paper'),
        ),
        migrations.AddField(
            model_name='authoridentity',
            name='instance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='identities', to='tethneweb.AuthorInstance'),
        ),
        migrations.AddField(
            model_name='authoridentity',
            name='model',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tethneweb.DisambiguationModel'),
        ),
        migrations.AddField(
            model_name='affiliationinstance',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='affiliations', to='tethneweb.AuthorInstance'),
        ),
        migrations.AddField(
            model_name='affiliationinstance',
            name='institution',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='affiliations', to='tethneweb.InstitutionInstance'),
        ),
        migrations.AddField(
            model_name='affiliationinstance',
            name='paper',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='affiliations', to='tethneweb.Paper'),
        ),
        migrations.AddField(
            model_name='affiliation',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='affiliations', to='tethneweb.Author'),
        ),
        migrations.AddField(
            model_name='affiliation',
            name='institution',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='affiliates', to='tethneweb.Institution'),
        ),
        migrations.AddField(
            model_name='affiliation',
            name='model',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tethneweb.DisambiguationModel'),
        ),
    ]
