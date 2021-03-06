import logging

from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import Http404
from django.urls import reverse
from django.views.generic.base import ContextMixin

from ..forms import CommentForm
from ..models import User
from ..widgets import Menu

logger = logging.getLogger(__name__)

class ViewWithCommentsMixin:
    def get_comment_form(self):
        return CommentForm()


class UserViewMixin(ContextMixin):
    MENU_SELECTED_INDEX = -1
    SELF_ONLY = False

    def _get_shown_user(self):
        if self.SELF_ONLY:
            return self.request.user
        try:
            return User.objects.get(username=self.kwargs['username'])
        except User.DoesNotExist:
            raise Http404()

    def breadcrumb(self):
        u = self._get_shown_user()
        return [(reverse('user_profile', args=(u.username, )), u.profile.display_name)]

    def get_menu(self):
        u = self._get_shown_user()
        uname = u.username
        ITEMS = [
            ("Projets", reverse('user_profile', args=(uname,))),
            ("Favoris", reverse('user_favorites', args=(uname,))),
        ]
        if u == self.request.user:
            ITEMS += [
                ("Messages", reverse('user_messages')),
                ("Mot de passe", reverse('auth_password_change')),
                ("Notifications", reverse('user_notifications')),
            ]
        else:
            ITEMS.append(("Contacter", reverse('user_sendmessage', args=(uname, ))))
        return Menu(ITEMS, self.MENU_SELECTED_INDEX)

    def get_context_data(self, **kwargs):
        result = super().get_context_data(**kwargs)
        result['shown_user'] = self._get_shown_user()
        return result


class BelongsToUserMixin(UserPassesTestMixin):
    USER_ATTR = None
    SUPERUSER_PERM = None
    raise_exception = True

    def test_func(self):
        u = self.request.user
        return u == getattr(self.get_object(), self.USER_ATTR) or u.has_perm(self.SUPERUSER_PERM)


class LogFormErrorMixin:
    def form_invalid(self, form):
        logger.warning(
            "Form error from user %s: %r",
            self.request.user.username,
            form.errors.as_data(),
        )
        return super().form_invalid(form)

