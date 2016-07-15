from django.contrib.auth.models import User
from rest_framework.pagination import LimitOffsetPagination
from rest_framework import serializers, viewsets
from django.core.paginator import Paginator
from rest_framework.response import Response
from rest_framework.reverse import reverse_lazy

from urlparse import urlparse, parse_qs, SplitResult
from urllib import urlencode

from tethneweb.models import *
from tethneweb.filters import *

import cPickle as pickle


def link_for(url_name, request, params):
    url = reverse_lazy(url_name, request=request)
    o = urlparse(url)
    params.update({k: v[0] for k, v in parse_qs(o.query).iteritems()})
    new = SplitResult(o.scheme, o.netloc, o.path, urlencode(params), '')
    return new.geturl().lower()


class AcceptsRequestSerializer(serializers.HyperlinkedModelSerializer):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(AcceptsRequestSerializer, self).__init__(*args, **kwargs)


class IdentifierSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Identifier
        fields = ('url', 'id', 'paper', 'name', 'value', 'corpus')


class MetadatumSerializer(serializers.HyperlinkedModelSerializer):
    value = serializers.SerializerMethodField('unpickle_value')

    class Meta:
        model = Metadatum
        fields = ('url', 'id', 'name', 'value', 'paper', 'corpus',)

    def unpickle_value(self, obj):
        return pickle.loads(str(obj.value))


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'id', 'username', 'email')


class AuthorInstanceSerializer(AcceptsRequestSerializer):
    affiliations = serializers.SerializerMethodField('affiliation_instances_link')

    class Meta:
        model = AuthorInstance
        fields = ('url', 'id', 'paper', 'first_name', 'last_name',
                  'affiliations', 'corpus',)

    def affiliation_instances_link(self, obj):
        params = {'author': obj.id}
        return link_for('affiliationinstance-list', self.request, params)


class InstitutionInstanceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = InstitutionInstance
        fields = ('url', 'id', 'paper', 'name', 'paper', 'department',
                  'address', 'state', 'city', 'zip', 'country', 'corpus',)


class AffiliationInstanceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AffiliationInstance
        fields = ('url', 'id', 'paper', 'author', 'institution', 'confidence',
                  'corpus',)


class PaperSerializer(AcceptsRequestSerializer):
    citations = serializers.SerializerMethodField('citations_link')
    authors = serializers.SerializerMethodField('author_instances_link')
    institutions = serializers.SerializerMethodField('institution_instances_link')
    affiliations = serializers.SerializerMethodField('affiliation_instances_link')
    metadata = serializers.SerializerMethodField('metadatum_link')

    identifiers = IdentifierSerializer(many=True)

    class Meta:
        model = Paper
        fields = ('url', 'id', 'corpus', 'publication_date', 'title', 'volume',
                  'issue', 'journal', 'abstract', 'concrete', 'cited_by',
                  'citations', 'authors', 'institutions', 'affiliations',
                  'metadata', 'identifiers')

    def citations_link(self, obj):
        params = {'cited_by': obj.id, 'concrete': False}
        return link_for('paper-list', self.request, params)

    def author_instances_link(self, obj):
        params = {'paper': obj.id}
        return link_for('authorinstance-list', self.request, params)

    def institution_instances_link(self, obj):
        params = {'paper': obj.id}
        return link_for('institutioninstance-list', self.request, params)

    def affiliation_instances_link(self, obj):
        params = {'paper': obj.id}
        return link_for('affiliationinstance-list', self.request, params)

    def metadatum_link(self, obj):
        params = {'paper': obj.id}
        return link_for('metadatum-list', self.request, params)


class CorpusSerializer(AcceptsRequestSerializer):
    papers = serializers.SerializerMethodField('papers_link')
    citations = serializers.SerializerMethodField('citations_link')
    authors = serializers.SerializerMethodField('author_instances_link')
    institutions = serializers.SerializerMethodField('institution_instances_link')
    affiliations = serializers.SerializerMethodField('affiliation_instances_link')
    metadata = serializers.SerializerMethodField('metadatum_link')

    class Meta:
        model = Corpus
        fields = ('url', 'id', 'source', 'label', 'date_created', 'created_by',
                  'papers', 'citations', 'affiliations', 'authors',
                  'institutions', 'metadata',)

    def papers_link(self, obj):
        params = {'corpus': obj.id, 'concrete': True}
        return link_for('paper-list', self.request, params)

    def citations_link(self, obj):
        params = {'corpus': obj.id, 'concrete': False}
        return link_for('paper-list', self.request, params)

    def author_instances_link(self, obj):
        params = {'corpus': obj.id}
        return link_for('authorinstance-list', self.request, params)

    def institution_instances_link(self, obj):
        params = {'corpus': obj.id}
        return link_for('institutioninstance-list', self.request, params)

    def affiliation_instances_link(self, obj):
        params = {'corpus': obj.id}
        return link_for('affiliationinstance-list', self.request, params)

    def metadatum_link(self, obj):
        params = {'corpus': obj.id}
        return link_for('metadatum-list', self.request, params)



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


class CreatorOnlyMixin(viewsets.ModelViewSet):
    def get_queryset(self):
        qs = super(CreatorOnlyMixin, self).get_queryset()
        return qs.filter(created_by=self.request.user.id)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class CorpusViewSet(PassRequestToSerializerMixin, CreatorOnlyMixin, viewsets.ModelViewSet):
    queryset = Corpus.objects.all()
    serializer_class = CorpusSerializer


class AuthorInstanceViewSet(PassRequestToSerializerMixin, CreatorOnlyMixin, viewsets.ModelViewSet):
    queryset = AuthorInstance.objects.all()
    serializer_class = AuthorInstanceSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = AuthorInstanceFilter


class InstitutionInstanceViewSet(CreatorOnlyMixin, viewsets.ModelViewSet):
    queryset = InstitutionInstance.objects.all()
    serializer_class = InstitutionInstanceSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = InstitutionInstanceFilter


class AffiliationInstanceViewSet(CreatorOnlyMixin, viewsets.ModelViewSet):
    queryset = AffiliationInstance.objects.all()
    serializer_class = AffiliationInstanceSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = AffiliationInstanceFilter


class PaperViewSet(PassRequestToSerializerMixin, CreatorOnlyMixin, viewsets.ModelViewSet):
    queryset = Paper.objects.all()
    serializer_class = PaperSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = PaperFilter


class MetadatumViewSet(CreatorOnlyMixin, viewsets.ModelViewSet):
    queryset = Metadatum.objects.all()
    serializer_class = MetadatumSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = MetadatumFilter


class IdentifierViewSet(CreatorOnlyMixin, viewsets.ModelViewSet):
    queryset = Identifier.objects.all()
    serializer_class = IdentifierSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = IdentifierFilter
