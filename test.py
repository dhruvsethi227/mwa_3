from itertools import count
import unittest
import requests

class TestMusicMarketPlaceAPI(unittest.TestCase):

	# POST /persons

	# POSITIVE SCENARIOS

	# Create a person with learner role

	def test_insert_person_role_learner(self, personName="person1"):
		url = "http://localhost:5003/persons"
		person = {}
		person['name'] = personName
		person['role'] = 'learner'
		resp = requests.post(url, json=person)
		self.assertIsNotNone(resp.json())
		resp_json = resp.json()
		print(resp_json)
		personId = resp_json['id']
		self.assertEqual(resp.status_code, 200)
		self.assertIsNotNone(personId)
		return resp_json
	
	# Create a person with teacher role

	def test_insert_person_role_teacher(self):
		url = "http://localhost:5003/persons"
		person = {}
		person['name'] = 'person2'
		person['role'] = 'teacher'
		resp = requests.post(url, json=person)
		self.assertIsNotNone(resp.json())
		resp_json = resp.json()
		print(resp_json)
		personId = resp_json['id']
		self.assertEqual(resp.status_code, 200)
		self.assertIsNotNone(personId)
		assert resp_json["id"] != None
		assert resp_json["name"] == "person2"
		assert resp_json["role"] == "teacher"

	# NEGATIVE SCENARIOS

	# Create a person with invalid role

	def test_insert_person_invalid(self):
		url = "http://localhost:5003/persons"
		person = {}
		person['name'] = 'person2'
		person['role'] = 'xyzRole'
		resp = requests.post(url, json=person)
		self.assertEqual(resp.status_code, 400)
		self.assertEqual(resp.reason, "BAD REQUEST")

	def test_insert_person_invalid_errorMessage(self):
		url = "http://localhost:5003/persons"
		person = {}
		person['name'] = 'person2'
		person['role'] = 'xyzRole'
		resp = requests.post(url, json=person)
		self.assertEqual(resp.status_code, 400)
		self.assertEqual(resp.reason, "BAD REQUEST")
		self.assertTrue(str(resp.content).lower().__contains__("invalid role"))
		self.assertTrue(str(resp.content).lower().__contains__("xyzrole"))

	# GET /persons

	def test_get_persons(self):
		url = "http://localhost:5003/persons"
		resp = requests.get(url)
		self.assertEqual(resp.status_code, 200)
		resp_json = resp.json()
		assert len(resp_json["persons"]) > 0

	def test_get_person_with_role(self):
		self.test_insert_person_role_learner()
		role = "learner"
		url = "http://localhost:5003/persons?role="+role
		resp = requests.get(url)
		self.assertEqual(resp.status_code, 200)
		resp_json = resp.json()
		assert len(resp_json["persons"]) >= 1
		assert resp_json["persons"][0]["role"] == role

	def test_get_person_with_role_teacher(self):
		self.test_insert_person_role_teacher()
		role = "teacher"
		url = "http://localhost:5003/persons?role="+role
		resp = requests.get(url)
		self.assertEqual(resp.status_code, 200)
		resp_json = resp.json()
		assert len(resp_json["persons"]) >= 1
		assert resp_json["persons"][0]["role"] == role

	# # NEGATIVE SCENARIO

	# GET PERSONS WITH INVALID ROLE
	def test_get_person_with_invalid_role_errorMessage(self):
		url = "http://localhost:5003/persons?role=coach"
		resp = requests.get(url)
		self.assertEqual(resp.status_code, 400)
		self.assertTrue(str(resp.content).lower().__contains__("role"))
		self.assertTrue(str(resp.content).lower().__contains__("can"))
		self.assertTrue(str(resp.content).lower().__contains__("teacher"))
		self.assertTrue(str(resp.content).lower().__contains__("learner"))

	def test_get_person_with_invalid_role(self):
		url = "http://localhost:5003/persons?role=coach"
		resp = requests.get(url)
		self.assertEqual(resp.status_code, 400)

	# # GET /persons/<person-id>

	# POSITIVE SCENARIOS
	def test_get_a_person(self):
		created_resp_json = self.test_insert_person_role_learner()
		personId = created_resp_json['id']

		url = "http://localhost:5003/persons/" + str(personId)
		resp = requests.get(url)
		self.assertEqual(resp.status_code, 200)
		resp_json = resp.json()
		assert resp_json["id"] == personId
		assert resp_json["name"] == created_resp_json["name"]
		assert resp_json["role"] == created_resp_json["role"]

	# NEGATIVE SCENARIOS
	
	# Get person with invalid id
	def test_get_person_not_found(self, personId=10000):
		url = "http://localhost:5003/persons/" + str(personId)
		resp = requests.get(url)
		self.assertEqual(resp.status_code, 404)
		self.assertTrue(resp.reason.__contains__("NOT FOUND"))

	def test_get_person_not_found_errorMessage(self, personId=10000):
		url = "http://localhost:5003/persons/" + str(personId)
		resp = requests.get(url)
		self.assertEqual(resp.status_code, 404)
		self.assertTrue(resp.reason.__contains__("NOT FOUND"))
		self.assertTrue(str(resp.content).lower().__contains__(str(personId)))
		self.assertTrue(str(resp.content).lower().__contains__("not found"))

	# DELETE /persons/<person-id>

	def test_delete_person(self):
		resp_json = self.test_insert_person_role_learner()
		personId = resp_json['id']

		url = "http://localhost:5003/persons/" + str(personId)
		resp = requests.delete(url)
		self.assertEqual(resp.status_code, 200)
		self.test_get_person_not_found(personId=personId)

	def test_delete_person_not_found(self):
		url = "http://localhost:5003/persons/100000"
		resp = requests.delete(url)
		self.assertEqual(resp.status_code, 404)

	def test_delete_person_not_found_errorMessage(self):
		url = "http://localhost:5003/persons/100000"
		resp = requests.delete(url)
		self.assertEqual(resp.status_code, 404)
		self.assertTrue(str(resp.content).lower().__contains__("10000"))
		self.assertTrue(str(resp.content).lower().__contains__("not found"))

	# POST /signups

	# POSITIVE SCENARIOS

	# Post a signup with valid personId and lessonId

	def test_insert_signup(self):
		resp_json1 = self.test_insert_person_role_learner()
		personId = resp_json1['id']

		resp_json = self.test_insert_lesson()
		lessonId = resp_json['id']

		url = "http://localhost:5003/signups"
		signup = {}
		signup["personId"] = personId
		signup['lessonId'] = lessonId
		resp = requests.post(url, json=signup)
		self.assertEqual(resp.status_code, 200)
		self.assertIsNotNone(resp.json())
		resp_json = resp.json()
		self.assertIsNotNone(personId)
		assert resp_json["personId"] == personId
		assert resp_json["lessonId"] == lessonId

	# NEGATIVE SCENARIOS

	# Post a signup with valid personId and invalid lessonId
	def test_insert_signup_invalid_lesson(self):
		resp_json1 = self.test_insert_person_role_learner()
		personId = resp_json1['id']

		lessonId = 10290901

		url = "http://localhost:5003/signups"
		signup = {}
		signup["personId"] = personId
		signup['lessonId'] = lessonId
		resp = requests.post(url, json=signup)
		self.assertEqual(resp.status_code, 400)
		self.assertEqual(resp.reason, "BAD REQUEST")

	def test_insert_signup_invalid_lesson_errorMessage(self):
		resp_json1 = self.test_insert_person_role_learner()
		personId = resp_json1['id']

		lessonId = 10290901

		url = "http://localhost:5003/signups"
		signup = {}
		signup["personId"] = personId
		signup['lessonId'] = lessonId
		resp = requests.post(url, json=signup)
		self.assertEqual(resp.status_code, 400)
		self.assertEqual(resp.reason, "BAD REQUEST")
		self.assertTrue(str(resp.content).lower().__contains__(str(lessonId)))
		self.assertTrue(str(resp.content).lower().__contains__("not exist"))

	# Post a signup with invalid personId and valid lessonId
	def test_insert_signup_invalid_person(self):
		personId = 10290901

		resp_json = self.test_insert_lesson()
		lessonId = resp_json['id']

		url = "http://localhost:5003/signups"
		signup = {}
		signup["personId"] = personId
		signup['lessonId'] = lessonId
		resp = requests.post(url, json=signup)
		self.assertEqual(resp.status_code, 400)
		self.assertEqual(resp.reason, "BAD REQUEST")

	def test_insert_signup_invalid_person_errorMessage(self):
		personId = 10290901

		resp_json = self.test_insert_lesson()
		lessonId = resp_json['id']

		url = "http://localhost:5003/signups"
		signup = {}
		signup["personId"] = personId
		signup['lessonId'] = lessonId
		resp = requests.post(url, json=signup)
		self.assertEqual(resp.status_code, 400)
		self.assertEqual(resp.reason, "BAD REQUEST")
		self.assertTrue(str(resp.content).lower().__contains__(str(personId)))
		self.assertTrue(str(resp.content).lower().__contains__("not exist"))

	# Post a signup with invalid personId and invalid lessonId
	def test_insert_signup_invalid_person_and_lesson(self):
		personId = 10290901
		lessonId = 12908978

		url = "http://localhost:5003/signups"
		signup = {}
		signup["personId"] = personId
		signup['lessonId'] = lessonId
		resp = requests.post(url, json=signup)
		self.assertEqual(resp.status_code, 400)
		self.assertEqual(resp.reason, "BAD REQUEST")

	def test_insert_signup_invalid_person_and_lesson_errorMessage(self):
		personId = 10290901
		lessonId = 12908978

		url = "http://localhost:5003/signups"
		signup = {}
		signup["personId"] = personId
		signup['lessonId'] = lessonId
		resp = requests.post(url, json=signup)
		self.assertEqual(resp.status_code, 400)
		self.assertEqual(resp.reason, "BAD REQUEST")
		self.assertTrue(str(resp.content).lower().__contains__(str(personId)))
		self.assertTrue(str(resp.content).lower().__contains__(str(lessonId)))
		self.assertTrue(str(resp.content).lower().__contains__("not exist"))
	

	# GET /signups

	# POSITIVE SCENARIOS

	def test_get_signups(self):
		# Create a signup
		resp_json1 = self.test_insert_person_role_learner("person456")
		personId = resp_json1['id']

		resp_json = self.test_insert_lesson()
		lessonId = resp_json['id']

		url = "http://localhost:5003/signups"
		signup = {}
		signup["personId"] = personId
		signup['lessonId'] = lessonId
		resp = requests.post(url, json=signup)
		self.assertEqual(resp.status_code, 200)

		# Get Signups
		url = "http://localhost:5003/signups"
		resp = requests.get(url)
		self.assertEqual(resp.status_code, 200)
		resp_json = resp.json()
		signups = resp_json["signups"]
		self.assertIsNotNone(next((x for x in signups if x["person"] == "person456"), None))	
		self.assertIsNotNone(next((x for x in signups if x["lesson"] == "test1"), None))	

	# Deleting the person should also delete all the signup entries corresponding to that person.

	def test_delete_person_check_signup(self):
		# Create a signup
		resp_json1 = self.test_insert_person_role_learner("person123")
		personId = resp_json1['id']

		resp_json = self.test_insert_lesson()
		lessonId = resp_json['id']

		url = "http://localhost:5003/signups"
		signup = {}
		signup["personId"] = personId
		signup['lessonId'] = lessonId
		resp = requests.post(url, json=signup)
		self.assertEqual(resp.status_code, 200)
		self.assertIsNotNone(resp.json())
		resp_json = resp.json()
		self.assertIsNotNone(personId)
		assert resp_json["personId"] == personId
		assert resp_json["lessonId"] == lessonId

		# Check for a signup
		resp = requests.get(url)
		self.assertEqual(resp.status_code, 200)
		resp_json = resp.json()
		self.assertIsNotNone(next((x for x in resp_json["signups"] if x["person"] == "person123"), None))	

		# Delete a person
		url = "http://localhost:5003/persons/" + str(personId)
		resp = requests.delete(url)
		self.assertEqual(resp.status_code, 200)
		self.test_get_person_not_found(personId=personId)

		# Check for a signup
		url = "http://localhost:5003/signups"
		resp = requests.get(url)
		self.assertEqual(resp.status_code, 200)
		resp_json = resp.json()
		self.assertIsNone(next((x for x in resp_json["signups"] if x["person"] == "person123"), None))		

	def test_insert_lesson(self):
		url = "http://localhost:5003/lessons"
		lesson = {}
		lesson['name'] = 'test1'
		lesson['demo_url'] = 'demo'
		lesson['timings'] = 'timings'
		lesson['instrument'] = 'instrument'
		lesson['days'] = 'days'
		resp = requests.post(url, json=lesson)
		resp_json = resp.json()
		return resp_json

	# POST /lessons

	# def test_insert_lesson(self):
	# 	url = "http://localhost:5003/lessons"
	# 	lesson = {}
	# 	lesson['name'] = 'test1'
	# 	lesson['demo_url'] = 'demo'
	# 	lesson['timings'] = 'timings'
	# 	lesson['instrument'] = 'instrument'
	# 	lesson['days'] = 'days'
	# 	resp = requests.post(url, json=lesson)
	# 	self.assertIsNotNone(resp.json())
	# 	resp_json = resp.json()
	# 	print(resp_json)
	# 	lessonId = resp_json['id']
	# 	self.assertEqual(resp.status_code, 200)
	# 	self.assertIsNotNone(lessonId)
	# 	return resp_json

	# def test_get_lesson(self):
	# 	resp_json = self.test_insert_lesson()
	# 	lessonId = resp_json['id']

	# 	url = "http://localhost:5003/lessons/" + str(lessonId)
	# 	resp = requests.get(url)
	# 	self.assertEqual(resp.status_code, 200)

	# def test_delete_lesson(self):
	# 	resp_json = self.test_insert_lesson()
	# 	lessonId = resp_json['id']

	# 	url = "http://localhost:5003/lessons/" + str(lessonId)
	# 	resp = requests.delete(url)
	# 	self.assertEqual(resp.status_code, 200)

	# 	self.test_get_lesson_not_found(lessonId=lessonId)

	# def test_get_lesson_not_found(self, lessonId="lesson123"):
	# 	url = "http://localhost:5003/lessons/" + str(lessonId)
	# 	resp = requests.get(url)
	# 	self.assertEqual(resp.status_code, 404)

	# def test_update_lesson_not_found(self):
	# 	url = "http://localhost:5003/lessons/123000"
	# 	resp = requests.put(url, json={"name": "test1"})
	# 	self.assertEqual(resp.status_code, 404)

	# def test_delete_lesson_not_found(self):
	# 	url = "http://localhost:5003/lessons/12235567"
	# 	resp = requests.delete(url)
	# 	self.assertEqual(resp.status_code, 404)

	# def test_get_lessons(self):
	# 	url = "http://localhost:5003/lessons"
	# 	resp = requests.get(url)
	# 	print(resp)
	# 	self.assertEqual(resp.status_code, 200)


if __name__ == '__main__':
    unittest.main()