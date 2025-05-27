from django import forms
from django.db.models.aggregates import Sum
from django.utils.html import format_html
from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from .models import (
	Dealer, Car, CarLocation, TripTracking, Rental, Transaction, CarReview, Fine, CarPhoto
)


class RentalForm(forms.ModelForm):
	class Meta:
		model = Rental
		fields = "__all__"
		widgets = {
			"start_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
			"end_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
		}


@admin.register(Rental)
class RentalAdmin(GuardedModelAdmin):
	form = RentalForm

	list_display = [
		"id",
		"user",
		"car",
		"get_start_time",
		"get_end_time",
		"total_price",
		"is_paid",
		"status",
	]
	list_editable = ["is_paid", "status"]
	list_filter = ["is_paid", "status"]
	search_fields = ["user__username", "car__brand", "car__model"]
	autocomplete_fields = ["user", "car"]

	readonly_fields = ["total_price", "created_at", "updated_at"]
	ordering = ["-start_time"]
	date_hierarchy = "start_time"

	fieldsets = (
		("Основная информация", {
			"fields": ("user", "car", "start_time", "end_time"),
		}),
		("Статус и оплата", {
			"fields": ("status", "is_paid", "total_price"),
		}),
		("Системные поля", {
			"fields": ("created_at", "updated_at"),
		}),
	)

	actions = ["mark_as_paid", "mark_as_unpaid", "cancel_rentals"]

	def get_queryset(self, request):
		"""Отбираем связанные объекты, чтобы снизить число запросов."""
		return super().get_queryset(request) \
			.select_related("user", "car")

	@admin.display(description="Начало аренды")
	def get_start_time(self, obj):
		return obj.start_time.strftime("%Y-%m-%d %H:%M") if obj.start_time else "—"

	@admin.display(description="Окончание аренды")
	def get_end_time(self, obj):
		return obj.end_time.strftime("%Y-%m-%d %H:%M") if obj.end_time else "—"

	@admin.action(description="Отметить как оплаченные")
	def mark_as_paid(self, request, queryset):
		updated = queryset.update(is_paid=True)
		self.message_user(request, f"{updated} аренда(ы) отмечены как оплаченные.")

	@admin.action(description="Отметить как неоплаченные")
	def mark_as_unpaid(self, request, queryset):
		updated = queryset.update(is_paid=False)
		self.message_user(request, f"{updated} аренда(ы) отмечены как неоплаченные.")

	@admin.action(description="Отменить выбранные аренды")
	def cancel_rentals(self, request, queryset):
		# Предполагаем, что статус 'cancelled' присутствует среди choices
		updated = queryset.update(status="cancelled")
		self.message_user(request, f"{updated} аренда(ы) отменено.")

	def save_model(self, request, obj, form, change):
		"""
		Пересчитываем total_price перед сохранением,
		например исходя из разницы между start_time и end_time + тариф.
		"""
		# допустим, у модели есть метод compute_total()
		obj.total_price = obj.compute_total()
		super().save_model(request, obj, form, change)


class TransactionForm(forms.ModelForm):
	class Meta:
		model = Transaction
		fields = '__all__'


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
	form = TransactionForm
	list_display = ['user', 'amount', 'transaction_type', 'timestamp']  # Убрали 'status'
	list_filter = ['transaction_type']
	search_fields = ['user__username']
	readonly_fields = ['timestamp']  # 'created_at' нет в модели, но есть 'timestamp'


class ReviewForm(forms.ModelForm):
	class Meta:
		model = CarReview
		fields = '__all__'


@admin.register(CarReview)
class ReviewAdmin(admin.ModelAdmin):
	form = ReviewForm
	list_display = ['user', 'car', 'rating', 'created_at']
	list_filter = ['rating']
	search_fields = ['user__username', 'car__brand']
	readonly_fields = ['created_at']


class FineForm(forms.ModelForm):
	class Meta:
		model = Fine
		fields = '__all__'


@admin.register(Fine)
class FineAdmin(admin.ModelAdmin):
	form = FineForm
	list_display = ['user', 'rental', 'amount', 'reason', 'issued_at']  # Убрали 'car'
	search_fields = ['user__username', 'rental__car__brand']
	readonly_fields = ['issued_at']  # Убрали 'created_at'


class CarInline(admin.TabularInline):
	model = Car
	extra = 0
	fields = ('brand', 'model', 'year', 'price_per_day', 'is_available')
	readonly_fields = ()
	show_change_link = True


class DealerForm(forms.ModelForm):
	class Meta:
		model = Dealer
		widgets = {
			'name': forms.TextInput(attrs={'class': 'vTextField'}),
			'address': forms.Textarea(attrs={'rows': 2}),
		}
		fields = '__all__'


@admin.register(Dealer)
class DealerAdmin(GuardedModelAdmin):
	form = DealerForm
	inlines = [CarInline]

	list_display = (
		'name', 'address', 'is_active',
		'cars_count', 'total_revenue', 'created_at'
	)
	list_filter = ('is_active', 'created_at')
	search_fields = ('name', 'address')
	actions = ('activate_dealers', 'deactivate_dealers')

	def cars_count(self, obj):
		return obj.car_set.count()

	cars_count.short_description = "Машин"

	def total_revenue(self, obj):
		# Сумма по всем завершённым арендам у машин данного дилера
		rev = Rental.objects.filter(
			car__dealer=obj,
			status='completed'
		).aggregate(sum=Sum('total_price'))['sum'] or 0
		return f"{rev:,.2f} ₸"

	total_revenue.short_description = "Доход"

	@admin.action(description="Активировать выбранных дилеров")
	def activate_dealers(self, request, queryset):
		updated = queryset.update(is_active=True)
		self.message_user(request, f"{updated} дилер(ов) активировано.")

	@admin.action(description="Деактивировать выбранных дилеров")
	def deactivate_dealers(self, request, queryset):
		updated = queryset.update(is_active=False)
		self.message_user(request, f"{updated} дилер(ов) деактивировано.")


class CarForm(forms.ModelForm):
	class Meta:
		model = Car
		fields = '__all__'
		widgets = {
			'brand': forms.TextInput(attrs={'class': 'vTextField'}),
			'model': forms.TextInput(attrs={'class': 'vTextField'}),
			'year': forms.NumberInput(attrs={'min': 2000, 'max': 2030}),
			'price_per_day': forms.NumberInput(attrs={'step': 0.01}),
		}


class CarPhotoInline(admin.TabularInline):
	model = CarPhoto
	extra = 3
	fields = ("photo_preview", "image", "alt_text", "order")
	readonly_fields = ("photo_preview",)

	def photo_preview(self, obj):
		if obj.image:
			return format_html(
				'<img src="{}" style="max-height: 100px; max-width: 150px; object-fit:contain;"/>',
				obj.image.url
			)
		return "-"

	photo_preview.short_description = "Превью"


@admin.register(CarPhoto)
class CarPhotoAdmin(admin.ModelAdmin):
	list_display = ('id', 'alt_text', 'order', 'uploaded_at')
	list_filter = ('uploaded_at',)
	search_fields = ('alt_text',)
	readonly_fields = ('uploaded_at',)


@admin.register(Car)
class CarAdmin(GuardedModelAdmin):
	form = CarForm

	# Горизонтальный селект для ManyToMany-поля photos
	filter_horizontal = ("photos",)

	search_fields = ("brand", "model")
	list_display = ("brand", "model", "year", "dealer", "is_available", "price_per_day")
	list_filter = ("dealer", "is_available", "car_type", "year")
	list_editable = ("is_available", "price_per_day")
	autocomplete_fields = ("dealer",)
	actions = ("make_available", "make_unavailable", "cancel_future_rentals")

	@admin.action(description="Сделать выбранные машины доступными")
	def make_available(self, request, queryset):
		updated = queryset.update(is_available=True)
		self.message_user(request, f"{updated} машин(ы) стали доступными.")

	@admin.action(description="Сделать выбранные машины недоступными")
	def make_unavailable(self, request, queryset):
		updated = queryset.update(is_available=False)
		self.message_user(request, f"{updated} машин(ы) стали недоступными.")

	@admin.action(description="Отменить будущие аренды этих машин")
	def cancel_future_rentals(self, request, queryset):
		# Предполагается, что статус 'booked' означает предстоящую аренду
		count = Rental.objects.filter(
			car__in=queryset,
			status='booked'
		).update(status='cancelled')
		self.message_user(request, f"{count} будущих аренды отменено.")


class CarLocationForm(forms.ModelForm):
	class Meta:
		model = CarLocation
		fields = '__all__'


@admin.register(CarLocation)
class CarLocationAdmin(admin.ModelAdmin):
	form = CarLocationForm
	list_display = ['car', 'latitude', 'longitude', 'updated_at']
	search_fields = ['car__brand', 'car__model']
	readonly_fields = ['updated_at']


### 4. Форма для истории трекинга
class TripTrackingForm(forms.ModelForm):
	class Meta:
		model = TripTracking
		fields = '__all__'


@admin.register(TripTracking)
class TripTrackingAdmin(admin.ModelAdmin):
	form = TripTrackingForm
	list_display = ['rental', 'timestamp', 'latitude', 'longitude']
	search_fields = ['rental__id']
	readonly_fields = ['timestamp']
