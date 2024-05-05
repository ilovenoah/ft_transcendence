import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question

# Create your tests here.

class QuestionModelTests(TestCase):
	def test_was_published_recently_with_future_question(self):
		"""
		was_published_recently() returns False for question whose
		pub_date is in the future.
		"""
		time = timezone.now() + datetime.timedelta(days=30)
		future_question = Question(pub_date=time)
		self.assertIs(future_question.was_published_recently(), False)

	def test_was_published_recently_with_old_question(self):
		"""
		was_published_recently() return False for questions whose
		pub_date is older than 1 day.
		"""
		time = timezone.now() - datetime.timedelta(days=1, seconds=1)
		old_question = Question(pub_date=time)
		self.assertIs(old_question.was_published_recently(), False)
	
	def test_was_published_recently_with_recent_question(self):
		"""
		was_published_recently() returns True for questions whose
		pub_date is within the last day.
		"""
		time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
		recent_question = Question(pub_date=time)
		self.assertIs(recent_question.was_published_recently(), True)

def create_question(question_text, days):
	"""
	Create a question with the given question_text and publish the given
	number of days offset to now (negative fro questions published in the
	past, positive for questions that have yet to be published).
	"""
	time = timezone.now() + datetime.timedelta(days=days)
	return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):
	def test_no_questions(self):
		"""
		If no questions exist, an appropriate message is displayed.
		"""
		response = self.client.get(reverse("polls:index"))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "No polls are available.")
		self.assertQuerySetEqual(response.context["latest_question_list"], [])
	
	def test_past_question(self):
		"""
		Questions with a pub_date in the pas are displayed on the 
		index page.
		"""
		question = create_question(question_text="Past question.", days=-30)
		response = self.client.get(reverse("polls:index"))
		self.assertQuerySetEqual(
			response.context["latest_question_list"],
			[question],
		)
	
	def test_future_question(self):
		"""
		Questions with a pub_date in the future aren't displayed on
		the index page.
		"""
		create_question(question_text="Future question.", days=30)
		response = self.client.get(reverse("polls:index"))
		self.assertContains(response, "No polls are available.")
		self.assertQuerySetEqual(response.context["latest_question_list"], [])
	
	def test_future_question_and_past_question(self):
		"""
		Event if both psat and future questions exist, only past 
		questions are displayed.
		"""
		question = create_question(question_text="Past question.", days=-30)
		create_question(question_text="Future question.", days=30)
		response = self.client.get(reverse("polls:index"))
		self.assertQuerySetEqual(
			response.context["latest_question_list"],
			[question],
		)
	
	def test_two_past_questions(self):
		"""
		The questions index page may display multiple quesitons.
		"""
		question1 = create_question(question_text="Past question 1.", days=-30)
		question2 = create_question(question_text="Past question2.", days=-5)
		response = self.client.get(reverse("polls:index"))
		self.assertQuerySetEqual(
			response.context["latest_question_list"],
			[question2, question1],
		)

