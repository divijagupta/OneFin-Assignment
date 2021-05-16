from django.urls import path

from credyapp import views

app_name = 'credyapp'

urlpatterns = [
    path('collection/<uuid:uuid>/', views.GetPutDeleteCollection.as_view(), name='get_put_delete_collection'),
    path('movies/', views.ListMovies.as_view(), name='list_movies'),
    path('collection/', views.GetAllCreateCollection.as_view(), name='get_all_create_collection'),
    path('register/', views.Register.as_view(), name='register'),
    path('request-count/', views.RequestCount.as_view(), name='request_count'),
    path('request-count/reset/', views.ResetRequestCount.as_view(), name='request_count_reset')
]
