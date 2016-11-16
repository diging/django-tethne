from django.db.models import Max
from django.contrib.auth.models import User
from rest_framework.pagination import LimitOffsetPagination
from rest_framework import serializers, viewsets
from django.core.paginator import Paginator
from rest_framework.response import Response
from rest_framework.reverse import reverse_lazy

from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.db.models.query_utils import Q
from django.db.models import Count

from urlparse import urlparse, parse_qs, SplitResult
from urllib import urlencode

from tethneweb.models import *
from tethneweb.filters import *

import json


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


class InstanceIdentifierSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = InstanceIdentifier
        fields = ('url', 'id', 'paper', 'name', 'value', 'corpus')


class InstanceMetadatumSerializer(serializers.HyperlinkedModelSerializer):
    value = serializers.SerializerMethodField('unpickle_value')

    class Meta:
        model = InstanceMetadatum
        fields = ('url', 'id', 'name', 'value', 'paper', 'corpus',)

    def unpickle_value(self, obj):
        # JSON can't support the full range of data structures here (e.g. dict
        #  with tuple keys), so we'll just return the raw pickled object and
        #  let the client sort it out.
        return obj.value #str(pickle.loads(str(obj.value)))


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


class PaperInstanceSerializer(AcceptsRequestSerializer):
    citations = serializers.SerializerMethodField('citations_link')
    authors = serializers.SerializerMethodField('author_instances_link')
    institutions = serializers.SerializerMethodField('institution_instances_link')
    affiliations = serializers.SerializerMethodField('affiliation_instances_link')
    metadata = serializers.SerializerMethodField('metadatum_link')

    identifiers = InstanceIdentifierSerializer(many=True)

    class Meta:
        model = PaperInstance
        fields = ('url', 'id', 'corpus', 'publication_date', 'title', 'volume',
                  'issue', 'journal', 'abstract', 'concrete', 'cited_by',
                  'citations', 'authors', 'institutions', 'affiliations',
                  'metadata', 'identifiers', 'checksum')

    def citations_link(self, obj):
        params = {'cited_by': obj.id, 'concrete': False}
        return link_for('paperinstance-list', self.request, params)

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
        return link_for('instancemetadatum-list', self.request, params)


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
        return link_for('paperinstance-list', self.request, params)

    def citations_link(self, obj):
        params = {'corpus': obj.id, 'concrete': False}
        return link_for('paperinstance-list', self.request, params)

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
        return link_for('instancemetadatum-list', self.request, params)


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

    def create(self, request):
        max_id = Corpus.objects.aggregate(Max('id'))['id__max']
        if max_id:
            max_id += 1
        else:
            max_id = 1
        corpus = Corpus.objects.create(**{
            'created_by': request.user,
            'source': request.POST.get('source'),
            'id': max_id,
            'label': request.POST.get('label'),
        })
        serializer = self.get_serializer(corpus, request=request)
        return Response(serializer.data)


class AuthorInstanceViewSet(PassRequestToSerializerMixin, CreatorOnlyMixin, viewsets.ModelViewSet):
    queryset = AuthorInstance.objects.all()
    serializer_class = AuthorInstanceSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = AuthorInstanceFilter

    def create(self, request):
        max_id = AuthorInstance.objects.aggregate(Max('id'))['id__max']
        if max_id:
            max_id += 1
        else:
            max_id = 1
        data = json.loads(request.POST.get('data'))
        id_map = {}
        if type(data) is list and len(data) > 0:
            instances = []
            for datum in data:
                temp_ident = datum.pop('id')
                id_map[temp_ident] = max_id
                datum.update({'id': max_id, 'created_by': request.user})
                max_id += 1
                instances.append(AuthorInstance(**datum))
            AuthorInstance.objects.bulk_create(instances)
        return Response({'id_map': id_map})


class InstitutionInstanceViewSet(CreatorOnlyMixin, viewsets.ModelViewSet):
    queryset = InstitutionInstance.objects.all()
    serializer_class = InstitutionInstanceSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = InstitutionInstanceFilter

    def create(self, request):
        max_id = InstitutionInstance.objects.aggregate(Max('id'))['id__max']
        if max_id:
            max_id += 1
        else:
            max_id = 1
        data = json.loads(request.POST.get('data'))
        id_map = {}
        if type(data) is list and len(data) > 0:
            instances = []
            for datum in data:
                temp_ident = datum.pop('id')
                id_map[temp_ident] = max_id
                datum.update({'id': max_id, 'created_by': request.user})
                max_id += 1
                instances.append(InstitutionInstance(**datum))
            InstitutionInstance.objects.bulk_create(instances)
        return Response({'id_map': id_map})


class AffiliationInstanceViewSet(CreatorOnlyMixin, viewsets.ModelViewSet):
    queryset = AffiliationInstance.objects.all()
    serializer_class = AffiliationInstanceSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = AffiliationInstanceFilter

    def create(self, request):
        max_id = AffiliationInstance.objects.aggregate(Max('id'))['id__max']
        if max_id:
            max_id += 1
        else:
            max_id = 1
        data = json.loads(request.POST.get('data'))
        id_map = {}
        if type(data) is list and len(data) > 0:
            instances = []
            for datum in data:
                temp_ident = datum.pop('id')
                id_map[temp_ident] = max_id
                datum.update({'id': max_id, 'created_by': request.user})
                max_id += 1
                instances.append(AffiliationInstance(**datum))
            AffiliationInstance.objects.bulk_create(instances)
        return Response({'id_map': id_map})


class PaperInstanceViewSet(PassRequestToSerializerMixin, CreatorOnlyMixin, viewsets.ModelViewSet):
    queryset = PaperInstance.objects.all()
    serializer_class = PaperInstanceSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = PaperInstanceFilter

    def create(self, request):
        max_id = PaperInstance.objects.aggregate(Max('id'))['id__max']
        if max_id:
            max_id += 1
        else:
            max_id = 1
        data = json.loads(request.POST.get('data'))
        id_map = {}
        if type(data) is list and len(data) > 0:
            instances = []
            for datum in data:
                temp_ident = datum.pop('id')
                id_map[temp_ident] = max_id
                datum.update({'id': max_id, 'created_by': request.user})
                # Citations may be lurking in here.
                if 'cited_by_id' in datum:
                    ident = datum['cited_by_id']
                    datum['cited_by_id'] = id_map.get(ident, ident)
                max_id += 1
                instances.append(PaperInstance(**datum))
            PaperInstance.objects.bulk_create(instances)
        return Response({'id_map': id_map})


class InstanceMetadatumViewSet(CreatorOnlyMixin, viewsets.ModelViewSet):
    queryset = InstanceMetadatum.objects.all()
    serializer_class = InstanceMetadatumSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = InstanceMetadatumFilter

    def create(self, request):
        max_id = InstanceMetadatum.objects.aggregate(Max('id'))['id__max']
        if max_id:
            max_id += 1
        else:
            max_id = 1
        data = json.loads(request.POST.get('data'))
        id_map = {}
        if type(data) is list and len(data) > 0:
            instances = []
            for datum in data:
                temp_ident = datum.pop('id')
                id_map[temp_ident] = max_id
                datum.update({'id': max_id, 'created_by': request.user})
                max_id += 1
                instances.append(InstanceMetadatum(**datum))
            InstanceMetadatum.objects.bulk_create(instances)
        return Response({'id_map': id_map})


class InstanceIdentifierViewSet(CreatorOnlyMixin, viewsets.ModelViewSet):
    queryset = InstanceIdentifier.objects.all()
    serializer_class = InstanceIdentifierSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = InstanceIdentifierFilter

    def create(self, request):
        max_id = InstanceIdentifier.objects.aggregate(Max('id'))['id__max']
        if max_id:
            max_id += 1
        else:
            max_id = 1
        data = json.loads(request.POST.get('data'))
        id_map = {}
        if type(data) is list and len(data) > 0:
            instances = []
            for datum in data:
                temp_ident = datum.pop('id')
                id_map[temp_ident] = max_id
                datum.update({'id': max_id, 'created_by': request.user})
                max_id += 1
                instances.append(InstanceIdentifier(**datum))
            InstanceIdentifier.objects.bulk_create(instances)
        return Response({'id_map': id_map})



def home(request):
    template = "tethneweb/home.html"
    context = RequestContext(request, {
        'paper_count': PaperInstance.objects.filter(concrete=True).count(),
        'citation_count': PaperInstance.objects.filter(concrete=False).count(),
        'author_count': AuthorInstance.objects.count()
    })

    return render(request, template, context)


def check_unique(request):
    if request.method == 'GET':
        checksum = request.GET.get('checksum')
        corpus_id = request.GET.get('corpus')
        unique = PaperInstance.objects.filter(checksum=checksum, corpus=corpus_id).count() == 0
        return JsonResponse({'unique': unique})
    elif request.method == 'POST':
        checksums = request.POST.get_list('checksum')
        corpus_id = request.POST.get('corpus')
        return JsonResponse({
            'unique': [
                PaperInstance.objects.filter(checksum=checksum, corpus=corpus_id).count() == 0
                for checksum in checksums
            ]})
