import datetime

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Q, OuterRef, Subquery, IntegerField
from django.forms.widgets import Select
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.views.generic import ListView, DetailView, RedirectView
from django.views.generic.edit import CreateView, UpdateView

from ..forms import ProjectForm
from ..models import (
    Project, Pattern, PatternCategory, PatternCreator, ProjectVote, Notification, Contest
)
from ..util import href
from ..widgets import UnrolledSelect, UnrolledTwoColsSelect, CheckboxList
from .common import ViewWithCommentsMixin, UserViewMixin, BelongsToUserMixin, LogFormErrorMixin

class ProjectList(ListView):
    template_name = 'project_list.html'
    model = Project
    paginate_by = 15

    def active_order(self):
        result = self.request.GET.get('order')
        if result not in {'latest', 'popular', 'random'}:
            result = 'latest'
        return result

    def target_selector(self):
        return UnrolledTwoColsSelect(
            self.request.GET.copy(),
            Pattern.TARGET_CHOICES,
            'target',
        ).render()

    def domain_selector(self):
        return UnrolledTwoColsSelect(
            self.request.GET.copy(),
            Pattern.DOMAIN_CHOICES,
            'domain',
        ).render()

    def category_selector(self):
        return UnrolledTwoColsSelect(
            self.request.GET.copy(),
            PatternCategory.objects.values_list('id', 'name'),
            'category',
        ).render()

    def pattern_checkboxes(self):
        reqparams = self.request.GET.copy()
        # as a special case, we always remove the 'pattern_id' param when selecting a
        # box from pattern_checkboxes to avoid weird empty listing.
        reqparams.pop('pattern_id', None)
        if 'pattern_id' in reqparams:
            del reqparams['pattern_id']

        return CheckboxList(
            reqparams,
            [('pattern_is_free', "Gratuit"), ('pattern_is_jersey', "Tissu Maille")]
        )

    def pattern_selectors(self):
        # This method became complicated, hence this comment. What are we trying to achieve here?
        #
        # Of course, we want a list of pattern creators. But also, if we have selected a creator,
        # we want its list of patterns. So there's that. Simple, right?
        #
        # But it's not over! We also want to avoid having our creator list polluted by patternless
        # creators (there are a couple of them in the DB), so our creator_qs has to be beefed up.
        #
        # But wait! now we have is_free and is_jersey flags. We want these to affect the list of
        # patterns and creators available for selection. *this* particularly complicates this
        # and make creator_qs much more complex.

        item_all = [(0, "Tous")]

        def pop(key):
            val = params.pop(key, None)
            if isinstance(val, list):
                val = val[0] if val else None
            return val

        params = self.request.GET.copy()
        params['page'] = '1'

        pattern_id = pop('pattern')
        pattern_creator_id = pop('pattern_creator')
        if pattern_id and Pattern.objects.filter(id=pattern_id).exists():
            # More reliable than the request argument.
            pattern_creator_id = Pattern.objects.get(id=pattern_id).creator.id

        pattern_filters = {
            v.replace('pattern_', ''): True
            for v in self.pattern_checkboxes().get_selected_options()
        }
        pattern_qs = Pattern.objects.filter(**pattern_filters)

        # Woah, complicated...
        # https://stackoverflow.com/a/30753074
        pattern_sub = Subquery(
            pattern_qs.filter(creator_id=OuterRef('pk'))
                .annotate(cnt=Count('pk'))
                .values('cnt')[:1],
            output_field=IntegerField()
        )
        creator_filter = Q(pattern_count__gt=0)

        # We always want a selected creator to show up, even if it has no pattern
        if pattern_creator_id:
            creator_filter |= Q(id=pattern_creator_id)

        creator_qs = PatternCreator.objects\
            .annotate(pattern_count=pattern_sub)\
            .filter(creator_filter)

        get_url = '?{}&pattern_creator='.format(params.urlencode())
        widget = Select(
            attrs={'data-get-url': get_url},
            choices=item_all + list(creator_qs.values_list('id', 'name')),
        )
        result = [widget.render(
            name='pattern_creator',
            value=pattern_creator_id,
        )]

        if pattern_creator_id and creator_qs.filter(id=pattern_creator_id).exists():
            pattern_creator = PatternCreator.objects.get(id=pattern_creator_id)
            pattern_qs = pattern_qs.filter(creator=pattern_creator)
            params['pattern_creator'] = pattern_creator_id
            get_url = '?{}&pattern='.format(params.urlencode())
            widget = Select(
                attrs={'data-get-url': get_url},
                choices=item_all + list(pattern_qs.values_list('id', 'name')),
            )
            result.append(widget.render(
                name='pattern',
                value=pattern_id,
            ))

        return result

    def contest_selector(self):
        return UnrolledSelect(
            self.request.GET.copy(),
            Contest.objects.values_list('id', 'name'),
            'contest',
        )

    def popular_this_week(self):
        return Project.objects.popular_this_week()

    @staticmethod
    def breadcrumb():
        return [(reverse('project_list'), "Projets couture")]

    def get_ordering(self):
        order = self.active_order()
        if order == 'popular':
            return '-num_likes'
        elif order == 'random':
            return '?'
        else:
            return '-creation_time'

    def get_queryset(self):

        def get(argname):
            try:
                return int(self.request.GET.get(argname))
            except (ValueError, TypeError):
                return None

        queryset = super().get_queryset()
        ARGSMAP = {
            'category': 'category_id',
            'domain': 'domain',
            'target': 'target',
            'pattern_creator': 'pattern__creator',
            'pattern': 'pattern_id',
        }
        filters = {v: get(k) for k, v in ARGSMAP.items() if get(k)}

        BOOLARGSMAP = {
            'pattern_is_free': 'pattern__is_free',
            'pattern_is_jersey': 'pattern__is_jersey',
        }
        filters.update({v: get(k) == 1 for k, v in BOOLARGSMAP.items() if get(k)})
        if filters:
            queryset = queryset.filter(**filters)

        order = self.active_order()
        if order == 'popular':
            queryset = queryset.annotate(num_likes=Count('likes'))
        elif order == 'random':
            # We only want one page of this, paginating is irrelevant here.
            queryset = queryset[:self.paginate_by]
        return queryset


class ProjectDetails(ViewWithCommentsMixin, DetailView):
    template_name = 'project_details.html'
    model = Project

    def breadcrumb(self):
        return ProjectList.breadcrumb() + [(None, self.get_object().title)]

    def user_can_admin(self):
        return self.request.user.has_perm('tn2app.change_project')

    def is_liked(self):
        return self.get_object().likes.filter(pk=self.request.user.id).exists()

    def is_favorite(self):
        try:
            return ProjectVote.objects.get(
                project=self.get_object(), user=self.request.user.id
            ).favorite
        except ProjectVote.DoesNotExist:
            return False

    def myprojects(self):
        current = self.get_object()
        return current.author.projects.exclude(id=current.id)

    def category_links(self):

        def l(argname, arg, name):
            return href(
                '{}?{}={}'.format(reverse('project_list'), argname, arg), name
            )

        project = self.get_object()
        links = []
        if project.category:
            links.append(l('category', project.category.id, project.category.name))
        links.append(l('target', project.target, project.get_target_display()))
        links.append(l('domain', project.domain, project.get_domain_display()))
        return mark_safe(', '.join(links))

    def pattern_link(self):
        project = self.get_object()
        if project.pattern:
            name = project.pattern.name
            url = project.pattern.url
        else:
            name = project.pattern_name
            url = project.pattern_url
            if url and not url.startswith('http'):
                url = 'http://{}'.format(url)
        if url:
            return href(url, name, newwindow=True)
        else:
            return name

    def creator_link(self):
        project = self.get_object()
        if project.pattern:
            creator = project.pattern.creator
            if creator:
                if creator.url:
                    return href(creator.url, creator.name, newwindow=True)
                else:
                    return creator.name

    def allprojects(self):
        # it's a really strange query that is made in the old app: it's 3 items with, in the middle,
        # the current project. Then, on the left, the project created just before it, and on the
        # right, the project created after it. Well... let's do the same thing.
        current = self.get_object()
        q1 = self.model.objects.filter(id__lt=current.id).order_by('-id')
        q2 = self.model.objects.filter(id__gt=current.id).order_by('id')
        if q1.exists() and q2.exists():
            return [q1.first(), current, q2.first()]
        elif not q1.exists():
            return [current] + list(q2.all()[:2])
        else:
            return list(q1.all()[:2]) + [current]


class ProjectEdit(BelongsToUserMixin, LogFormErrorMixin, UpdateView):
    USER_ATTR = 'author'
    SUPERUSER_PERM = 'tn2app.change_project'
    TITLE = "Modifier un projet"
    ACTION_NAME = "Modifier"
    FORM_CLASS = 'editproject'

    template_name = 'project_edit.html'
    form_class = ProjectForm
    model = Project

    def breadcrumb(self):
        project = self.get_object()
        return ProjectList.breadcrumb() + [
            (project.get_absolute_url(), project.title),
            (None, "Modifier"),
        ]

    def post_url(self):
        project = self.get_object()
        return reverse('project_edit', kwargs={'pk': project.pk, 'slug': project.get_slug()})

    def post(self, request, *args, **kwargs):
        if 'delete' in request.POST:
            project = self.get_object()
            success_url = project.author.profile.get_absolute_url()
            project.delete()
            return HttpResponseRedirect(success_url)
        else:
            return super().post(request, *args, **kwargs)


class ProjectCreate(LoginRequiredMixin, UserViewMixin, LogFormErrorMixin, CreateView):
    template_name = 'project_edit.html'
    form_class = ProjectForm
    TITLE = "Publier un projet"
    ACTION_NAME = "Publier"
    FORM_CLASS = 'newproject'

    def breadcrumb(self):
        return super().breadcrumb() + [(None, "Publier un projet")]

    def post_url(self):
        user = self.request.user
        return reverse('project_create', kwargs={'username': user.username})

    def get_form_kwargs(self):
        result = super().get_form_kwargs()
        result['author'] = self.request.user
        return result


class ProjectAction(RedirectView):
    pattern_name = 'project_details'

    def _do_project_action(self, project):
        raise NotImplementedError()

    def get(self, request, *args, **kwargs):
        result = super().get(request, *args, **kwargs)
        try:
            project = Project.objects.get(pk=kwargs['pk'])
        except Project.DoesNotExist:
            raise Http404()
        self._do_project_action(project)
        return result


class ProjectLike(LoginRequiredMixin, ProjectAction):
    def _do_project_action(self, project):
        try:
            ProjectVote.objects.get(user=self.request.user, project=project).delete()
        except ProjectVote.DoesNotExist:
            vote = ProjectVote.objects.create(user=self.request.user, project=project)
            Notification.objects.notify_of_project_vote(vote)


class ProjectFavorite(LoginRequiredMixin, ProjectAction):
    def _do_project_action(self, project):
        vote, _ = ProjectVote.objects.get_or_create(user=self.request.user, project=project)
        vote.favorite = not vote.favorite
        vote.date_liked = datetime.datetime.now()
        vote.save()


class ProjectFeature(UserPassesTestMixin, ProjectAction):
    # for UserPassesTestMixin
    raise_exception = True

    def test_func(self):
        return self.request.user.has_perm('tn2app.change_project')

    def _do_project_action(self, project):
        project.featured_time = datetime.datetime.now()
        project.save()



