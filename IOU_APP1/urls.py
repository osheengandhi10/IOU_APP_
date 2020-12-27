from django.urls import include, path
from . import views
from .views import product_detail


urlpatterns = [
  
    path('users/',views.GetUser.as_view()),
    path('add/',views.CreateUSer.as_view()),
    path('iou/',views.CreateIOU.as_view()),
    path('iou/getsummary/<lender_id>/<borrower_id>/',views.product_detail.as_view())
]   