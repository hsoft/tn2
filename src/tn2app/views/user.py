from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import views as auth_views
from django.db.models import Q
from django.views.generic import ListView, FormView
from django.views.generic.edit import UpdateView

from ..models import (
    UserProfile, Project, ProjectVote, Notification, Message
)
from ..forms import (
    UserProfileForm, UserSendMessageForm, LoginForm
)
from .common import UserViewMixin, BelongsToUserMixin

class UserProfileView(UserViewMixin, ListView):
    MENU_SELECTED_INDEX = 0
    template_name = 'user_profile.html'
    model = Project
    ordering = '-creation_time'
    paginate_by = 9

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(author=self._get_shown_user())

    def user_can_admin(self):
        return self.request.user.has_perm('tn2app.change_userprofile')


class UserFavoritesView(UserViewMixin, ListView):
    MENU_SELECTED_INDEX = 1
    template_name = 'user_favorites.html'
    model = ProjectVote
    ordering = '-date_liked'
    paginate_by = 9

    def breadcrumb(self):
        return super().breadcrumb() + [(None, "Favoris")]

    def get_context_data(self, **kwargs):
        result = super().get_context_data(**kwargs)
        result['project_list'] = [vote.project for vote in result['projectvote_list']]
        return result

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self._get_shown_user(), favorite=True)


class UserProfileEdit(UserViewMixin, BelongsToUserMixin, UpdateView):
    USER_ATTR = 'user'
    SUPERUSER_PERM = 'tn2app.change_userprofile'
    MENU_SELECTED_INDEX = 0

    template_name = 'user_profile_edit.html'
    model = UserProfile
    form_class = UserProfileForm
    context_object_name = 'profile'

    def breadcrumb(self):
        return super().breadcrumb() + [(None, "Modifier")]

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        return self._get_shown_user().profile


class UserSendMessageView(UserViewMixin, LoginRequiredMixin, FormView):
    MENU_SELECTED_INDEX = 2
    form_class = UserSendMessageForm
    template_name = 'user_sendmessage.html'

    def breadcrumb(self):
        return super().breadcrumb() + [(None, "Contacter")]

    def form_valid(self, form):
        to = self._get_shown_user()
        from_ = self.request.user
        msg = Message.objects.create(from_user=from_, to_user=to, content=form.cleaned_data['message'])
        Notification.objects.notify_of_message(msg)
        return self.render_to_response(self.get_context_data(message_sent=True))


class UserMessagesView(UserViewMixin, LoginRequiredMixin, ListView):
    SELF_ONLY = True
    MENU_SELECTED_INDEX = 2
    template_name = 'user_messages.html'
    model = Message

    def get_queryset(self):
        queryset = super().get_queryset()
        u = self._get_shown_user()
        return queryset.filter(Q(from_user=u) | Q(to_user=u))


class UserNotificationsView(UserViewMixin, LoginRequiredMixin, ListView):
    SELF_ONLY = True
    MENU_SELECTED_INDEX = 4
    template_name = 'user_notifications.html'
    model = Notification

    def breadcrumb(self):
        return super().breadcrumb() + [(None, "Notifications")]

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.profile.has_notifications:
            user.profile.has_notifications = False
            user.profile.save()
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return self._get_shown_user().notifications.all()


class LoginView(auth_views.LoginView):
    form_class = LoginForm

    @staticmethod
    def breadcrumb():
        return [(None, "Connexion")]


class ChangePasswordView(UserViewMixin, auth_views.PasswordChangeView):
    SELF_ONLY = True
    MENU_SELECTED_INDEX = 3
    done = False

    @staticmethod
    def breadcrumb():
        return [(None, "Modifier mon mot de passe")]

