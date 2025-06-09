from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import JSONField
from django.urls import reverse
from django.utils.text import slugify
from django.utils.timezone import now

UserModel = get_user_model()


# 1. Дилерский центр (точка получения машины)
class Dealer(models.Model):
	name = models.CharField(max_length=100, verbose_name="Название")
	address = models.TextField(verbose_name="Адрес")
	latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Широта")
	longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Долгота")
	is_active = models.BooleanField(
		default=True,
		verbose_name="Активен",
		help_text="Снимите галочку, чтобы заблокировать дилера"
	)
	created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
	updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = "Дилер"
		verbose_name_plural = "Дилеры"


class CarPhoto(models.Model):
	"""
	Дополнительные фотографии машины для слайдера.
	"""
	image = models.ImageField(
		upload_to="cars/gallery/",
		verbose_name="Фото"
	)
	alt_text = models.CharField(
		max_length=200,
		blank=True,
		verbose_name="Alt‑текст"
	)
	order = models.PositiveSmallIntegerField(
		default=0,
		verbose_name="Порядок"
	)
	uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Загружено")

	class Meta:
		verbose_name = "Фото Машины"
		verbose_name_plural = "Фото Машин"
		ordering = ["order", "uploaded_at"]

	def __str__(self):
		return f"Фото [{self.order}]"


class Car(models.Model):
	class CarType(models.TextChoices):
		SEDAN = 'Sedan', 'Седан'
		SUV = 'SUV', 'Внедорожник'
		HATCHBACK = 'Hatchback', 'Хэтчбек'
		CABRIOLET = 'Cabriolet', 'Кабриолет'
		COUPE = 'Coupe', 'Купе'
		MINIVAN = 'Minivan', 'Минивэн'
		PICKUP = 'Pickup', 'Пикап'

	class TransmissionTypes(models.TextChoices):
		MANUAL = 'Manual', 'Механика'
		AUTOMATIC = 'Automatic', 'Автоматическая'

	class FuelTypes(models.TextChoices):
		PB95 = "PB95", "PB95"
		PB98 = "PB98", "PB98"

	STATUS_CHOICES = (
		('available', 'Available'),
		('rented', 'Rented'),
		('maintenance', 'Maintenance'),
		('pending_inspection', 'Pending Inspection'),  # <-- НОВЫЙ СТАТУС
	)

	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
	slug = models.SlugField(max_length=150, unique=True, blank=True)
	brand = models.CharField(max_length=100, verbose_name="Марка")
	model = models.CharField(max_length=100, verbose_name="Модель")
	car_type = models.CharField(
		max_length=20,
		choices=CarType.choices,
		default=CarType.SEDAN,
		verbose_name="Тип"
	)
	year = models.PositiveIntegerField(verbose_name="Год выпуска")
	price_per_day = models.DecimalField(
		max_digits=10,
		decimal_places=2,
		verbose_name="Цена за день (₸)"
	)
	is_available = models.BooleanField(default=True, verbose_name="Доступна")
	description = models.TextField(blank=True, null=True, verbose_name="Описание")
	dealer = models.ForeignKey(
		"Dealer",
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		verbose_name="Дилер"
	)
	main_image = models.ImageField(
		upload_to='cars/main/',
		null=False,
		blank=False,
		verbose_name="Главная фотография"
	)
	photos = models.ManyToManyField(CarPhoto, blank=True, verbose_name="Фото")
	seats = models.IntegerField(default=5, verbose_name="Места")
	doors = models.IntegerField(default=4, verbose_name="Двери")
	mileage = models.IntegerField(default=0, verbose_name="Пробег (км)")
	air_conditioner = models.BooleanField(default=True, verbose_name="Кондиционер")
	transmission = models.CharField(
		max_length=20,
		choices=TransmissionTypes.choices,
		default=TransmissionTypes.MANUAL,
		verbose_name="Трансмиссия"
	)
	fuel_type = models.CharField(
		max_length=20,
		choices=FuelTypes.choices,
		default=FuelTypes.PB95,
		verbose_name="Тип топлива"
	)
	features = JSONField(
		blank=True,
		null=True,
		verbose_name="Дополнительные характеристики",
		help_text="JSON: ключ → значение, например {\"ABS\": true, \"Cruise Control\": true}"
	)
	created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
	updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

	class Meta:
		verbose_name = "Машина"
		verbose_name_plural = "Машины"
		ordering = ["-created_at"]

	def save(self, *args, **kwargs):
		# Автослаг по бренду+модели
		if not self.slug:
			base = f"{self.brand}-{self.model}"
			self.slug = slugify(base)[:150]
		super().save(*args, **kwargs)

	def __str__(self):
		return f"{self.brand} {self.model} ({self.year})"

	def get_absolute_url(self):
		return reverse("car_detail", kwargs={"slug": self.slug})


# 3. Отзывы пользователей на машины
class CarReview(models.Model):
	user = models.ForeignKey(UserModel, on_delete=models.CASCADE, verbose_name="Пользватель")
	car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="reviews", verbose_name="Автомобиль")
	rating = models.FloatField(validators=[MinValueValidator(1.0), MaxValueValidator(5.0)], verbose_name="Оценка")
	comment = models.TextField(blank=True, verbose_name="Комментарий")
	created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата отзыва")

	def __str__(self):
		return f"Отзыв {self.user.username} на {self.car} ({self.rating})"

	class Meta:
		verbose_name = "Отзыв Машины"
		verbose_name_plural = "Отзывы Машин"


class Rental(models.Model):
	PAYMENT_METHODS = (
		("CARD", "Банковская карта"),
		("PAYPAL", "PayPal"),
		("BITCOIN", "Bitcoin"),
	)

	STATUS_CHOICES = (
		("WAITING", "Ожидание ответа от Stripe"),
		("OWNED", "Пользватель еще пользуется услугой"),
		("COMPLETED", "Завершена"),
		("REJECTED", "Отказано"),
		("CANCELED", "Отмена от пользвателя")
	)

	user = models.ForeignKey(UserModel, on_delete=models.CASCADE, verbose_name="Пользователь")
	car = models.ForeignKey('Car', on_delete=models.CASCADE, verbose_name="Автомобиль")

	start_time = models.DateTimeField(default=now, verbose_name="Начало аренды")
	end_time = models.DateTimeField(verbose_name="Окончание аренды")

	# Личные данные
	full_name = models.CharField(max_length=255, verbose_name="ФИО")
	phone_number = models.CharField(max_length=20, verbose_name="Телефон")
	address = models.TextField(verbose_name="Адрес")
	city = models.CharField(max_length=100, verbose_name="Город")

	# Локация аренды
	pickup_location = models.CharField(max_length=255, verbose_name="Место получения")
	pickup_date = models.DateField(verbose_name="Дата получения")
	pickup_time = models.TimeField(verbose_name="Время получения")

	# Локация возврата
	dropoff_location = models.CharField(max_length=255, verbose_name="Место возврата")
	dropoff_date = models.DateField(verbose_name="Дата возврата")
	dropoff_time = models.TimeField(verbose_name="Время возврата")

	# Оплата
	payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS, verbose_name="Метод оплаты")
	card_number = models.CharField(max_length=16, blank=True, null=True, verbose_name="Номер карты")
	expiration_date = models.CharField(max_length=7, blank=True, null=True, verbose_name="Срок действия карты (MM/YY)")
	card_holder = models.CharField(max_length=255, blank=True, null=True, verbose_name="Владелец карты")
	cvc = models.CharField(max_length=3, blank=True, null=True, verbose_name="CVC")

	is_paid = models.BooleanField(default=False, verbose_name="Оплачено")
	total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True,
	                                  verbose_name="Итоговая цена")
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="WAITING", verbose_name="Статус")

	created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
	updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

	def save(self, *args, **kwargs):
		"""
		Автоматический расчет стоимости аренды. Если заданы даты получения и возврата,
		вычисляется количество дней (минимум 1 день) и итоговая цена = количество дней * цена за час * 24.
		"""
		if self.pickup_date and self.dropoff_date:
			# Если поля типа str, преобразуем их в date
			if isinstance(self.pickup_date, str):
				self.pickup_date = datetime.strptime(self.pickup_date, "%Y-%m-%d").date()
			if isinstance(self.dropoff_date, str):
				self.dropoff_date = datetime.strptime(self.dropoff_date, "%Y-%m-%d").date()
			days = (self.dropoff_date - self.pickup_date).days
			if days < 1:
				days = 1
			self.total_price = days * self.car.price_per_day
		super().save(*args, **kwargs)

	def __str__(self):
		return f"Аренда {self.car} пользователем {self.user.username} (Статус: {self.get_status_display()})"

	class Meta:
		verbose_name = "Аренда"
		verbose_name_plural = "Аренды"


class Transaction(models.Model):
	TRANSACTION_TYPES = (
		("TOP_UP", "Пополнение баланса"),
		("RENTAL", "Оплата аренды"),
	)

	TRANSACTION_STATUSES = (
		("WAITING", "Ожидание ответа от strype"),
		("COMPLETED", "Закончен"),
		("REJECTED", "Отказано")
	)

	user = models.ForeignKey(UserModel, on_delete=models.CASCADE, verbose_name="Пользователь")
	transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES, verbose_name="Тип")
	amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма")
	timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Дата")
	status = models.CharField(max_length=20, choices=TRANSACTION_STATUSES, verbose_name="Статус")

	def __str__(self):
		return f"Транзакция {self.user.username}: {self.transaction_type} {self.amount}"

	class Meta:
		verbose_name = "Транзакция"
		verbose_name_plural = "Транзакции"


# 3. Текущее местоположение машины
class CarLocation(models.Model):
	car = models.OneToOneField(Car, on_delete=models.CASCADE, related_name="location", verbose_name="Автомобиль")
	latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Широта")
	longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Долгота")
	updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

	def __str__(self):
		return f"Местоположение {self.car} ({self.latitude}, {self.longitude})"

	@staticmethod
	def get_last_position(car_id):
		"""Получает последнюю зафиксированную позицию машины"""
		try:
			return CarLocation.objects.get(car_id=car_id)
		except CarLocation.DoesNotExist:
			return None

	class Meta:
		verbose_name = "Расположение Машины"
		verbose_name_plural = "Расположение Машин"


# 4. История перемещений (лог трекинга)
class TripTracking(models.Model):
	rental = models.ForeignKey("Rental", on_delete=models.CASCADE, related_name="tracking", verbose_name="Аренда")
	timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Время фиксации")
	latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Широта")
	longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Долгота")

	def __str__(self):
		return f"Трек аренды {self.rental.id} ({self.latitude}, {self.longitude})"

	class Meta:
		verbose_name = "Трекер Машины"
		verbose_name_plural = "Трекер Машин"


# 6. Штрафы
class Fine(models.Model):
	user = models.ForeignKey(UserModel, on_delete=models.CASCADE, verbose_name="Пользователь")
	rental = models.ForeignKey(Rental, on_delete=models.CASCADE, verbose_name="Аренда")
	amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма штрафа")
	reason = models.TextField(verbose_name="Причина")
	issued_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата")

	def __str__(self):
		return f"Штраф {self.user.username} ({self.amount} руб.)"

	class Meta:
		verbose_name = "Штраф"
		verbose_name_plural = "Штрафы"


class Favorite(models.Model):
	user = models.ForeignKey(UserModel,
	                         on_delete=models.CASCADE)
	car = models.ForeignKey(Car, on_delete=models.CASCADE)
	added_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = ('user', 'car')


class Notification(models.Model):
	user = models.ForeignKey(UserModel,
	                         related_name='notifications',
	                         on_delete=models.CASCADE)
	title = models.CharField(max_length=150)
	message = models.TextField(blank=True)
	is_read = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-created_at']
