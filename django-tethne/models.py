from django.db import models


class Source(models.Model):

    """
    Model Name = Source

    Source represents the source of the Corpus
    Example 1. JSTOR, 2. ZOTERO or 3. WOS
    """
    JSTOR = 'JSTOR'
    WOS = 'WOS'
    ZOTERO = 'ZOTERO'
    SCOPUS = 'SCOPUS'
    name_choices = (
        (JSTOR, 'Jstor'),
        (WOS, 'World of Science'),
        (ZOTERO, 'Zotero'),
        (SCOPUS, 'Scopus')
    )

    name = models.CharField(max_length=35, choices=name_choices, null=True)



class Corpus(models.Model):
    """

    Model name = Corpus
    Will store the corpus details, for example source, the number of papers and label.
    """
    source = models.ForeignKey(Source, related_name='corpora')
    date_created = models.DateTimeField(auto_now_add=True)
    length = models.IntegerField(null=True)
    label = models.CharField(max_length=10, null=True)



class PaperManager(models.Manager):
    def get_by_natural_key(self, corpus, paper_id):
        return self.get(paper_id=paper_id, corpus=corpus)

class Paper(models.Model):
    """
    Model name = Paper

    Each paper belongs to a Corpus. So, a foriegn key reference is created to the Corpus.

    """
    objects = PaperManager()
    paper_id = models.CharField(max_length=355)
    corpus = models.ForeignKey(Corpus, related_name='collection')
    pub_date = models.CharField(max_length=355)
    title = models.CharField(max_length=1000, null=True)
    volume = models.CharField(max_length=40, null=True)
    issue = models.CharField(max_length=40, null=True)
    abstract = models.TextField(null=True)

    class Meta:
        unique_together = (('paper_id', 'corpus'),)



class AuthorManager(models.Manager):
    def get_by_natural_key(self, first_name, last_name):
        return self.get(first_name=first_name, last_name=last_name)


class Author(models.Model):
    """
    Model name = 'Author'
    Each author will has FirstName and LastName.

    TO_DO - Think of any missing useful attributes that can be added

    """
    objects = AuthorManager()
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    identifier = models.CharField(max_length=1000, null=True)

    class Meta:
        unique_together = (('first_name', 'last_name'), )


class AuthorInstanceManager(models.Manager):
    def get_by_natural_key(self, author, paper):
        return self.get(author=author, paper=paper)



class Author_Instance(models.Model):
    """
    Model name = 'Author_Instance'
    This refers to the Paper instance(Foreign Key) and thus represents a record in the corpus.

    """
    objects = AuthorInstanceManager()
    paper = models.ForeignKey(Paper, related_name='authorinstance_by')
    author = models.ForeignKey(Author, related_name='authorinstance_name')
    first_name = models.CharField(max_length=45, null=True)
    last_name = models.CharField(max_length=45, null=True)

    class Meta:
        unique_together = (('paper', 'author'), )



class AuthorIdentityManager(models.Manager):
    def get_by_natural_key(self, author, author_instance):
        return self.get(author=author, author_instance=author_instance)

class Author_Identity(models.Model):

    """
    Model name : Author_Identity
    This represents the relation Author <-> Author_identity <-> Author_instance.
    An additional field confidence is added in this relation.

    """
    objects = AuthorIdentityManager()
    author = models.ForeignKey(Author, related_name='authoridentity_name')
    author_instance = models.ForeignKey(Author_Instance, related_name='authoridentity_instance')
    confidence = models.FloatField(null=True, default=0.0)

    class Meta:
        unique_together = (('author', 'author_instance'), )



class InstitutionManager(models.Manager):
    def get_by_natural_key(self, name, city):
        return self.get(name=name, city=city)


class Institution(models.Model):
    """
    Model Name : Institution
    Will store all the details of a specific institution
    """
    objects = InstitutionManager()
    name = models.CharField(max_length=1000, null=True)
    addressLine1 = models.CharField(max_length=1000, null=True)
    addressLine2 = models.CharField(max_length=1000, null=True)
    state = models.CharField(max_length=1000, null=True)
    city = models.CharField(max_length=1000, null=True)
    zip = models.CharField(max_length=1000, null=True)
    country = models.CharField(max_length=1000, null=True)

    #def natural_key(self):
     #   return (self.name, self.city)

    class Meta:
        unique_together = (('name', 'city'), )



class InstitutionInstanceManager(models.Manager):
    def get_by_natural_key(self, institution, paper):
        return self.get(institution=institution, paper=paper)


class Institution_Instance(models.Model):
    """
    Model Name : Institution_Instance

    Will store a record that appears in the Corpus.
    Thus refers to the Paper.
    """
    objects = InstitutionInstanceManager()
    institution = models.ForeignKey(Institution, related_name='insitution_name')
    paper = models.ForeignKey(Paper, related_name='institution_paper')
    department = models.CharField(max_length=1000, null=True)
    name = models.CharField(max_length=1000, null=True)
    addressLine1 = models.CharField(max_length=1000, null=True)
    addressLine2 = models.CharField(max_length=1000, null=True)
    state = models.CharField(max_length=1000, null=True)
    city = models.CharField(max_length=1000, null=True)
    zip = models.CharField(max_length=1000, null=True)
    country = models.CharField(max_length=1000, null=True)

    def natural_key(self):
        return (self.institution, self.paper)

    class Meta:
        unique_together = (('institution', 'paper'), )




class InstitutionIdentityManager(models.Manager):
    def get_by_natural_key(self, institution, institution_instance):
        return self.get(institution=institution, institution_instance=institution_instance)

class Institution_Identity(models.Model):
    """
    Model : Insitution_Identity.
    has a relation to Institution and Instance_instance with confidence field
    """
    objects = InstitutionIdentityManager()
    institution = models.ForeignKey(Institution, related_name='institutionidentity_name')
    institution_instance = models.ForeignKey(Institution_Instance, related_name='insitutionidentity_instance')
    confidence = models.FloatField(null=True, default=0.0)

    def natural_key(self):
        return (self.institution, self.institution_instance)


    class Meta:
        unique_together = (('institution', 'institution_instance'),)



class AffiliationManager(models.Manager):
    def get_by_natural_key(self, institution, author, start_date):
        return self.get(institution=institution, author=author, start_date=start_date)

class Affiliation(models.Model):
    """
    Model : Affiliation
    represents a affiliation between an author and an instance.
    """
    objects = AffiliationManager()
    author = models.ForeignKey(Author, related_name='affiliation_authorname')
    institution = models.ForeignKey(Institution, related_name='affiliation_institution')
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    confidence = models.FloatField(null=True, default=0.0)

    def natural_key(self):
        return (self.author, self.institution, self.start_date)

    class Meta:
        unique_together = (('author', 'institution', 'start_date'), )


class Affiliation_Instance(models.Model):
    """
    Model : Affiliation_Instance
    relation between author_instance and Institution_Instance with confidence.(between 0.0 and 1.0)
    """
    author_instance = models.ForeignKey(Author_Instance, related_name='affiliationinstance_authorinstance')
    institution_instance = models.ForeignKey(Institution_Instance, related_name='affiliationinstance_institutionInstance')
    confidence = models.FloatField(null=True, default=0.0)


class Citation(models.Model):
    """
    Model : Citation.

    TO_CHECK - "Do we need a Foreign Key reference to 'PAPER' in 'CITATION' or 'CITATION_INSTANCE' ??

    """
    paper = models.ForeignKey(Paper, related_name='papercited')
    literal = models.CharField(max_length=255, null=True)
    journal = models.CharField(max_length=255, null=True)
    first_author = models.CharField(max_length=45, null=True)
    date = models.DateField(null=True)



class Citation_Instance(models.Model):
    """
    Model : Citation_Instance.
    represents a record in the Corpus.
    """
    citation = models.ForeignKey(Citation, related_name='citation')
    paper = models.ForeignKey(Paper, auto_created='ciation_papercited')
    literal = models.CharField(max_length=255, null=True)
    journal = models.CharField(max_length=255, null=True)
    first_author = models.CharField(max_length=45, null=True)
    date = models.DateField(null=True)


class Citation_Identity(models.Model):

    citation = models.ForeignKey(Citation, related_name='identity_citation')
    citation_instance = models.ForeignKey(Citation_Instance, related_name='identity_citationinstance')
    confidence = models.FloatField(null=True, default=0.0)






