from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin


admin.autodiscover()


urlpatterns = patterns('',
    url(r'^$', 'spec_maker.views.new_spec', name='new_spec'),
    url(r'^tree.json$', 'spec_maker.views.tree_json', name='tree_json'),
    url(r'^git_commit_id.json$', 'spec_maker.views.git_commit_id_json', name='get_commit_id_json'),
    url(r'^check_project_out_of_date.json$', 'spec_maker.views.check_project_out_of_date_json', name='check_project_out_of_date_json'),
    url(r'^spec_list/$', 'spec_maker.views.spec_list', name='spec_list'),
    url(r'^spec_list/edit/(?P<spec_name>\w+)/$', 'spec_maker.views.edit_spec', name='edit_spec'),
    url(r'^specs/$', 'spec_maker.views.specs_action', name='specs_action'),
    url(r'^specs/(?P<spec_name>\w+)$', 'spec_maker.views.spec_nodes', name='spec_nodes'),
    # url(r'^upload_image/$', 'spec_maker.views.upload_image', name='upload_image'),
    url(r'^admin/', include(admin.site.urls)),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
