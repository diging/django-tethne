from django.contrib.auth.models import User
from rest_framework.pagination import LimitOffsetPagination
from rest_framework import serializers, viewsets
from django.core.paginator import Paginator
from rest_framework.response import Response
from rest_framework.reverse import reverse_lazy

from tethneweb.models import *
from tethneweb.filters import *

import cPickle as pickle


class AcceptsRequestSerializer(serializers.HyperlinkedModelSerializer):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(AcceptsRequestSerializer, self).__init__(*args, **kwargs)


class MetadatumSerializer(serializers.HyperlinkedModelSerializer):
    value = serializers.SerializerMethodField('unpickle_value')

    class Meta:
        model = Metadatum
        fields = ('url', 'id', 'name', 'value', 'paper')

    def unpickle_value(self, obj):
        return pickle.loads(str(obj.value))


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'id', 'username', 'email')


class AuthorInstanceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AuthorInstance
        fields = ('url', 'id', 'paper', 'first_name', 'last_name')


class InstitutionInstanceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = InstitutionInstance
        fields = ('url', 'id', 'paper', 'name', 'paper', 'department',
                  'address', 'state', 'city', 'zip', 'country')


class AffiliationInstanceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AffiliationInstance
        fields = ('url', 'id', 'paper', 'author', 'institution', 'confidence')


class PaperSerializer(AcceptsRequestSerializer):
    citations = serializers.SerializerMethodField('citations_link')
    authors = serializers.SerializerMethodField('author_instances_link')
    institutions = serializers.SerializerMethodField('institution_instances_link')
    affilations = serializers.SerializerMethodField('affiliation_instances_link')
    metadata = serializers.SerializerMethodField('metadatum_link')

    class Meta:
        model = Paper
        fields = ('url', 'id', 'corpus', 'publication_date', 'title', 'volume',
                  'issue', 'journal', 'abstract', 'concrete', 'cited_by',
                  'citations', 'authors', 'institutions', 'affilations',
                  'metadata')

    def citations_link(self, obj):
        return reverse_lazy('paper-list', request=self.request) + '?cited_by=%i&concrete=false' % obj.id

    def author_instances_link(self, obj):
        return reverse_lazy('authorinstance-list', request=self.request) + '?paper=%i' % obj.id

    def institution_instances_link(self, obj):
        return reverse_lazy('institutioninstance-list', request=self.request) + '?paper=%i' % obj.id

    def affiliation_instances_link(self, obj):
        return reverse_lazy('affiliationinstance-list', request=self.request) + '?paper=%i' % obj.id

    def metadatum_link(self, obj):
        return reverse_lazy('metadatum-list', request=self.request) + '?paper=%i' % obj.id


class CorpusSerializer(AcceptsRequestSerializer):
    papers = serializers.SerializerMethodField('papers_link')

    class Meta:
        model = Corpus
        fields = ('url', 'id', 'source', 'label', 'date_created', 'created_by', 'papers')

    def papers_link(self, obj):
        return reverse_lazy('paper-list', request=self.request) + '?corpus=%i&concrete=true' % obj.id


class PassRequestToSerializerMixin(object):
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, request=request)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, request=request)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True, request=request)
        return Response(serializer.data)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class CorpusViewSet(PassRequestToSerializerMixin, viewsets.ModelViewSet):
    queryset = Corpus.objects.all()
    serializer_class = CorpusSerializer


class AuthorInstanceViewSet(viewsets.ModelViewSet):
    queryset = AuthorInstance.objects.all()
    serializer_class = AuthorInstanceSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = AuthorInstanceFilter


class InstitutionInstanceViewSet(viewsets.ModelViewSet):
    queryset = InstitutionInstance.objects.all()
    serializer_class = InstitutionInstanceSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = InstitutionInstanceFilter


class AffiliationInstanceViewSet(viewsets.ModelViewSet):
    queryset = AffiliationInstance.objects.all()
    serializer_class = AffiliationInstanceSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = AffiliationInstanceFilter


class PaperViewSet(PassRequestToSerializerMixin, viewsets.ModelViewSet):
    queryset = Paper.objects.all()
    serializer_class = PaperSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = PaperFilter



class MetadatumViewSet(viewsets.ModelViewSet):
    queryset = Metadatum.objects.all()
    serializer_class = MetadatumSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = MetadatumFilter
