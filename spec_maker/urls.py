from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin


admin.autodiscover()


urlpatterns = patterns('',
    url(r'^$', 'spec_maker.views.new_spec', name='new_spec'),
    url(r'^tree.json$', 'spec_maker.views.tree_json', name='tree_json'),
    url(r'^spec_list/$', 'spec_maker.views.spec_list', name='spec_list'),
    url(r'^specs/$', 'spec_maker.views.specs', name='specs'),
    url(r'^specs/(?P<spec_name>\w+)$', 'spec_maker.views.spec', name='spec'),
    # url(r'^upload_image/$', 'spec_maker.views.upload_image', name='upload_image'),
    url(r'^admin/', include(admin.site.urls)),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
