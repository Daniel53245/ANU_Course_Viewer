from rdflib import Graph, Literal, RDF, URIRef, Namespace
from rdflib.namespace import FOAF, XSD


class Course:
    def __init__(self, name, school=None):
        self.name = name
        self.school = school
        self.prequisites = set()
        self.course_code = None
        self.prequiste_course = {}

    def add_prequisite(self, course):
        self.prequisites.add(course)

    def __str__(self):
        str = ""
        if self.school:
            str += f"{self.school}: "
        str += self.name
        str += "\n"
        if self.prequisites:
            str += "Prerequisites:\n"
            for course in self.prequisites:
                str += f"  {course}\n"
        return str

    def generate_uid(self):
        return f"{self.course_code}"

    def to_rdf(self):
        # Define a namespace
        ex = Namespace("http://caligula.today/onto#")
        data = Namespace("http://caligula.today/data/")
        # List to store the triples
        triples = []

        # Process each course in the list
        course_uri = data[self.generate_uid()]
        triples.append((course_uri, RDF.type, ex.Course))
        triples.append(
            (course_uri, ex.courseString, Literal(self.name, datatype=XSD.string))
        )
        for (
            related_course_string,
            related_course_instance,
        ) in self.prequiste_course.items():
            related_course_uri = data[related_course_instance.generate_uid()]
            triples.append((course_uri, ex.prequusite_from, related_course_uri))
            triples.append((related_course_uri, RDF.type, ex.Course))
            triples.append(
                (
                    related_course_uri,
                    ex.courseString,
                    Literal(related_course_instance.course_code, datatype=XSD.string),
                )
            )

        return triples
