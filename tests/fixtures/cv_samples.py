"""Curriculums ficticios usados en pruebas de integracion."""


SPANISH_CV_PAGES = (
    """\
Alex Rivera
Backend Developer
alex.rivera@example.test
+34 000 000 000
linkedin.com/in/cv-test-alex-rivera
github.com/cv-test-alex-rivera
alexrivera.dev
PERFIL PROFESIONAL
Desarrollador de servicios web y automatizaciones.
EXPERIENCIA PROFESIONAL
Northwind Labs - Backend Developer
- Desarrollo de APIs en Python
""",
    """\
FORMACION ACADEMICA
Grado en Ingenieria Informatica
HABILIDADES
Python, FastAPI, PostgreSQL
IDIOMAS
Ingles - C1
CERTIFICACIONES
Python Professional
CURSOS
Arquitectura de software
PROYECTOS
Analizador de CV
""",
)


ENGLISH_CV_PAGES = (
    """\
Sam Taylor
Data Analyst
sam.taylor@example.test
SUMMARY
Analyst focused on reliable reporting.
WORK EXPERIENCE
Contoso - Data Analyst
- Built operational dashboards
EDUCATION
BSc in Statistics
TECHNICAL SKILLS
SQL; Power BI
LANGUAGES
English: Native
""",
)


HEADERLESS_CV_PAGES = (
    """\
Taylor Morgan
taylor.morgan@example.test
Independent consultant working with Python.
Available for remote projects.
""",
)


DUPLICATE_SECTION_CV_PAGES = (
    """\
Jordan Lee
Software Engineer
EXPERIENCE
First role retained
EXPERIENCE
Second role retained
""",
)


MULTI_EXPERIENCE_CV_PAGES = (
    """\
Morgan Price
Software Engineer
EXPERIENCE
Northwind Labs - Backend Developer
January 2021 - December 2022
- Built internal APIs
Contoso - Senior Engineer
2023 - Present
- Led the platform team
SKILLS
Python, SQL
""",
)


SPARSE_CV_PAGES = (
    """\
Riley Stone
Product Designer
EDUCATION
Bachelor of Design | Design Institute
2018 - 2022
SKILLS
Figma
""",
)
