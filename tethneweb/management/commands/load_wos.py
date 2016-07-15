from django.core.management.base import BaseCommand, CommandError
from django.db.models import Max

import os
import cPickle as pickle
from collections import Counter, defaultdict

from tethneweb.models import *
from tethne.readers import wos


identifier_fields = ['doi', 'ayjid', 'issn', 'isbn', 'uri']
paper_fields = [
    ('date', 'publication_date'),
    ('title', 'title'),
    ('volume', 'volume'),
    ('issue', 'issue'),
    ('abstract', 'abstract'),
    ('journal', 'journal'),
]

exclude_fields = [
    'citations',
    'citedReferences'
]


class CorpusHandler(object):
    _add_order = [
        ('Paper', Paper),
        ('Identifier', Identifier),
        ('Metadatum', Metadatum),
        ('AuthorInstance', AuthorInstance),
        ('InstitutionInstance', InstitutionInstance),
        ('AffiliationInstance', AffiliationInstance),
    ]

    def __init__(self, tethne_corpus, label, batch_size=100):
        self.batch_size = batch_size
        self.primary_keys = Counter()
        for model_name, model in self._add_order + [('Corpus', Corpus)]:
            max_id = model.objects.aggregate(Max('id'))['id__max']
            self.primary_keys[model_name] = max_id + 1 if max_id else 1
        self.hoppers = defaultdict(list)

        self.corpus = Corpus.objects.create(**{
            'id': self.primary_keys['Corpus'],
            'source': Corpus.WOS,
            'label': label,
            'created_by_id': 1,
        })
        self.tethne_corpus = tethne_corpus

    def run(self):
        for tethne_paper in self.tethne_corpus:
            paper_id = self._handle_paper(tethne_paper)

            for tethne_reference in getattr(tethne_paper, 'citedReferences', []):
                self._handle_cited_reference(tethne_reference, paper_id)

            if len(self.hoppers['Paper']) >= self.batch_size:
                self._commit()
        self._commit()

    def _commit(self):
        for model_name, model in self._add_order:
            model.objects.bulk_create(self.hoppers[model_name])
            print 'Created %i instances of %s' % (len(self.hoppers[model_name]), model_name)
            self.hoppers[model_name] = []

    def _add_instance(self, model_name, instance):
        ident = self.primary_keys[model_name]
        instance.id = ident
        self.hoppers[model_name].append(instance)
        self.primary_keys[model_name] += 1
        return ident

    def _exclude_paper_field(self, field):
        exclude = list(zip(*paper_fields)[0]) + identifier_fields + exclude_fields
        return field.startswith('_') or field in exclude

    def _generate_metadata(self, tethne_paper):
        # Generate data for Metadatum model.
        metadata = []

        for field, value in tethne_paper.__dict__.iteritems():
            if self._exclude_paper_field(field):
                continue
            value = pickle.dumps(value)
            # if type(value) is not unicode:
            #     value = pickle.dumps(value)

            metadata.append({
                'name': field,
                'value': value,
                'corpus_id': self.corpus.id,
                'created_by_id': 1,
            })
        return metadata


    def _generate_identifiers(self, tethne_paper):
        # Generate data for Identifier model.
        identifiers = []
        for field in identifier_fields:
            value = getattr(tethne_paper, field, None)
            if value:
                identifiers.append({
                    'name': field,
                    'value': value,
                    'corpus_id': self.corpus.id,
                    'created_by_id': 1,
                })
        return identifiers


    def _handle_paper(self, tethne_paper, **additional):
        paper_data = {}
        for pfield, dbfield in paper_fields:
            value = getattr(tethne_paper, pfield, None)
            if value:
                paper_data[dbfield] = value

        paper_data.update({
            'corpus_id': self.corpus.id,
            'created_by_id': 1,
        })
        paper_data.update(**additional)
        paper_id = self._add_instance('Paper', Paper(**paper_data))

        metadata = []
        for metadata_data in self._generate_metadata(tethne_paper):
            metadata_data.update({'paper_id': paper_id})
            self._add_instance('Metadatum', Metadatum(**metadata_data))

        identifiers = []
        for identifier_data in self._generate_identifiers(tethne_paper):

            identifier_data.update({'paper_id': paper_id})
            self._add_instance('Identifier', Identifier(**identifier_data))

        self._handle_authors(tethne_paper, paper_id)
        return paper_id


    def _handle_cited_reference(self, tethne_reference, paper_id):
        return self._handle_paper(tethne_reference, cited_by_id=paper_id, concrete=False)


    def _handle_institution(self, address, paper_id):
        return self._add_instance('InstitutionInstance', InstitutionInstance(**{
            'name': address[0],
            'country': address[1],
            'address': address[2],
            'paper_id': paper_id,
            'corpus_id': self.corpus.id,
            'created_by_id': 1,
        }))

    def _handle_authors(self, tethne_paper, paper_id):
        # So that we don't create multiple InstitutionInstances for what are clearly
        #  the same institutions, we first extract all unique address tuples and
        #  create InstitutionInstances before proceeding.
        addresses = getattr(tethne_paper, 'addresses', {})
        normalize = lambda a: (a[0], a[1], ', '.join(a[2]))
        institution_instances = {i: self._handle_institution(i, paper_id) for i
                                 in set([normalize(j) for jset in addresses.values() for j in jset])}

        institutions = {
            name: [institution_instances[normalize(address)] for address in author_addresses]
            for name, author_addresses in addresses.items()
        }

        authors = []
        affiliations = []
        for tethne_author in tethne_paper.authors:
            author_id = self._add_instance('AuthorInstance', AuthorInstance(**{
                'paper_id': paper_id,
                'last_name': tethne_author[0][0],
                'first_name': tethne_author[0][1],
                'corpus_id': self.corpus.id,
                'created_by_id': 1,
            }))

            tethne_affiliations = institutions.get(tethne_author,
                                                   institutions.get('__all__',
                                                                    None))
            if not tethne_affiliations:
                continue

            for institution_id in tethne_affiliations:
                self._add_instance('AffiliationInstance', AffiliationInstance(**{
                    'paper_id': paper_id,
                    'author_id': author_id,
                    'institution_id': institution_id,
                    'confidence': 1./len(tethne_affiliations),
                    'corpus_id': self.corpus.id,
                    'created_by_id': 1,
                }))


class Command(BaseCommand):
    help = 'Load web of science data.'

    def add_arguments(self, parser):
        parser.add_argument('path', nargs=1, type=str)
        parser.add_argument('label', nargs=1, type=str)
        parser.add_argument('batch_size', nargs=1, type=int)

    def handle(self, *args, **options):
        path = options.get('path')[0]
        label = options.get('label')[0]
        batch_size = options.get('batch_size')[0]

        tethne_corpus = wos.read(path, streaming=True)
        handler = CorpusHandler(tethne_corpus, label, batch_size)
        handler.run()
