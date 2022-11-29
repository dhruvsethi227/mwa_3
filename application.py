from flask import Flask, render_template, redirect, request, url_for, abort, jsonify
from jinja2 import Environment, PackageLoader, select_autoescape
from flask import Response

import requests

from werkzeug.datastructures import Headers

import os
import time
import random

from jinja2 import Template

from logging.config import dictConfig

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, ForeignKey, String

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    },
     'file.handler': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'myapp.log',
            'maxBytes': 10000000,
            'backupCount': 5,
            'level': 'DEBUG',
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['file.handler']
    }
})

app = Flask(__name__)

# Globals
lessons = []
lesson1 = {}
lesson1['name'] = "Guitar1"
lesson1['instrument'] = "Guitar"
lesson1["demo_url"] = "https://abc.com"
lesson1["days"] = "MW"
lesson1["timings"] = "3:30 - 4.00"

lesson2 = {}
lesson2['name'] = "Guitar2"
lesson2['instrument'] = "Guitar"
lesson2["demo_url"] = "https://def.com"
lesson2["days"] = "TTh"
lesson2["timings"] = "3:30 - 4.00"

lesson3 = {}
lesson3['name'] = "Piano1"
lesson3['instrument'] = "Piano"
lesson3["demo_url"] = "https://pia.no"
lesson3["days"] = "TTh"
lesson3["timings"] = "3:30 - 4.00"

lessons.append(lesson1)
lessons.append(lesson2)
lessons.append(lesson3)

signed_up_students = []


# SQLite Database creation
Base = declarative_base()

# TODO: Change db name -- DONE
db_name = os.getenv("MUSIC_MARKETPLACE_DB","musicmarketplace.db")
db_url = "sqlite:///" + db_name
engine = create_engine(db_url, echo=True, future=True)
Session = sessionmaker(bind=engine)


class Lesson(Base):
    __tablename__ = 'lessons'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    instrument = Column(String)
    demo_url = Column(String)
    days = Column(String)
    timings = Column(String)
    signups = relationship("Signup", cascade="all, delete-orphan")

    def __repr__(self):
        return "<Lesson(name='%s', instrument='%s', demo_url='%s', days='%s', timings='%s')>" % (
                self.name, self.instrument, self.demo_url, self.days, self.timings)

    # Ref: https://stackoverflow.com/questions/5022066/how-to-serialize-sqlalchemy-result-to-json
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


# TODO: Add Person class - DONE
class Person(Base):
    __tablename__ = 'persons'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    role = Column(String)
    signups = relationship("Signup", cascade="all, delete-orphan")


    def __repr__(self):
        return "<Person(name='%s', role='%s')>" % (self.name, self.role)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Signup(Base):
    __tablename__ = 'signup'
    lessonId = Column(ForeignKey("lessons.id"), primary_key=True)
    #TODO: Add personId - DONE
    personId = Column(ForeignKey('persons.id'), primary_key=True)

    def __repr__(self):
        return "<Signup(lessonId='%d', personId='%d')>" % (self.lessonId, self.personId)

    # Ref: https://stackoverflow.com/questions/5022066/how-to-serialize-sqlalchemy-result-to-json
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}



Base.metadata.create_all(engine)



@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404


@app.route("/signups_in_memory")
def get_signups_previous():
    app.logger.info("Inside get_signups")

    names = ['alpha', 'beta', 'gamma', 'zeta', 'calisto', 'io', 'europa', 'ganymede']
    name = names[random.choice([1,2,3,4,5,6,7,8])-1]
    student = {}
    student['name'] = name
    signed_up_students.append(student)

    ret_obj = {}
    ret_obj['signups'] = signed_up_students
    return ret_obj


@app.route("/lessons_with_delay")
def get_lessons_with_delay():
    app.logger.info("Inside get_lessons_with_delay")
    time.sleep(10)
    ret_obj = {}
    if 'instrument' in request.args:
        instrument = request.args.get('instrument').strip().lower()
        lessons_to_ret = []
        for lesson in lessons:
            if instrument in lesson['instrument'].lower():
                lessons_to_ret.append(lesson)
    else:
        lessons_to_ret = lessons
    ret_obj['lessons'] = lessons_to_ret
    return ret_obj


@app.route("/lessons_by_name/<lesson_name>")
def get_lesson_from_in_memory_dict(lesson_name):
    app.logger.info("Inside get_lesson_from_in_memory_dict %s", lesson_name)
    lesson_to_ret = ""
    for lesson in lessons:
        if lesson['name'] == lesson_name:
            lesson_to_ret = lesson
            break

    if lesson_to_ret == "":
        abort(404)
        #abort(404, description=lesson_name + " not found")

    return lesson_to_ret


#### MusicMarketPlace REST API methods below
@app.route("/lessons", methods=['POST'])
def register_lesson():
    app.logger.info("Inside register_lesson")
    data = request.json
    app.logger.info("Received request:%s", str(data))

    name = data['name']
    instrument = data['instrument']
    timings = data['timings']
    demo_url = data['demo_url']
    days = data['days']

    lesson = Lesson(name=name,
                    instrument=instrument,
                    timings=timings,
                    demo_url=demo_url,
                    days=days)

    session = Session()
    session.add(lesson)
    session.commit()

    return lesson.as_dict()


@app.route("/lessons")
def get_lessons():
    app.logger.info("Inside get_lessons")
    ret_obj = {}

    session = Session()
    lessons = session.query(Lesson)
    lesson_list = []
    for lesson in lessons:
        lesson_list.append(lesson.as_dict())

    ret_obj['lessons'] = lesson_list
    return ret_obj


@app.route("/lessons123/<id>")
def get_lesson_by_id123(id):
    app.logger.info("Inside get_lesson_by_id %s\n", id)

    session = Session()
    lesson = session.query(Lesson).filter_by(id=id).first()

    app.logger.info("Found lesson:%s\n", str(lesson))
    if lesson == None:
        status = ("Lesson with id {id} not found\n").format(id=id)
        return Response(status, status=404)
    else: 
        return lesson.as_dict()


@app.route("/lessons/<id>")
def get_lesson_by_id(id):
    app.logger.info("Inside get_lesson_by_id %s\n", id)

    session = Session()
    lesson = session.get(Lesson, id)

    app.logger.info("Found lesson:%s\n", str(lesson))
    if lesson == None:
        status = ("Lesson with id {id} not found\n").format(id=id)
        return Response(status, status=404)
    else: 
        return lesson.as_dict()


@app.route("/lessons/<id>", methods=['PUT'])
def update_lesson_by_id(id):
    app.logger.info("Inside update_lesson_by_id %s\n", id)

    input_lesson = request.json
    app.logger.info("Received request:%s", str(input_lesson))

    session = Session()
    lesson = session.query(Lesson).filter_by(id=id).first()

    app.logger.info("Found lesson:%s\n", str(lesson))
    if lesson == None:
        status = ("Lesson with id {id} not found.\n").format(id=id)
        return Response(status, status=404)
    else:
        lesson.name = input_lesson['name']
        lesson.instrument = input_lesson['instrument']
        lesson.timings = input_lesson['timings']
        lesson.demo_url = input_lesson['demo_url']
        lesson.days = input_lesson['days']
        session.commit()
        status = ("Lesson with id {id} updated.\n").format(id=id)
        return Response(status, status=200)


@app.route("/lessons/<id>", methods=['DELETE'])
def delete_lesson_by_id(id):
    app.logger.info("Inside delete_lesson_by_id %s\n", id)

    session = Session()
    lesson = session.query(Lesson).filter_by(id=id).first()

    app.logger.info("Found lesson:%s\n", str(lesson))
    if lesson == None:
        status = ("Lesson with id {id} not found.\n").format(id=id)
        return Response(status, status=404)
    else:
        session.delete(lesson)
        session.commit()
        status = ("Lesson with id {id} deleted.\n").format(id=id)
        return Response(status, status=200)

def filter_lessons(data_to_search=''):
    data = {}
    if data_to_search == '':
        data['all'] = 'all'
    if 'instrument' in data_to_search and 'days' in data_to_search:
        data['instrument'] = data_to_search['instrument']
        data['days'] = data_to_search['days']
    if 'instrument' in data_to_search:
        data['instrument'] = data_to_search['instrument']
    if 'days' in data_to_search:
        data['days'] = data_to_search['days']
    return data


@app.route("/lessons1")
def getLessons1():
    if ('instrument' in request.args and 'days' in request.args) or ('instrument' in request.args) or ('days' in request.args):
        return filter_lessons(data_to_search=request.args)
    else:
        return filter_lessons()


## TODO: Add methods for person resource and signup resource

# 1. Register Person
@app.route("/persons", methods=['POST'])
def register_person():
    app.logger.info("Inside register_lesson")
    data = request.json
    app.logger.info("Received request:%s", str(data))

    name = data['name']
    role = data['role']

    #add check for invalid person name
    if (role != "teacher") and (role != "learner"):
        status = ("Invalid role {role}\n").format(role=role)
        return Response(status, status=400)
    else:
        person = Person(name=name,
                    role=role)

        session = Session()
        session.add(person)
        session.commit()

        return person.as_dict()


# 2. Get all persons
@app.route("/persons")
def get_persons():
    app.logger.info("Inside get_persons")
    ret_obj = {}

    session = Session()
    persons = session.query(Person)
    person_list = []

    if ('role' in request.args):
        role = request.args["role"]
        if role != "teacher" and role != "learner":
            status = ("role can be teacher or learner\n").format()
            return Response(status, status=400)
        for person in persons:
            person = person.as_dict()
            if person['role'] == role:
                person_list.append(person)
    else:
        for person in persons:
            person_list.append(person.as_dict())

    ret_obj['persons'] = person_list
    return ret_obj


# 3. Get a person
@app.route("/persons/<id>")
def get_person_by_id(id):
    app.logger.info("Inside get_person_by_id %s\n", id)

    session = Session()
    person = session.get(Person, id)

    if person == None:
        status = ("Person with id {id} not found\n").format(id=id)
        return Response(status, status=404)
    else: 
        app.logger.info("Found person:%s\n", str(person))
        return person.as_dict()



# 5. Signup for a lesson
@app.route("/signups", methods=['POST'])
def signup_lesson():
    app.logger.info("Inside signup_lesson")
    data = request.json
    app.logger.info("Received request:%s", str(data))

    lessonId = data['lessonId']
    personId = data['personId']
    session = Session()

    lesson = session.query(Lesson.id).filter_by(id=lessonId).first() is None
    person = session.query(Person.id).filter_by(id=personId).first() is None
 
    # need to check if id's exist
    if (lesson and person):
        status = ("Lesson with id {lessonId} and Person with id {personId} do not exist\n").format(lessonId=lessonId, personId=personId)
        return Response(status, status=400)
    if (lesson):
        status = ("Lesson with id {id} does not exist\n").format(id=lessonId)
        return Response(status, status=400)
    if (person):
        status = ("Person with id {id} does not exist\n").format(id=personId)
        return Response(status, status=400)

    signup = Signup(lessonId=lessonId, personId=personId)

    session.add(signup)
    session.commit()

    return signup.as_dict()

# 6. Get all signups
@app.route("/signups")
def get_signups():
    app.logger.info("Inside get_signups")
    ret_obj = {}

    session = Session()
    signups = session.query(Signup)
    signup_list = []
    
    for signup in signups:
        #Get signup information
        signup = signup.as_dict()
        lessonId = signup["lessonId"]
        personId = signup["personId"]
        

        # query Lesson db to get lesson name
        l_name = session.get(Lesson, lessonId)
        l_name = l_name.as_dict()
        p_name = session.get(Person, personId)
        p_name = p_name.as_dict()

        #add names to signup map
        s_map = {}
        s_map["lesson"] = l_name["name"]
        s_map["person"] = p_name["name"]
        signup_list.append(s_map)
    
    
    ret_obj["signups"] = signup_list
    return ret_obj


# 7. Delete a person
@app.route("/persons/<id>", methods=['DELETE'])
def delete_person_by_id(id):
    app.logger.info("Inside delete_person_by_id %s\n", id)

    session = Session()
    person = session.query(Person).filter_by(id=id).first()

    app.logger.info("Found person:%s\n", str(person))
    if person == None:
        status = ("Person with id {id} not found.\n").format(id=id)
        return Response(status, status=404)
    else:
        session.delete(person)
        # delete corresponding signup for person
        signups = session.query(Signup)
        for signup in signups:
            map = signups.as_dict()
            if map['personId'] == id:
                session.delete(signup)
        
        session.commit()
        status = ("Person with id {id} deleted successfully.\n").format(id=id)
        return Response(status, status=200)


@app.route("/cors")
def test_cors():

    d = Headers()
    d.add('Content-type', 'text/html')
    d.add('Access-Control-Allow-Origin',"*")

    resp = "cors_test"

    r = Response(resp, status=200, headers=d)
    return r


@app.route("/login", methods=['POST'])
def login123():
    app.logger.info("Inside login")
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(BASE_DIR, "templates/musicmarketplace.html")

    fp = open(template_path,"r")
    contents = fp.read()
    t = Template(contents)

    d = Headers()
    d.add('Content-type', 'text/html')
    d.add('Set-Cookie','friend=true')

    rendered_content = t.render(lessons=lessons)

    r = Response(rendered_content, status=200, headers=d)
    app.logger.info(r)

    #return t.render(lessons=lessons)
    return r


@app.route("/")
def index():
    app.logger.info("Inside index")
    return render_template('index.html')


if __name__ == "__main__":

    app.debug = True
    app.logger.info('Portal started...')
    app.run(host='0.0.0.0', port=5003) 
