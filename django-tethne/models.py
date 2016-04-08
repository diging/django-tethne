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




class Paper(models.Model):
    """
    Model name = Paper

    Each paper belongs to a Corpus. So, a foriegn key reference is created to the Corpus.

    """
    corpus = models.ForeignKey(Corpus, related_name='collection')
    pub_date = models.DateField(null=True)
    title = models.CharField(max_length=1000, null=True)
    volume = models.CharField(max_length=40, null=True)
    issue = models.CharField(max_length=40, null=True)
    abstract = models.TextField(null=True)




class Author(models.Model):
    """
    Model name = 'Author'
    Each author will has FirstName and LastName.

    TO_DO - Think of any missing useful attributes that can be added

    """
    first_name = models.CharField(max_length=45, null=True)
    last_lname = models.CharField(max_length=45, null=True)
    identifier = models.CharField(max_length=1000, null=True)




class Author_Instance(models.Model):
    """
    Model name = 'Author_Instance'
    This refers to the Paper instance(Foreign Key) and thus represents a record in the corpus.

    """
    paper = models.ForeignKey(Paper, related_name='authorinstance_by')
    author = models.ForeignKey(Author, related_name='authorinstance_name')
    first_name = models.CharField(max_length=45, null=True)
    last_name = models.CharField(max_length=45, null=True)




class Author_Identity(models.Model):

    """
    Model name : Author_Identity
    This represents the relation Author <-> Author_identity <-> Author_instance.
    An additional field confidence is added in this relation.

    """
    author = models.ForeignKey(Author, related_name='authoridentity_name')
    author_instance = models.ForeignKey(Author_Instance, related_name='authoridentity_instance')
    confidence = models.FloatField(null=True, default=0.0)


class Institution(models.Model):
    """
    Model Name : Institution
    Will store all the details of a specific institution
    """
    name = models.CharField(max_length=1000, null=True)
    addressLine1 = models.CharField(max_length=1000, null=True)
    addressLine2 = models.CharField(max_length=1000, null=True)
    state = models.CharField(max_length=1000, null=True)
    city = models.CharField(max_length=1000, null=True)
    zip = models.CharField(max_length=1000, null=True)
    country = models.CharField(max_length=1000, null=True)




class Institution_Instance(models.Model):
    """
    Model Name : Institution_Instance

    Will store a record that appears in the Corpus.
    Thus refers to the Paper.
    """
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





class Institution_Identity(models.Model):
    """
    Model : Insitution_Identity.
    has a relation to Institution and Instance_instance with confidence field
    """
    institution = models.ForeignKey(Institution, related_name='institutionidentity_name')
    institution_instance = models.ForeignKey(Institution_Instance, related_name='insitutionidentity_instance')
    confidence = models.FloatField(null=True, default=0.0)



class Affiliation(models.Model):
    """
    Model : Affiliation
    represents a affiliation between an author and an instance.
    """
    author = models.ForeignKey(Author, related_name='affiliation_authorname')
    institution = models.ForeignKey(Institution, related_name='affiliation_institution')
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    confidence = models.FloatField(null=True, default=0.0)


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






