# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from os.path import basename

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect, StreamingHttpResponse
from django.utils.translation import ugettext, ungettext
from django.views.generic.base import RedirectView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, FormMixin, UpdateView
from django.views.generic.list import ListView

from extra_views.contrib.mixins import SortableListMixin

from cosinnus.authentication.views import FilterGroupMixin, RequireGroupMixin
from cosinnus.utils.views import TaggedListMixin
from cosinnus.utils.zip import create_zip_file

from cosinnus_file.forms import FileForm, FileListForm
from cosinnus_file.models import FileEntry


class FileFormMixin(object):

    def dispatch(self, request, *args, **kwargs):
        self.form_view = kwargs.get('form_view', None)
        return super(FileFormMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(FileFormMixin, self).get_context_data(**kwargs)
        context.update({'form_view': self.form_view})
        return context

    def get_success_url(self):
        return reverse('sinn_file-entry-list',
                       kwargs={'group': self.group.pk})


class FileIndexView(RequireGroupMixin, RedirectView):

    def get_redirect_url(self, **kwargs):
        return reverse('sinn_file-entry-list',
                       kwargs={'group': self.group.pk})


class FileCreateView(RequireGroupMixin, FilterGroupMixin, FileFormMixin,
                     CreateView):

    form_class = FileForm
    model = FileEntry
    template_name = 'file/file_form.html'

    def get_context_data(self, **kwargs):
        context = super(FileCreateView, self).get_context_data(**kwargs)
        tags = FileEntry.objects.tags()
        context.update({
            'tags': tags
        })
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.uploaded_by = self.request.user
        self.object.group = self.group
        ret = super(FileCreateView, self).form_valid(form)
        form.save_m2m()
        return ret


class FileDeleteView(RequireGroupMixin, FilterGroupMixin, FileFormMixin,
                     DeleteView):

    model = FileEntry
    template_name = 'file/file_form.html'

    def get_queryset(self):
        qs = super(FileDeleteView, self).get_queryset()
        if self.request.user.is_superuser:
            return qs
        return qs.filter(uploaded_by=self.request.user)

    def get(self, request, *args, **kwargs):
        try:
            return super(FileDeleteView, self).get(request, *args, **kwargs)
        except Http404:
            messages.error(request, ugettext(u'File does not exist or you '
                                             u'are not allowed to delete it.'))
            return HttpResponseRedirect(self.get_success_url())

    def post(self, request, *args, **kwargs):
        try:
            return super(FileDeleteView, self).post(request, *args, **kwargs)
        except Http404:
            messages.error(request, ugettext(u'File does not exist or you '
                                             u'are not allowed to delete it.'))
            return HttpResponseRedirect(self.get_success_url())


class FileDetailView(RequireGroupMixin, FilterGroupMixin, DetailView):

    model = FileEntry
    template_name = 'file/file_detail.html'


class FileListView(RequireGroupMixin, FilterGroupMixin, TaggedListMixin,
                   SortableListMixin, FormMixin, ListView):

    form_class = FileListForm
    model = FileEntry
    template_name = 'file/file_list.html'

    def get(self, request, *args, **kwargs):
        self.sort_fields_aliases = self.model.SORT_FIELDS_ALIASES
        return super(FileListView, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        if 'download' in self.request.POST:
            d = form.cleaned_data
            ids = map(int, d.get('select', []))
            files = FileEntry.objects.filter(id__in=ids)
            if not files:
                messages.warning(self.request, ugettext('No files selected.'))
                return HttpResponseRedirect(self.request.path)

            filenames = [(f.file.path, f.file.name) for f in files]
            zf, missing = create_zip_file(filenames)
            download_fn = '_'.join([basename(f.file.name) for f in files])[:50]
            if missing:
                messages.warning(self.request,
                    ungettext(
                        'A problem occurred during export. The following file is missing: %(filename)s.',
                        'A problem occurred during export. The following files are missing: %(filename)s.',
                        len(missing)
                    ) % {
                        'filename': ', '.join(map(basename, missing))
                    }
                )
                return HttpResponseRedirect(self.request.path)
            response = StreamingHttpResponse(open(zf.name, 'rb'), content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename=' + download_fn + '.zip'
            return response

        # Either the request is valid (we offer the download or throw an
        # appropriate message) or the request ist invalid, (e.g. the user
        # didn't press the 'download' button and ca
        messages.error(self.request, ugettext('Invalid request.'))
        return HttpResponseRedirect(self.request.path)

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        files = self.get_queryset()
        form.fields['select'].choices = [(f.id, u'') for f in files]

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.get(request, *args, **kwargs)


class FileUpdateView(RequireGroupMixin, FilterGroupMixin, FileFormMixin,
                     UpdateView):

    form_class = FileForm
    model = FileEntry
    template_name = 'file/file_form.html'

    def get_context_data(self, **kwargs):
        context = super(FileUpdateView, self).get_context_data(**kwargs)
        tags = FileEntry.objects.tags()
        context.update({
            'tags': tags
        })
        return context
