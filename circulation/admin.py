from django.contrib import admin
from .models import Book, BookCopy, Member, Loan, Reservation, Penalty, UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type', 'created_at')
    list_filter = ('user_type',)
    search_fields = ('user__username',)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'isbn', 'category')
    search_fields = ('title', 'author', 'isbn')

@admin.register(BookCopy)
class BookCopyAdmin(admin.ModelAdmin):
    list_display = ('book', 'barcode', 'status')
    list_filter = ('status',)

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'library_id', 'max_active_loans')
    search_fields = ('user__username', 'library_id')

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('copy', 'member', 'loan_date', 'due_date', 'status')
    list_filter = ('status', 'loan_date', 'due_date')

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('book', 'member', 'reserved_at', 'expires_at', 'status')
    list_filter = ('status',)

@admin.register(Penalty)
class PenaltyAdmin(admin.ModelAdmin):
    list_display = ('member', 'amount', 'reason', 'resolved')
    list_filter = ('resolved',)
