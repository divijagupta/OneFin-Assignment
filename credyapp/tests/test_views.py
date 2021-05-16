from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework_jwt.settings import api_settings

from credyapp.models import Collection, Movies

JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER


class ViewTest(TestCase):

    def setUp(self):
        user_data = {"username": 'test_user_1', "password": "test_password_1"}
        user = User.objects.create_user(username=user_data["username"],
                                        password=user_data["password"])
        payload = JWT_PAYLOAD_HANDLER(user)
        self.access_token = JWT_ENCODE_HANDLER(payload)
        movies_data = [
            {
                "title": "The Morning After",
                "description": "The Morning After is a feature film that consists of 8 vignettes that are inter-cut "
                               "throughout the film. The 8 vignettes are about when you wake up next to someone the "
                               "next "
                               "morning...",
                "genres": "Comedy,Drama",
                "uuid": "9a4fcb67-24f6-4cda-8f49-ad66b689f481"
            },
            {
                "title": "Maa",
                "description": "The bliss of a biology teacher’s family life in Delhi is shattered when her daughter, "
                               "Arya  is physically assaulted by Jagan and gang. Does Devki Sabarwal wait for the law "
                               "to take its course? Or does Devki become Maa Durga and hunt down the perpetrators of "
                               "the crime?",
                "genres": "Crime,Drama,Thriller",
                "uuid": "587a1f5b-d36a-41a3-8bf8-ea0788ebc752"
            }
        ]
        collection_obj = Collection.objects.create(title="test_title", description="test_description", user=user)
        self.collection_uuid = collection_obj.uuid
        for movie in movies_data:
            movie_obj = Movies.objects.create(**movie)
            collection_obj.movies.add(movie_obj)

    def test_user_registration_view(self):
        data = {"username": 'test_user', "password": "test_password", "confirm_password": "test_password"}
        resp = self.client.post(reverse("credyapp:register"), data)
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(resp.json().get('access_token'))

    def test_movies(self):
        resp = self.client.get(reverse("credyapp:list_movies"), HTTP_AUTHORIZATION="Bearer " + self.access_token)
        self.assertEqual(resp.status_code, 200)

    def test_get_all_collections(self):
        resp = self.client.get(reverse("credyapp:get_all_create_collection"),
                               HTTP_AUTHORIZATION="Bearer " + self.access_token)
        self.assertEqual(resp.status_code, 200)

    def test_create_collection(self):
        data = {
            "title": "Test collection",
            "description": "New collection",
            "movies": [
                {
                    "title": "The Morning After",
                    "description": "The Morning After is a feature film that consists of 8 vignettes that are "
                                   "inter-cut throughout the film. The 8 vignettes are about when you wake up next to "
                                   "someone the next morning...",
                    "genres": "Comedy,Drama",
                    "uuid": "9a4fcb67-24f6-4cda-8f49-ad66b689f481"
                },
                {
                    "title": "Maa",
                    "description": "The bliss of a biology teacher’s family life in Delhi is shattered when her "
                                   "daughter, Arya  is physically assaulted by Jagan and gang. Does Devki Sabarwal "
                                   "wait for the law to take its course? Or does Devki become Maa Durga and hunt down "
                                   "the perpetrators of the crime?",
                    "genres": "Crime,Drama,Thriller",
                    "uuid": "587a1f5b-d36a-41a3-8bf8-ea0788ebc752"
                }
            ]
        }
        resp = self.client.post(reverse("credyapp:get_all_create_collection"), data,
                                HTTP_AUTHORIZATION="Bearer " + self.access_token, content_type="application/json")
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(resp.json().get('collection_uuid'))
        self.collection_uuid = resp.json().get('collection_uuid')

    def test_get_collection(self):
        resp = self.client.get(reverse("credyapp:get_put_delete_collection", kwargs={"uuid": self.collection_uuid}),
                               HTTP_AUTHORIZATION="Bearer " + self.access_token)
        self.assertEqual(resp.status_code, 200)

    def test_put_collection(self):
        resp = self.client.put(reverse("credyapp:get_put_delete_collection", kwargs={"uuid": self.collection_uuid}),
                               HTTP_AUTHORIZATION="Bearer " + self.access_token)
        self.assertEqual(resp.status_code, 200)

    def test_delete_collection(self):
        resp = self.client.delete(reverse("credyapp:get_put_delete_collection", kwargs={"uuid": self.collection_uuid}),
                                  HTTP_AUTHORIZATION="Bearer " + self.access_token)
        self.assertEqual(resp.status_code, 200)
