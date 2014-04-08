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
from cosinnus.views.mixins.group import (RequireReadMixin, RequireWriteMixin,
    FilterGroupMixin)
from cosinnus.views.mixins.tagged import TaggedListMixin

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

    def form_valid(self, form):
        creating = self.object is None

        form.instance.creator = self.request.user
        form.instance.save()

        # only after this save do we know the final slug
        # we still must add it to the end of our path if we're saving a folder
        # however not when we're only updating the object
        if form.instance.isfolder and creating:
            suffix = self.object.slug + '/'
            form.instance.path += suffix
        return super(FileFormMixin, self).form_valid(form)

    def get_success_url(self):
        return reverse('cosinnus:file:list',
                       kwargs={'group': self.group.slug})


class FileIndexView(RequireReadMixin, RedirectView):

    def get_redirect_url(self, **kwargs):
        return reverse('cosinnus:file:list',
                       kwargs={'group': self.group.slug})


class FileCreateView(RequireWriteMixin, FilterGroupMixin, FileFormMixin,
                     CreateView):

    form_class = FileForm
    model = FileEntry
    template_name = 'cosinnus_file/file_form.html'

    def get_object(self, queryset=None):
        return CreateView.get_object(self, queryset=queryset)

    def get_initial(self):
        """
            Supports calling /add under other files,
            which creates a new file under the given file/folder's path
        """
        initial = super(FileCreateView, self).get_initial()

        # if a file is given in the URL, we check if its a folder, and if so, let
        # the user create a file under that path
        # if it is a file, we let the user create a new file on the same level
        if 'slug' in self.kwargs.keys():
            folder = get_object_or_404(FileEntry, slug=self.kwargs.get('slug'))
            initial.update({'path': folder.path})

        # the createfolder view is just a readonly flag that we set here
        if self.kwargs['form_view'] == 'create_folder':
            initial.update({'isfolder': True})

        return initial

    def form_valid(self, form):
        """ Pass the path variable retrieved from the slug file over the non-editable field """
        path = form.initial.get('path', None)
        if path:
            form.instance.path = path
        return super(FileCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(FileCreateView, self).get_context_data(**kwargs)
        tags = FileEntry.objects.tags()
        context.update({
            'tags': tags
        })

        return context


class FileDeleteView(RequireWriteMixin, FilterGroupMixin, DeleteView):

    model = FileEntry
    template_name = 'cosinnus_file/file_delete.html'

    def _getFilesInPath(self, path):
        return FileEntry.objects.filter(path__startswith=path)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.isfolder:
            dellist = list(self._getFilesInPath(self.object.path))
        else:
            dellist = [self.object]

        # for a clean deletion, sort so that subelements are always before their parents and files always before folders on the same level
        dellist.sort(key=lambda o: len(o.path) + (0 if o.isfolder else 1), reverse=True)

        total_files = len(dellist)
        deleted_count = 0
        for fileentry in dellist:
            """ sanity check: only delete a folder if it is empty
                (there should only be one object (the folder itself) with the path, because
                we have deleted all its files before it!
            """
            if fileentry.isfolder:
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
            if delfile.isfolder:
                # special handling for folders being deleted:
                pathfiles = self._getFilesInPath(delfile.path)
                dellist.extend(pathfiles)
            else:
                dellist.append(delfile)

        context['files_to_delete'] = dellist
        return context

    def get_queryset(self):
        qs = super(FileDeleteView, self).get_queryset()
        if self.request.user.is_superuser:
            return qs
        return qs.filter(creator=self.request.user)

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
        return reverse('cosinnus:file:list', kwargs={'group': self.group.slug})


class FileDetailView(RequireReadMixin, FilterGroupMixin, DetailView):

    model = FileEntry
    template_name = 'cosinnus_file/file_detail.html'


def create_file_hierarchy(filelist):
    '''
        Create a node/children tree structure containing files.
        We assume that ALL (!) pathnames end with a '/'
        A folder has a pathname of /path/to/folder/foldername/   (the last path part is the folder itself!)
    '''
    # saves all folder paths that have been created
    folderdict = dict()

    def getOrCreateFolder(path, folderFileEntry, specialname=None):
        if (path in folderdict.keys()):
            folderEnt = folderdict[path]
            # attach the folders file entry if we were passed one
            if folderFileEntry is not None:
                folderEnt['folderfile'] = folderFileEntry
            return folderEnt
        name = specialname if specialname else basename(path[:-1])
        newfolder = defaultdict(dict, (('files', []), ('folders', []), ('name', name), ('path', path), ('folderfile', folderFileEntry),))
        folderdict[path] = newfolder
        if path != '/':
            attachToParentFolder(newfolder)
        return newfolder

    def attachToParentFolder(folder):
        parentpath = dirname(folder['path'][:-1])
        if parentpath[-1] != '/':
            parentpath += '/'
        if parentpath not in folderdict.keys():
            parentfolder = getOrCreateFolder(parentpath, None)
        else:
            parentfolder = folderdict[parentpath]
        parentfolder['folders'].append(folder)

    root = getOrCreateFolder('/', None)
    for fileEnt in filelist:
        if fileEnt.isfolder:
            getOrCreateFolder(fileEnt.path, fileEnt)
        else:
            filesfolder = getOrCreateFolder(fileEnt.path, None)
            filesfolder['files'].append(fileEnt)

    return root


class FileListView(RequireReadMixin, FilterGroupMixin, TaggedListMixin,
                   FormMixin, ListView):

    form_class = FileListForm
    model = FileEntry
    template_name = 'cosinnus_file/file_list.html'

    def get_context_data(self, **kwargs):
        context = super(FileListView, self).get_context_data(**kwargs)

        tree = create_file_hierarchy(context['fileentry_list'])
        context['filetree'] = tree

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


class FileUpdateView(RequireWriteMixin, FilterGroupMixin, FileFormMixin,
                     UpdateView):

    form_class = FileForm
    model = FileEntry
    template_name = 'cosinnus_file/file_form.html'

    def get_context_data(self, **kwargs):
        context = super(FileUpdateView, self).get_context_data(**kwargs)
        tags = FileEntry.objects.tags()
        context.update({
            'tags': tags
        })
        return context


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
