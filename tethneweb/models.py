from django.db import models
from django.contrib.auth.models import User


class CorpusComponentMixin(models.Model):
    corpus = models.ForeignKey('Corpus')
    date_created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User)

    class Meta:
        abstract = True


class DisambiguationModel(models.Model):
    """
    A system of assertions about identities and affiliations.
    """
    id = models.PositiveIntegerField(primary_key=True)
    label = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User)
    methods = models.TextField()
    """
    Notes on the methods used to generate this :class:`.DisambiguationModel`\.
    """


class DisambiguationMixin(models.Model):
    """
    Mixin for Identity models.
    """
    id = models.PositiveIntegerField(primary_key=True)
    model = models.ForeignKey('DisambiguationModel')
    confidence = models.FloatField(default=0.0)
    methods = models.TextField()
    """
    Notes on the methods used to generate this identity.
    """

    class Meta:
        abstract = True


class Corpus(models.Model):
    """
    A collection of bibliographic records.

    Each :class:`.Corpus` shall have a single :class:`.Source`\.
    """
    id = models.PositiveIntegerField(primary_key=True)

    JSTOR = 'JSTOR'
    WOS = 'WOS'
    ZOTERO = 'ZOTERO'
    SCOPUS = 'SCOPUS'
    SOURCE_CHOICES = (
        (JSTOR, 'JSTOR DfR'),
        (WOS, 'Web of Science'),
        (ZOTERO, 'Zotero'),
        (SCOPUS, 'Scopus')
    )
    source = models.CharField(max_length=35, choices=SOURCE_CHOICES)
    date_created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User)
    label = models.CharField(max_length=255)

    # def __len__(self):
    #     return self.papers.count()

    def __unicode__(self):
        return self.label


class InstanceMetadatum(CorpusComponentMixin):
    """
    Catch-all model for freeform bibliographic metadata.
    """
    id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    value = models.TextField()
    paper = models.ForeignKey('PaperInstance', related_name='metadata')
    """The record that the :class:`.Metadatum` describes."""


class InstanceIdentifier(CorpusComponentMixin):
    """
    A unique identifier for a :class:`.Paper`\.
    """
    id = models.PositiveIntegerField(primary_key=True)

    paper = models.ForeignKey('PaperInstance', related_name='identifiers')
    """The record that the :class:`.Identifier` instance identifies."""

    name = models.CharField(max_length=255)
    """E.g. LoC, URL."""

    value = models.CharField(max_length=255)


class Paper(CorpusComponentMixin):
    """
    A single bibliographic record.
    """
    id = models.PositiveIntegerField(primary_key=True)
    publication_date = models.IntegerField(null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    volume = models.CharField(max_length=40, null=True, blank=True)
    issue = models.CharField(max_length=40, null=True, blank=True)
    journal = models.CharField(max_length=255, null=True, blank=True)
    abstract = models.TextField(null=True)

    concrete = models.BooleanField(default=True)
    cited_by = models.ForeignKey('Paper', related_name='cited_references', null=True, blank=True)


class Author(models.Model):
    """
    Represents a specific person who has written scholarly texts.

    :class:`.Author`\s are related to bibliographic records (:class:`.Paper`\s)
    only by way of :class:`.AuthorInstance`\s. This model should not be
    populated directly from data.
    """
    id = models.PositiveIntegerField(primary_key=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    initials =  models.CharField(max_length=255, null=True, blank=True)
    identifier = models.CharField(max_length=255, null=True, blank=True)
    """
    E.g. a Conceptpower, VIAF or DBPedia URI.
    """

    description = models.TextField()


class Institution(models.Model):
    """
    Represents a specific institituion or organization with whom one or more
    :class:`.Author`\s may be affiliated.
    """
    id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    address = models.TextField()
    state = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    zip = models.CharField(max_length=10, null=True, blank=True)
    """Supports zip+4 (including the hyphen)."""

    country = models.CharField(max_length=255, null=True, blank=True)


class PaperInstance(CorpusComponentMixin):
    """
    A single bibliographic record.
    """
    id = models.PositiveIntegerField(primary_key=True)

    checksum = models.TextField(blank=True, null=True)
    """Can be used to avoid adding duplicate data."""

    publication_date = models.IntegerField(null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    volume = models.CharField(max_length=40, null=True, blank=True)
    issue = models.CharField(max_length=40, null=True, blank=True)
    journal = models.CharField(max_length=255, null=True, blank=True)
    abstract = models.TextField(null=True)

    concrete = models.BooleanField(default=True)
    cited_by = models.ForeignKey('PaperInstance', related_name='cited_references', null=True, blank=True)


class AuthorInstance(CorpusComponentMixin):
    """
    An instantiation of an :class:`.Author` in a particular bibliographic
    record.

    We may not know who the corresponding :class:`.Author` is. This model should
    be directly populated from data.
    """
    id = models.PositiveIntegerField(primary_key=True)
    paper = models.ForeignKey('PaperInstance', related_name='author_instances')

    first_name = models.CharField(max_length=255, null=True, blank=True)
    """We may only have a surname, so this is optional."""

    last_name = models.CharField(max_length=255)


class InstitutionInstance(CorpusComponentMixin):
    """
    An instantiation of an :class:`.Institution` in a particular bibliographic
    record.

    We may not know who the corresponding :class:`.InstitutionInstance` is. This
    model should be populated directly from data.
    """
    id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    paper = models.ForeignKey('PaperInstance', related_name='institutions')

    department = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField()
    state = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    zip = models.CharField(max_length=10, null=True, blank=True)
    """Supports zip+4 (including the hyphen)."""

    country = models.CharField(max_length=255, null=True, blank=True)


class AffiliationInstance(CorpusComponentMixin):
    """
    A (probable) affiliation between an :class:`.AuthorInstance` and an
    :class:`.InstitutionInstance`\.
    """
    id = models.PositiveIntegerField(primary_key=True)
    paper = models.ForeignKey('PaperInstance', related_name='affiliations')
    author = models.ForeignKey('AuthorInstance', related_name='affiliations')
    institution = models.ForeignKey('InstitutionInstance',
                                    related_name='affiliations')
    confidence = models.FloatField(default=0.0)
    """
    If we have a precise author-institution mapping, this will be 1.0. Otherwise
    this should be 1./N (number of possible institutions).
    """


class AuthorIdentity(DisambiguationMixin):
    """
    Represents the assertion that an :class:`.AuthorInstance` is an instance of
    a particular :class:`.Author`\.

    """
    author = models.ForeignKey('Author', related_name='instantiations')
    instance = models.ForeignKey('AuthorInstance', related_name='identities')


class InstitutionIdentity(DisambiguationMixin):
    """
    Represents the assertion that an :class:`.InstitutionInstance` is an
    instance of a particular :class:`.Institution`\.
    """
    institution = models.ForeignKey('Institution',
                                    related_name='instantiations')
    instance = models.ForeignKey('InstitutionInstance',
                                 related_name='identities')


class Affiliation(DisambiguationMixin):
    """
    Represents the assertion that an :class:`.Author` is affiliated with a
    specific :class:`.Institution`.
    """

    author = models.ForeignKey(Author, related_name='affiliations')
    institution = models.ForeignKey(Institution, related_name='affiliates')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    occur_date = models.DateField(null=True, blank=True)


class PaperIdentity(DisambiguationMixin):
    """
    Represents the assertion that a :class:`.PaperInstance` refers to a
    specific :class:`.Paper`\.
    """
    paper = models.ForeignKey('Paper', related_name='instantiations')
    instance = models.ForeignKey('PaperInstance', related_name='identities')
