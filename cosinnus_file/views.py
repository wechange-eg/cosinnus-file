# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import mimetypes

from collections import defaultdict
from os.path import basename, dirname

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import (Http404, HttpResponse, HttpResponseNotFound,
    HttpResponseRedirect, StreamingHttpResponse)
from django.shortcuts import get_object_or_404
from django.utils.translation import ungettext, ugettext_lazy as _
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
    RedirectView, UpdateView, View)
from django.views.generic.edit import FormMixin

from cosinnus.conf import settings
from cosinnus.utils.files import create_zip_file
from cosinnus.templatetags.cosinnus_tags import add_current_params
from cosinnus.views.mixins.group import (RequireReadMixin, RequireWriteMixin,
    FilterGroupMixin, GroupFormKwargsMixin)
from cosinnus.views.mixins.tagged import HierarchyTreeMixin, HierarchyPathMixin
from cosinnus.views.mixins.user import UserFormKwargsMixin

from cosinnus_file.forms import FileForm, FileListForm
from cosinnus_file.models import FileEntry
from cosinnus.views.mixins.hierarchy import HierarchicalListCreateViewMixin
from cosinnus.views.mixins.filters import CosinnusFilterMixin
from cosinnus_file.filters import FileFilter


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
        return reverse('cosinnus:file:list',
                       kwargs={'group': self.group.slug})
    
    


class FileIndexView(RequireReadMixin, RedirectView):

    def get_redirect_url(self, **kwargs):
        return reverse('cosinnus:file:list',
                       kwargs={'group': self.group.slug})

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
        return reverse('cosinnus:file:list', kwargs={
                'group': self.group.slug,
                'slug': self.object.slug})

file_hybrid_list_view = FileHybridListView.as_view()


class FileDeleteView(RequireWriteMixin, FilterGroupMixin, DeleteView):

    model = FileEntry
    template_name = 'cosinnus_file/file_delete.html'

    def _getFilesInPath(self, path):
        return FileEntry.objects.filter(path__startswith=path)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.is_container:
            dellist = list(self._getFilesInPath(self.object.path))
        else:
            dellist = [self.object]

        # for a clean deletion, sort so that subelements are always before their parents and files always before folders on the same level
        dellist.sort(key=lambda o: len(o.path) + (0 if o.is_container else 1), reverse=True)

        total_files = len(dellist)
        deleted_count = 0
        for fileentry in dellist:
            """ sanity check: only delete a folder if it is empty
                (there should only be one object (the folder itself) with the path, because
                we have deleted all its files before it!
            """
            if fileentry.is_container:
                folderfiles = self._getFilesInPath(fileentry.path)
                if len(folderfiles) > 1:
                    messages.error(request, _('Folder "%(filename)s" could not be deleted because it contained files that could not be deleted.') % {'filename': fileentry.title})
                    continue
            deletedpk = fileentry.pk
            fileentry.delete()
            # check if deletion was successful
            try:
                checkfileentry = FileEntry.objects.get(pk=deletedpk)
                messages.error(request, _('File "%(filename)s" could not be deleted.') % {'filename': checkfileentry.title})
            except FileEntry.DoesNotExist:
                deleted_count += 1

        if deleted_count > 0:
            if deleted_count > 1 and deleted_count == total_files:
                messages.success(request, _('%(numfiles)d files were deleted successfully.') % {'numfiles': deleted_count})
            elif deleted_count == 1 and total_files == 1:
                messages.success(request, _('File "%(filename)s" was deleted successfully.') % {'filename': fileentry.title})
            else:
                messages.info(request, _('%(numfiles)d other files were deleted.') % {'numfiles': deleted_count})

        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(FileDeleteView, self).get_context_data(**kwargs)
        delfile = kwargs.get('object', None)

        dellist = []
        if delfile:
            if delfile.is_container:
                # special handling for folders being deleted:
                pathfiles = self._getFilesInPath(delfile.path)
                dellist.extend(pathfiles)
            else:
                dellist.append(delfile)

        context['files_to_delete'] = dellist
        return context


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
        return "%s%s" % (reverse('cosinnus:file:list', kwargs={'group': self.group.slug}), add_current_params(None, self.request))

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
        slug = kwargs.get('slug', None)
        if slug:
            files = FileEntry.objects.filter(slug=slug)
            try:
                fileentry = files[0]
                dlfile = fileentry.file
                path = dlfile.path
            except:
                pass

        response = HttpResponseNotFound()
        if path:
            try:
                fsock = open(path, "rb")
                mime_type_guess = mimetypes.guess_type(path)
                if mime_type_guess is not None:
                    response = HttpResponse(fsock, mimetype=mime_type_guess[0])
                response['Content-Disposition'] = 'attachment; filename=' + fileentry._sourcefilename
            except IOError:
                if settings.DEBUG:
                    raise
                else:
                    pass

        return response

file_download_view = FileDownloadView.as_view()
