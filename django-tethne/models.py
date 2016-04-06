from django.db import models



"""
Model Name = Source

Source represents the source of the Corpus
Example 1. JSTOR, 2. ZOTERO or 3. WOS
"""
class Source(models.Model):
    source_value = models.CharField(max_length=35, null=True)

"""

Model name = Corpus
Will store the corpus details, for example source, the number of papers and label.
"""

class Corpus(models.Model):
    source = models.ForeignKey(Source)
    date_created = models.DateTimeField(auto_now=True, auto_created=True)
    length = models.IntegerField(null=True)
    label = models.CharField(max_length=10, null=True)


"""
Model name = Paper

Each paper belongs to a Corpus. So, a foriegn key reference is created to the Corpus.

"""

class Paper(models.Model):
    corpus = models.ForeignKey(Corpus)
    pub_date = models.DateField(null=True)
    is_collaborated = models.BooleanField()
    title = models.TextField(null=True)
    volume = models.CharField(max_length=40, null=True)
    issue = models.CharField(max_length=40, null=True)
    abstract = models.TextField(null=True)


"""
Model name = 'Author'
Each author will has FirstName and LastName.

TO_DO - Think of any missing useful attributes that can be added

"""

class Author(models.Model):
    au_fname = models.CharField(max_length=45, null=True)
    au_lname = models.CharField(max_length=45, null=True)


"""
Model name = 'Author_Instance'
This refers to the Paper instance(Foreign Key) and thus represents a record in the corpus.

"""

class Author_Instance(models.Model):
    paper = models.ForeignKey(Paper)
    author = models.ForeignKey(Author)
    au_fname = models.CharField(max_length=45, null=True)
    au_lname = models.CharField(max_length=45, null=True)



"""

Model name : Author_Identity
This represents the relation Author <-> Author_identity <-> Author_instance.
An additional field confidence is added in this relation.

"""

class Author_Identity(models.Model):
    author = models.ForeignKey(Author)
    author_instance = models.ForeignKey(Author_Instance)
    confidence = models.FloatField(null=True)



"""

Model Name : Institution

Will store all the details of a specific institution

"""

class Institution(models.Model):
    name = models.CharField(max_length=45, null=True)
    addressLine1 = models.CharField(max_length=50, null=True)
    addressLine2 = models.CharField(max_length=50, null=True)
    state = models.CharField(max_length=45, null=True)
    city = models.CharField(max_length=45, null=True)
    zip = models.CharField(max_length=45, null=True)
    country = models.CharField(max_length=45, null=True)


"""
Model Name : Institution_Instance

Will store a record that appears in the Corpus.
Thus refers to the Paper.
"""

class Institution_Instance(models.Model):
    institution = models.ForeignKey(Institution)
    paper = models.ForeignKey(Paper)
    department = models.CharField(max_length=45, null=True)
    name = models.CharField(max_length=45, null=True)
    addressLine1 = models.CharField(max_length=50, null=True)
    addressLine2 = models.CharField(max_length=50, null=True)
    state = models.CharField(max_length=45, null=True)
    city = models.CharField(max_length=45, null=True)
    zip = models.CharField(max_length=45, null=True)
    country = models.CharField(max_length=45, null=True)





class Institution_Identity(models.Model):
    institution = models.ForeignKey(Institution)
    institution_instance = models.ForeignKey(Institution_Instance)
    confidence = models.FloatField(null=True)



class Affiliation(models.Model):
    author = models.ForeignKey(Author)
    institution = models.ForeignKey(Institution)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    confidence = models.FloatField(null=True)


class Affiliation_instance(models.Model):
    author_instance = models.ForeignKey(Author_Instance)
    institution_instance = models.ForeignKey(Institution_Instance)


class Citation_Instance(models.Model):
    paper = models.ForeignKey(Paper)
    literal = models.CharField(max_length=45, null=True)
    journal = models.CharField(max_length=45, null=True)
    first_author = models.CharField(max_length=45, null=True)
    date = models.DateField(null=True)


class Citation_Indentity(models.Model):
    citation_instance = models.ForeignKey(Citation_Instance)
    confidence = models.FloatField(null=True)






