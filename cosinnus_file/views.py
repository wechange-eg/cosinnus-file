# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import mimetypes

from os.path import basename

from django.contrib import messages
from django.http import (Http404, HttpResponse, HttpResponseNotFound,
    HttpResponseRedirect, StreamingHttpResponse)
from django.utils.translation import ungettext, ugettext_lazy as _
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
    RedirectView, UpdateView, View)
from django.views.generic.edit import FormMixin

from cosinnus.conf import settings
from cosinnus.utils.files import create_zip_file
from cosinnus.templatetags.cosinnus_tags import add_current_params
from cosinnus.views.mixins.group import (RequireReadMixin, RequireWriteMixin,
    FilterGroupMixin, GroupFormKwargsMixin)
from cosinnus.views.mixins.tagged import HierarchyTreeMixin, HierarchyPathMixin,\
    HierarchyDeleteMixin
from cosinnus.views.mixins.user import UserFormKwargsMixin

from cosinnus_file.forms import FileForm, FileListForm
from cosinnus_file.models import FileEntry
from cosinnus.views.mixins.hierarchy import HierarchicalListCreateViewMixin
from cosinnus.views.mixins.filters import CosinnusFilterMixin
from cosinnus_file.filters import FileFilter
from cosinnus.utils.urls import group_aware_reverse
from cosinnus_file.utils.strings import clean_filename


class FileFormMixin(FilterGroupMixin, GroupFormKwargsMixin,
                    UserFormKwargsMixin):
    message_success = _('File "%(title)s" was uploaded successfully.')
    message_error = _('File "%(title)s" could not be uploaded.')

    def get_context_data(self, **kwargs):
        context = super(FileFormMixin, self).get_context_data(**kwargs)
        tags = FileEntry.objects.tags()
        context.update({
            'form_view': self.form_view,
            'tags': tags
        })
        return context
    
    def form_valid(self, form):
        form.instance.creator = self.request.user
        # save/update filesize
        form.instance._filesize = form.instance.file.file.size
        
        ret = super(FileFormMixin, self).form_valid(form)
        messages.success(self.request,
            self.message_success % {'title': self.object.title})
        return ret

    def form_invalid(self, form):
        ret = super(FileFormMixin, self).form_invalid(form)
        if self.object:
            messages.error(self.request,
                self.message_error % {'title': self.object.title})
        return ret
    
    def get_success_url(self):
        return group_aware_reverse('cosinnus:file:list',
                       kwargs={'group': self.group,
                               'slug': self.object.slug})
    
    


class FileIndexView(RequireReadMixin, RedirectView):

    def get_redirect_url(self, **kwargs):
        return group_aware_reverse('cosinnus:file:list',
                       kwargs={'group': self.group})

file_index_view = FileIndexView.as_view()


class FileCreateView(RequireWriteMixin, FileFormMixin, CreateView):
    form_view = 'create'
    form_class = FileForm
    model = FileEntry
    template_name = 'cosinnus_file/file_form.html'
    
    message_success = _('File "%(title)s" was uploaded successfully.')
    message_error = _('File "%(title)s" could not be added.')

    def get_object(self, queryset=None):
        return CreateView.get_object(self, queryset=queryset)

    def get_context_data(self, **kwargs):
        context = super(FileCreateView, self).get_context_data(**kwargs)
        tags = FileEntry.objects.tags()
        context.update({
            'tags': tags
        })

        return context

file_create_view = FileCreateView.as_view()


class FileHybridListView(RequireReadMixin, HierarchyPathMixin, HierarchicalListCreateViewMixin, 
                             CosinnusFilterMixin, FileCreateView):
    template_name = 'cosinnus_file/file_list.html'
    filterset_class = FileFilter
    
    message_success_folder = _('Folder "%(title)s" was created successfully.')
    
    def get_success_url(self):
        if self.object.is_container:
            messages.success(self.request,
                self.message_success_folder % {'title': self.object.title})
        return group_aware_reverse('cosinnus:file:list', kwargs={
                'group': self.group,
                'slug': self.object.slug})

file_hybrid_list_view = FileHybridListView.as_view()


class FileDeleteView(RequireWriteMixin, FilterGroupMixin, HierarchyDeleteMixin, DeleteView):

    model = FileEntry
    template_name = 'cosinnus_file/file_delete.html'

    def get(self, request, *args, **kwargs):
        try:
            return super(FileDeleteView, self).get(request, *args, **kwargs)
        except Http404:
            messages.error(request, _('File does not exist or you are not allowed to delete it.'))
            return HttpResponseRedirect(self.get_success_url())

    def post(self, request, *args, **kwargs):
        try:
            return super(FileDeleteView, self).post(request, *args, **kwargs)
        except Http404:
            messages.error(request, _('File does not exist or you are not allowed to delete it.'))
            return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return "%s%s" % (group_aware_reverse('cosinnus:file:list', kwargs={'group': self.group}), add_current_params(None, self.request))

file_delete_view = FileDeleteView.as_view()


class FileDetailView(RequireReadMixin, FilterGroupMixin, DetailView):

    model = FileEntry
    template_name = 'cosinnus_file/file_detail.html'

file_detail_view = FileDetailView.as_view()



class FileListView(RequireReadMixin, FilterGroupMixin,
                   FormMixin, HierarchyTreeMixin, ListView):

    form_class = FileListForm
    model = FileEntry
    template_name = 'cosinnus_file/file_list.html'

    def get_context_data(self, **kwargs):
        context = super(FileListView, self).get_context_data(**kwargs)
        tree =  self.get_tree(self.object_list)
        context.update({'filetree': tree})
        return context

    def form_valid(self, form):
        if 'download' in self.request.POST:
            d = form.cleaned_data
            ids = map(int, d.get('select', []))
            files = FileEntry.objects.filter(id__in=ids)
            if not files:
                messages.warning(self.request, _('No files selected.'))
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
        messages.error(self.request, _('Invalid request.'))
        return HttpResponseRedirect(self.request.path)

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        files = self.get_queryset()
        form.fields['select'].choices = [(f.id, '') for f in files]

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.get(request, *args, **kwargs)

file_list_view = FileListView.as_view()


class FileUpdateView(RequireWriteMixin, FileFormMixin, UpdateView):
    form_view = 'edit'
    form_class = FileForm
    model = FileEntry
    template_name = 'cosinnus_file/file_edit.html'
    
    message_success = _('File "%(title)s" was updated successfully.')
    message_error = _('File "%(title)s" could not be updated.')

    def get_context_data(self, **kwargs):
        context = super(FileUpdateView, self).get_context_data(**kwargs)
        tags = FileEntry.objects.tags()
        context.update({
            'tags': tags
        })
        return context

file_update_view = FileUpdateView.as_view()


class FileDownloadView(RequireReadMixin, FilterGroupMixin, View):
    '''
        Lets the user download a FileEntry file (file is determined by slug),
        while the user never gets to see the server file path.
        Mime type is guessed based on the file
    '''
    mimetypes.init()

    def get(self, request, *args, **kwargs):
        path = None

        slug = kwargs.get('slug', None)
        if slug:
            files = FileEntry.objects.filter(slug=slug)
            try:
                fileentry = files[0]
                dlfile = fileentry.file
                path = dlfile.path
            except:
                raise Http404

        response = HttpResponseNotFound()
        
        if path:
            fp = open(path, 'rb')
            response = HttpResponse(fp.read())
            fp.close()
            content_type, encoding = mimetypes.guess_type(fileentry.sourcefilename)
            filename = fileentry.sourcefilename
            if content_type is None:
                content_type = fileentry.mimetype or 'application/octet-stream'
            response['Content-Type'] = content_type
            response['Content-Length'] = fileentry._filesize
            if encoding is not None:
                response['Content-Encoding'] = encoding
        
            # To inspect details for the below code, see http://greenbytes.de/tech/tc2231/
            if u'WebKit' in request.META['HTTP_USER_AGENT']:
                # Safari 3.0 and Chrome 2.0 accepts UTF-8 encoded string directly.
                filename_header = 'filename=%s' % clean_filename(filename)
            elif u'MSIE' in request.META['HTTP_USER_AGENT']:
                # IE does not support internationalized filename at all.
                # It can only recognize internationalized URL, so we do the trick via routing rules.
                filename_header = ''
            else:
                # For others like Firefox, we follow RFC2231 (encoding extension in HTTP headers).
                filename_header = 'filename*=UTF-8\'\'%s' % clean_filename(filename)
            response['Content-Disposition'] = 'attachment; ' + filename_header
        
        return response
    
    
file_download_view = FileDownloadView.as_view()
