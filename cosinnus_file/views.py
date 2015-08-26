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
    FilterGroupMixin, GroupFormKwargsMixin, RequireReadWriteHybridMixin)
from cosinnus.views.mixins.tagged import HierarchyTreeMixin, HierarchyPathMixin,\
    HierarchyDeleteMixin
from cosinnus.views.mixins.user import UserFormKwargsMixin

from cosinnus_file.forms import FileForm, FileListForm
from cosinnus_file.models import FileEntry, get_or_create_attachment_folder
from cosinnus.views.mixins.hierarchy import HierarchicalListCreateViewMixin
from cosinnus.views.mixins.filters import CosinnusFilterMixin
from cosinnus_file.filters import FileFilter
from cosinnus.utils.urls import group_aware_reverse
from cosinnus_file.utils.strings import clean_filename
from cosinnus.views.hierarchy import MoveElementView
from django.http.response import HttpResponseNotAllowed
from cosinnus.utils.http import JSONResponse
from cosinnus.core.decorators.views import get_group_for_request
from cosinnus.utils.permissions import check_group_create_objects_access
from django.core.exceptions import PermissionDenied
from cosinnus.utils.functions import clean_single_line_text
from cosinnus.views.attached_object import build_attachment_field_result


import logging
from django.utils.datastructures import MultiValueDict
from django.shortcuts import get_object_or_404
logger = logging.getLogger('cosinnus')


mimetypes.init()


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


class FileHybridListView(RequireReadWriteHybridMixin, HierarchyPathMixin, HierarchicalListCreateViewMixin, 
                             CosinnusFilterMixin, FileFormMixin, CreateView):
    template_name = 'cosinnus_file/file_list.html'
    filterset_class = FileFilter
    
    model = FileEntry
    form_view = 'create'
    form_class = FileForm
    
    message_success = _('File "%(title)s" was uploaded successfully.')
    message_error = _('File "%(title)s" could not be added.')
    
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




class FileDownloadView(RequireReadMixin, FilterGroupMixin, DetailView):
    '''
        Lets the user download a FileEntry file (file is determined by slug),
        while the user never gets to see the server file path.
        Mime type is guessed based on the file
    '''
    model = FileEntry

    def render_to_response(self, context, **response_kwargs):
        response = HttpResponseNotFound()
        
        fileentry = self.object
        path = fileentry.file and fileentry.file.path
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

                
            if content_type not in settings.COSINNUS_FILE_NON_DOWNLOAD_MIMETYPES:
                # To inspect details for the below code, see http://greenbytes.de/tech/tc2231/
                if u'WebKit' in self.request.META['HTTP_USER_AGENT']:
                    # Safari 3.0 and Chrome 2.0 accepts UTF-8 encoded string directly.
                    filename_header = 'filename=%s' % clean_filename(filename)
                elif u'MSIE' in self.request.META['HTTP_USER_AGENT']:
                    # IE does not support internationalized filename at all.
                    # It can only recognize internationalized URL, so we do the trick via routing rules.
                    filename_header = ''
                else:
                    # For others like Firefox, we follow RFC2231 (encoding extension in HTTP headers).
                    filename_header = 'filename*=UTF-8\'\'%s' % clean_filename(filename)
                response['Content-Disposition'] = 'attachment; ' + filename_header
        
        return response
    
    
file_download_view = FileDownloadView.as_view()


class FileMoveElementView(MoveElementView):
    model = FileEntry

move_element_view = FileMoveElementView.as_view()



def file_upload_inline(request, group):
    if not request.is_ajax() or not request.method=='POST':
        return HttpResponseNotAllowed(['POST'])
    
    # resolve group either from the slug, or like the permission group mixin does ist
    # (group type needs to also be used for that=
    group = get_group_for_request(group, request)
    if not group:
        logger.error('No group found when trying to upload a file!', extra={'group_slug': group, 
            'request': request, 'path': request.path})
        return JSONResponse({'error': 'groupnotfound'})
    
    # do permission checking using has_write_access(request.user, group)
    if not check_group_create_objects_access(group, request.user):
        logger.error('Permission error while uploading an attached file directly!', 
             extra={'user': request.user, 'request': request, 'path': request.path, 'group_slug': group})
        return JSONResponse({'error': 'denied'})
    
    # add any other required kwargs (group) and stuff correctly so the form can be saved
    post = request.POST
    post._mutable = True
    post.update({
        'group_id': group.id
    })
    
    
    upload_folder = None
    if 'target_folder' in post:
        upload_folder = get_object_or_404(FileEntry, id=int(post.get('target_folder')))
    if not upload_folder:
        # check if the group has a folder with slug 'uploads' and if not, create one
        upload_folder = get_or_create_attachment_folder(group)
    
    
    result_list = []
    for dict_file in request.FILES.getlist('file'):
        single_file_dict = MultiValueDict({'file': [dict_file]})
        post.update({
            'title': clean_single_line_text(dict_file._name),
        })
        form = FileForm(post, single_file_dict, initial={})
        if form.is_valid():
            form.instance.group = group
            form.instance.creator = request.user
            form.instance.path = upload_folder.path
            form.instance._filesize = form.instance.file.file.size
            form.forms['obj'].instance.no_notification = True # disable spammy notifications
            saved_file = form.save()
            
            # pipe the file into the select2 JSON representation to be displayed as select2 pill 
            pill_id, pill_html = build_attachment_field_result('cosinnus_file.FileEntry', saved_file)
            result_list.append({'text': pill_html, 'id': pill_id})
        else:
            logger.error('Form error while uploading an attached file directly!', 
                 extra={'form.errors': form.errors, 'user': request.user, 'request': request, 
                        'path': request.path, 'group_slug': group})
    
    if result_list:
        if post.get('on_success', None) == 'refresh_page':
            messages.success(request, ungettext('%(count)d File was added successfully.', '%(count)d Files were added successfully.', len(result_list)) % {'count': len(result_list)})
        
        return JSONResponse({'status': 'ok', 'on_success': post.get('on_success', 'add_to_select2'), 'select2_data_list': result_list})
    else:
        return JSONResponse({'status': 'invalid'})

