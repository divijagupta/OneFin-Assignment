from django.contrib.auth.models import User
from django.contrib.auth.models import update_last_login
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

from credyapp.models import Movies, Collection

JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER


class MoviesSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField()

    class Meta:
        model = Movies
        fields = ('uuid', 'title', 'description', 'genres')


class CollectionSerializer(serializers.ModelSerializer):
    movies = MoviesSerializer(many=True)

    class Meta:
        model = Collection
        fields = ('title', 'description', 'movies')

    def validate(self, data):
        if Collection.objects.filter(user=self.context.get("user"), title=data.get("title")).first():
            raise serializers.ValidationError("A collection with that title already exists")
        return data

    def create(self, validated_data):
        collection = Collection(user=self.context.get("user"), title=validated_data.get("title"),
                                description=validated_data.get("description"))

        collection.save()

        movie_data = validated_data.get("movies")

        movie_data = [dict(t) for t in {tuple(d.items()) for d in movie_data}]

        for item in movie_data:
            try:
                movie = Movies.objects.get(uuid=item["uuid"])
            except Movies.DoesNotExist:
                movie = Movies.objects.create(**item)
            collection.movies.add(movie)

        return collection


class UpdateCollectionSerializer(serializers.ModelSerializer):
    movies = MoviesSerializer(many=True, required=False)
    title = serializers.CharField(max_length=20, required=False)
    description = serializers.CharField(max_length=500, required=False)

    class Meta:
        model = Collection
        fields = ('title', 'description', 'movies')

    def validate(self, data):
        if Collection.objects.filter(user=self.context.get("user"), title=data.get("title")).first():
            raise serializers.ValidationError("A collection with that title already exists")
        return data

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)

        instance.save()

        if 'movies' in validated_data.keys():
            instance.movies.clear()

            movie_data = validated_data.get("movies")

            movie_data = [dict(t) for t in {tuple(d.items()) for d in movie_data}]

            for item in movie_data:
                try:
                    movie = Movies.objects.get(uuid=item["uuid"])
                except Movies.DoesNotExist:
                    movie = Movies.objects.create(**item)
                instance.movies.add(movie)

        return instance


class GetAllCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ('title', 'uuid', 'description')


class GetCollectionSerializer(serializers.ModelSerializer):
    movies = MoviesSerializer(many=True)

    class Meta:
        model = Collection
        fields = ('title', 'uuid', 'description', 'movies')


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=50, min_length=3, trim_whitespace=True)
    password = serializers.CharField(max_length=100, min_length=8, write_only=True,
                                     trim_whitespace=True)
    confirm_password = serializers.CharField(max_length=100, write_only=True, min_length=8, trim_whitespace=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate_username(self, username):
        existing = User.objects.filter(username=username).first()
        if existing:
            raise serializers.ValidationError("Someone with that username already exists")
        return username

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError("Both passwords don't match")
        return data

    def create(self, validated_data):
        user = User.objects.create_user(username=self.validated_data["username"],
                                        password=self.validated_data["password"])

        payload = JWT_PAYLOAD_HANDLER(user)
        jwt_token = JWT_ENCODE_HANDLER(payload)
        update_last_login(None, user)

        return {
            'token': jwt_token
        }
