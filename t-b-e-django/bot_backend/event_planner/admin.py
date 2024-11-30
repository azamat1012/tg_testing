from django.contrib import admin
from .models import Event, Speaker, Session, SpeakerSession, User
from .utils import get_schedule
from telebot import TeleBot


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'location')
    search_fields = ('name', 'location')
    list_filter = ('date',)
    ordering = ('date',)


@admin.register(Speaker)
class SpeakerAdmin(admin.ModelAdmin):
    list_display = ('name', 'stack')
    search_fields = ('name', 'stack')
    ordering = ('name',)


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'event')
    search_fields = ('title', 'event__name')
    list_filter = ('event',)
    ordering = ('event__date',)


@admin.register(SpeakerSession)
class SpeakerSessionAdmin(admin.ModelAdmin):
    list_display = ('speaker', 'topic', )
    search_fields = ('speaker__name', 'topic')
    ordering = ('session__event__date',)


@admin.action(description="Рассылка о изменении в расписании")
def send_massage_to_all_users(modeladmin, request, queryset):
    bot = TeleBot("8066339717:AAFqYwMs5zx8va4mYBMgV8i9xFwXVK_4RKI")
    users = User.objects.all()
    massage_text = get_schedule()
    for user in users:
        bot.send_message(user.tg_id, massage_text)

    modeladmin.message_user(
        request, "Сообщения отправлены всем пользователям!")


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    actions = [send_massage_to_all_users]
