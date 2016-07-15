import django_filters
from django.db.models import Count
from django.utils.translation import ugettext as _

from rest_framework import filters

from tethneweb.models import *


class PaperFilter(filters.FilterSet):
    title = django_filters.CharFilter(name='title', lookup_type='icontains')
    abstract = django_filters.CharFilter(name='abstract', lookup_type='icontains')
    journal = django_filters.CharFilter(name='journal', lookup_type='icontains')
    concrete = django_filters.BooleanFilter(name='concrete', widget=django_filters.widgets.BooleanWidget())
    citations = django_filters.MethodFilter()

    class Meta:
        model = Paper
        fields = ['title', 'journal', 'publication_date', 'corpus', 'volume',
                  'issue', 'abstract', 'concrete', 'cited_by', 'id',
                  'citations']

    def filter_citations(self, queryset, value):
        return queryset.filter(cited_references=value)

class AuthorInstanceFilter(filters.FilterSet):
    first_name = django_filters.CharFilter(name='first_name', lookup_type='icontains')
    last_name = django_filters.CharFilter(name='last_name', lookup_type='icontains')

    class Meta:
        model = AuthorInstance
        fields = ['id', 'paper', 'first_name', 'last_name']


class InstitutionInstanceFilter(filters.FilterSet):
    class Meta:
        model = InstitutionInstance
        fields = ['id', 'paper', 'name', 'department', 'address', 'state',
                  'city', 'zip', 'country']


class AffiliationInstanceFilter(filters.FilterSet):
    confidence = django_filters.MethodFilter()

    class Meta:
        model = AffiliationInstance
        fields = ['id', 'paper', 'author', 'institution', 'confidence']

    def filter_confidence(self, queryset, value):
        return queryset.filter(confidence__gte=value)


class MetadatumFilter(filters.FilterSet):
    class Meta:
        model = Metadatum
        fields = ['id', 'paper', 'name', 'value']
