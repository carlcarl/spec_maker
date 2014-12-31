#!/usr/bin/env python
# encoding: utf-8

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
import json
import logging
import os
from spec_maker.utils import get_all_specs
from spec_maker.utils import get_dir_tree
from spec_maker.utils import get_spec_nodes
from spec_maker.utils import make_spec
from spec_maker.utils import write_file
from spec_maker.utils import deprecation
# from django.contrib.auth.decorators import login_required

logger = logging.getLogger(__name__)


@ensure_csrf_cookie
def new_spec(request):
    return render(request, 'spec_maker/new_spec.html')


def tree_json(request):
    dir_tree = get_dir_tree()
    return HttpResponse(json.dumps(dir_tree), content_type='application/json')


def spec_list(request):
    specs = get_all_specs()
    return render(request, 'spec_maker/spec_list.html', {'specs': specs})


def specs(request):
    response = {
        'error': 0,
        'message': '',
    }
    if request.method == 'GET':
        specs = get_all_specs()
        response['specs'] = specs
    elif request.method == 'POST':
        spec_name = request.POST.get('spec_name')
        node_str = request.POST.get('node_str')
        logger.debug('node_str: ' + node_str)
        node_list = node_str.split(' ')
        try:
            make_spec(spec_name, node_list)
        except OSError as e:
            response['error'] = 1
            response['message'] = str(e)
    else:
        response['error'] = 1
        response['message'] = 'Unknown HTTP method: ' + request.method

    return HttpResponse(json.dumps(response), content_type='application/json')


def spec(request, spec_name):
    response = {
        'error': 0,
    }
    node_list = get_spec_nodes(spec_name)
    response['nodes'] = node_list
    return HttpResponse(json.dumps(response), content_type='application/json')


def _get_image_prefix_url(is_secure, http_host, media_url):
    protocol = 'https' if is_secure else 'http'
    return (
        protocol + '://' + http_host +
        media_url + 'images/'
    )


@ensure_csrf_cookie
def upload_image(request):
    deprecation('Upload images function is no longer for use')
    response = {
        'error': 0,
        'message': '',
        'image_url': '',
    }
    if request.method == 'GET':
        return render(request, 'spec_maker/upload_image.html')
    elif request.method == 'POST':
        location = os.path.join(settings.MEDIA_ROOT, 'images')
        file_name = request.FILES['file'].name
        if os.path.exists(
            os.path.join(
                location,
                request.FILES['file'].name
            )
        ):
            response['error'] = 2
            response['message'] = file_name + ' already exists'
            return HttpResponse(json.dumps(response), content_type='application/json')

        try:
            image_prefix_url = _get_image_prefix_url(
                request.is_secure(),
                request.META['HTTP_HOST'],
                settings.MEDIA_URL
            )
            write_file(
                location,
                request.FILES['file']
            )
        except Exception as e:
            logger.error(str(e))
            response['error'] = 1
            response['message'] = file_name + ' upload failed: ' + str(e)
        else:
            response['image_url'] = image_prefix_url + file_name
            response['message'] = (
                'Your link: <a href="{image_url}">'
                '{image_url}</a>'.format(image_url=response['image_url'])
            )
        return HttpResponse(json.dumps(response), content_type='application/json')
    else:
        return HttpResponse(json.dumps(response), content_type='application/json')
