from django.urls import path

from . import views

urlpatterns = [
    # ex: /polls/
    path("", views.index, name="index"),
    path("second/", views.second, name="second"),
    path("third/", views.third, name="third"),
]
        