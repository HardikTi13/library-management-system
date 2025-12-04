from django.urls import path
from .views import BookListCreateView, BookCopyListCreateView, MemberView, LoanCreateView, LoanReturnView, ReservationView, signup, signin, LoanListView, ReservationListView, cancel_reservation

urlpatterns = [
    path('books/', BookListCreateView.as_view(), name='book-list-create'),
    path('books/<int:book_id>/copies/', BookCopyListCreateView.as_view(), name='book-copy-list-create'),
    path('members/', MemberView.as_view(), name='member-list-create'),
    path('loans/', LoanListView.as_view(), name='loan-list'),
    path('loans/checkout/', LoanCreateView.as_view(), name='loan-checkout'),
    path('loans/return/', LoanReturnView.as_view(), name='loan-return'),
    path('reservations/', ReservationView.as_view(), name='reservation-create'),
    path('reservations/list/', ReservationListView.as_view(), name='reservation-list'),
    path('reservations/<int:reservation_id>/cancel/', cancel_reservation, name='reservation-cancel'),
    path('signup/', signup, name='signup'),
    path('signin/', signin, name='signin'),
]
