from django.http import JsonResponse

from django.views.decorators.csrf import csrf_exempt

# Health check endpoint
@csrf_exempt
def health_check(request):
    return JsonResponse({'status': 'ok', 'message': 'Server is running'}, status=200)
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.views import View
from .models import Book, BookCopy, Member, Loan, Reservation, Penalty, UserProfile
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
import json
import uuid
import traceback
from django.db.models import Q

@method_decorator(csrf_exempt, name='dispatch')
class BookListCreateView(View):
    def get(self, request):
        books = Book.objects.all()
        books_data = []
        for book in books:
            book_dict = {
                'id': book.id,
                'title': book.title,
                'author': book.author,
                'isbn': book.isbn,
                'category': book.category,
                'isbn': book.isbn,
                'category': book.category,
                'about': book.about,
                'cover_image': book.cover_image.url if book.cover_image else None,
                'created_at': book.created_at,
                'updated_at': book.updated_at,
            }
            books_data.append(book_dict)
        return JsonResponse(books_data, safe=False)

    def post(self, request):
        try:
            # Handle multipart form data for image upload
            if request.content_type.startswith('multipart/form-data'):
                title = request.POST.get('title')
                author = request.POST.get('author')
                isbn = request.POST.get('isbn')
                category = request.POST.get('category')
                about = request.POST.get('about')
                cover_image = request.FILES.get('cover_image')
                
                book = Book.objects.create(
                    title=title,
                    author=author,
                    isbn=isbn,
                    category=category,
                    about=about,
                    cover_image=cover_image
                )
            else:
                # Handle JSON data (backward compatibility)
                data = json.loads(request.body)
                book = Book.objects.create(
                    title=data['title'],
                    author=data['author'],
                    isbn=data['isbn'],
                    category=data['category'],
                    about=data.get('about')
                )
            
            return JsonResponse({
                'id': book.id,
                'title': book.title,
                'cover_image': book.cover_image.url if book.cover_image else None,
                'message': 'Book created successfully'
            }, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def signup(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            email = data.get('email', '')

            if User.objects.filter(username=username).exists():
                return JsonResponse({'error': 'Username already exists'}, status=400)

            user = User.objects.create_user(username=username, password=password, email=email)
            
            # Always create as MEMBER - librarians must be created via admin panel
            UserProfile.objects.create(user=user, user_type='MEMBER')
            
            # Auto-generate Library ID
            library_id = f"LIB-{uuid.uuid4().hex[:8].upper()}"
            Member.objects.create(user=user, library_id=library_id)
            
            return JsonResponse({
                'message': 'User created successfully',
                'id': user.id,
                'library_id': library_id
            }, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def signin(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                
                # Get user profile to determine user type
                try:
                    profile = UserProfile.objects.get(user=user)
                    user_type = profile.user_type
                except UserProfile.DoesNotExist:
                    # If no profile exists, create one with MEMBER type (for existing users)
                    profile = UserProfile.objects.create(user=user, user_type='MEMBER')
                    user_type = 'MEMBER'
                
                return JsonResponse({
                    'message': 'Login successful',
                    'user_id': user.id,
                    'username': user.username,
                    'user_type': user_type
                }, status=200)
            else:
                return JsonResponse({'error': 'Invalid credentials'}, status=401)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@method_decorator(csrf_exempt, name='dispatch')
class BookCopyListCreateView(View):
    def get(self, request, book_id):
        try:
            if not Book.objects.filter(id=book_id).exists():
                return JsonResponse({'error': 'Book not found'}, status=404)
            copies = list(BookCopy.objects.filter(book_id=book_id).values())
            return JsonResponse(copies, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    def post(self, request, book_id):
        try:
            if not Book.objects.filter(id=book_id).exists():
                return JsonResponse({'error': 'Book not found'}, status=404)
            
            data = json.loads(request.body)
            count = int(data.get('count', 1))
            
            created_copies = []
            for _ in range(count):
                # Auto-generate internal barcode
                internal_barcode = f"COPY-{uuid.uuid4().hex[:8].upper()}"
                
                copy = BookCopy.objects.create(
                    book_id=book_id,
                    barcode=internal_barcode
                )
                created_copies.append(copy.barcode)
            
            return JsonResponse({
                'message': f'{count} copies created successfully',
                'count': count,
                'barcodes': created_copies
            }, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class MemberView(View):
    def get(self, request):
        members = list(Member.objects.values('id', 'user__username', 'library_id', 'max_active_loans'))
        return JsonResponse(members, safe=False)

    def post(self, request):
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            library_id = data.get('library_id')
            
            if not User.objects.filter(id=user_id).exists():
                return JsonResponse({'error': 'User not found'}, status=404)
                
            member = Member.objects.create(
                user_id=user_id,
                library_id=library_id
            )
            return JsonResponse({
                'id': member.id,
                'user': member.user.username,
                'library_id': member.library_id,
                'message': 'Member profile created successfully'
            }, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class LoanCreateView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            book_id = data.get('book_id')
            library_id = data.get('library_id')
            
            member = Member.objects.filter(library_id=library_id).first()
            if not member:
                return JsonResponse({'error': 'Member not found'}, status=404)

            # Find an available copy of the book
            copy = BookCopy.objects.filter(book_id=book_id, status='AVAILABLE').first()
            if not copy:
                return JsonResponse({'error': 'No available copies of this book'}, status=400)
            
            if Loan.objects.filter(member=member, status='ACTIVE').count() >= member.max_active_loans:
                return JsonResponse({'error': 'Member has reached maximum active loans'}, status=400)
            
            due_date = timezone.now() + timezone.timedelta(days=14)
            loan = Loan.objects.create(
                copy=copy,
                member=member,
                due_date=due_date
            )
            copy.status = 'ON_LOAN'
            copy.save()
            
            # Check if this member has a pending reservation for this book and fulfill it
            pending_reservation = Reservation.objects.filter(
                book_id=book_id,
                member=member,
                status='PENDING'
            ).first()
            
            if pending_reservation:
                pending_reservation.status = 'FULFILLED'
                pending_reservation.save()
            
            return JsonResponse({
                'message': 'Book checked out successfully',
                'loan_id': loan.id,
                'due_date': loan.due_date,
                'reservation_fulfilled': pending_reservation is not None
            }, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class LoanReturnView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            book_id = data.get('book_id')
            library_id = data.get('library_id')
            
            member = Member.objects.filter(library_id=library_id).first()
            if not member:
                return JsonResponse({'error': 'Member not found'}, status=404)

            # Find active loan for this book and member
            loan = Loan.objects.filter(copy__book_id=book_id, member=member, status='ACTIVE').first()
            if not loan:
                return JsonResponse({'error': 'No active loan found for this book and member'}, status=404)
            
            copy = loan.copy
            
            loan.return_date = timezone.now()
            loan.status = 'RETURNED'
            loan.save()
            
            copy.status = 'AVAILABLE'
            copy.save()
            
            penalty_data = None
            if loan.return_date > loan.due_date:
                overdue_delta = loan.return_date - loan.due_date
                overdue_days = overdue_delta.days + 1 # Charge for partial days
                amount = overdue_days * 100.00 # 100 rupees per day
                
                penalty = Penalty.objects.create(
                    member=loan.member,
                    loan=loan,
                    amount=amount,
                    reason=f"Overdue by {overdue_days} days"
                )
                penalty_data = {
                    'penalty_id': penalty.id,
                    'amount': str(penalty.amount),
                    'reason': penalty.reason
                }
            
            response_data = {
                'message': 'Book returned successfully',
                'loan_id': loan.id
            }
            if penalty_data:
                response_data['penalty'] = penalty_data
                response_data['message'] = 'Book returned with penalty'
                
            return JsonResponse(response_data, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class ReservationView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            book_id = data.get('book_id')
            library_id = data.get('library_id')
            
            book = Book.objects.filter(id=book_id).first()
            member = Member.objects.filter(library_id=library_id).first()
            
            if not book:
                return JsonResponse({'error': 'Book not found'}, status=404)
            if not member:
                return JsonResponse({'error': 'Member not found'}, status=404)
                
            # Check if member already has a pending reservation for this book
            if Reservation.objects.filter(book=book, member=member, status='PENDING').exists():
                return JsonResponse({'error': 'Member already has a pending reservation for this book'}, status=400)

            # Check availability
            total_copies = BookCopy.objects.filter(book=book).count()
            active_loans = Loan.objects.filter(copy__book=book, status='ACTIVE').count()
            active_reservations = Reservation.objects.filter(book=book, status='PENDING').count()
            
            if active_loans + active_reservations >= total_copies:
                 return JsonResponse({'error': 'No copies available for reservation'}, status=400)

            expires_at = timezone.now() + timezone.timedelta(days=7)
            reservation = Reservation.objects.create(
                book=book,
                member=member,
                expires_at=expires_at
            )
            
            return JsonResponse({
                'message': 'Book reserved successfully',
                'reservation_id': reservation.id,
                'expires_at': reservation.expires_at
            }, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)




@method_decorator(csrf_exempt, name='dispatch')
class LoanListView(View):
    def get(self, request):
        member_id = request.GET.get('member_id')
        
        loans_query = Loan.objects.all().select_related('copy__book')
        if member_id:
            loans_query = loans_query.filter(member_id=member_id)
            
        loans_data = []
        for loan in loans_query:
            loans_data.append({
                'id': loan.id,
                'copy__book__id': loan.copy.book.id,
                'copy__book__title': loan.copy.book.title,
                'copy__book__cover_image': loan.copy.book.cover_image.url if loan.copy.book.cover_image else None,
                'due_date': loan.due_date,
                'return_date': loan.return_date,
                'status': loan.status
            })
            
        return JsonResponse(loans_data, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
class ReservationListView(View):
    def get(self, request):
        # First, update any expired reservations
        now = timezone.now()
        Reservation.objects.filter(
            status='PENDING',
            expires_at__lt=now
        ).update(status='EXPIRED')
        
        member_id = request.GET.get('member_id')
        
        reservations_query = Reservation.objects.all().select_related('book', 'member')
        if member_id:
            reservations_query = reservations_query.filter(member_id=member_id)
            
        reservations_data = []
        for res in reservations_query:
            reservations_data.append({
                'id': res.id,
                'book__id': res.book.id,
                'book__title': res.book.title,
                'book__cover_image': res.book.cover_image.url if res.book.cover_image else None,
                'member__library_id': res.member.library_id,
                'reserved_at': res.reserved_at,
                'expires_at': res.expires_at,
                'status': res.status
            })
            
        return JsonResponse(reservations_data, safe=False)


@csrf_exempt
def cancel_reservation(request, reservation_id):
    if request.method == 'POST':
        try:
            reservation = Reservation.objects.get(id=reservation_id)
            
            if reservation.status != 'PENDING':
                return JsonResponse({
                    'error': f'Cannot cancel reservation with status {reservation.status}'
                }, status=400)
            
            reservation.status = 'CANCELLED'
            reservation.save()
            
            return JsonResponse({
                'message': 'Reservation cancelled successfully',
                'reservation_id': reservation.id
            }, status=200)
        except Reservation.DoesNotExist:
            return JsonResponse({'error': 'Reservation not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)
