# Create your views here.
import os
from json import JSONDecodeError

import requests
from django.db.models import Count
from django.http import Http404
from requests.auth import HTTPBasicAuth
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from credyapp.models import Collection, Movies, RequestCounter
from credyapp.serializers import RegisterSerializer, CollectionSerializer, GetAllCollectionSerializer, \
    GetCollectionSerializer, UpdateCollectionSerializer
from django.conf import settings


class GetPutDeleteCollection(APIView):
    def get_object(self, uuid, user):
        try:
            return Collection.objects.get(uuid=uuid, user=user)
        except Collection.DoesNotExist:
            raise Http404

    def get(self, request, uuid):
        collection = self.get_object(uuid, request.user)
        return Response(GetCollectionSerializer(collection).data, status=status.HTTP_200_OK)

    def put(self, request, uuid):
        collection = self.get_object(uuid, request.user)
        serializer = UpdateCollectionSerializer(collection, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Collection details updated"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, uuid):
        collection = self.get_object(uuid, request.user)
        collection.delete()
        return Response({"message": "Collection deleted"}, status=status.HTTP_200_OK)


class GetAllCreateCollection(APIView):
    def get(self, request):
        movie_set = set()
        queryset = Collection.objects.filter(user=request.user).prefetch_related('movies')

        for collection in queryset:
            movie_set.update(list(collection.movies.values_list('uuid', flat=True)))

        fav_genres = list(
            Movies.objects.filter(uuid__in=movie_set).values('genres').annotate(genre_count=Count('genres')).order_by(
                '-genre_count').values_list('genres', flat=True))

        if len(fav_genres) > 3:
            fav_genres = fav_genres[0:3]

        serializer = GetAllCollectionSerializer(queryset, many=True)

        response = {"is_success": True,
                    "data": {"collections": serializer.data, "favourite_genres": ";".join(fav_genres)}}

        return Response(response, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CollectionSerializer(data=request.data, context={"user": request.user})
        if serializer.is_valid():
            collection = serializer.save()
            return Response({"collection_uuid": collection.uuid}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def api_request(page):
    api_response = requests.get(settings.CREDY_URL, params={"page": page},
                                auth=HTTPBasicAuth(os.environ.get("CREDY_USERNAME"), os.environ.get("CREDY_PASSWORD")),
                                timeout=3)
    return api_response


class ListMovies(APIView):
    def get(self, request):
        page = request.query_params.get("page", 1)
        counter = 10
        api_response = api_request(page)
        while counter != 0:
            if api_response.status_code not in [500, 502, 504, 503, 429]:
                break
            api_response = api_request(page)
            counter -= 1

        try:
            response_data = api_response.json()
        except JSONDecodeError:
            response_data = api_response.content

        return Response({"message": response_data})


class Register(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        if self.request.user.is_authenticated:
            return Response({"message": "You're already logged in!"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.save()
            return Response({"access_token": data.get("token")}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RequestCount(APIView):
    def get(self, request):
        obj = RequestCounter.objects.last()
        return Response({"requests": obj.counter}, status=status.HTTP_200_OK)


class ResetRequestCount(APIView):
    def post(self, request):
        obj = RequestCounter.objects.last()
        obj.counter = 0
        obj.save()
        return Response({"message": "Request count reset successfully"}, status=status.HTTP_200_OK)
