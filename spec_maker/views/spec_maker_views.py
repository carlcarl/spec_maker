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
from spec_maker.utils import get_spec_template_tree
from spec_maker.utils import get_spec_nodes
from spec_maker.utils import make_spec
from spec_maker.utils import rebuild_spec
from spec_maker.utils import delete_spec
from spec_maker.utils import write_file
from spec_maker.utils import deprecation
# from django.contrib.auth.decorators import login_required

logger = logging.getLogger(__name__)


@ensure_csrf_cookie
def new_spec(request):
    return render(request, 'spec_maker/new_spec.html')


def tree_json(request):
    spec_template_tree = get_spec_template_tree()
    return HttpResponse(json.dumps(spec_template_tree), content_type='application/json')


def spec_list(request):
    specs = get_all_specs()
    return render(request, 'spec_maker/spec_list.html', {'specs': specs})


def edit_spec(request, spec_name):
    return render(request, 'spec_maker/edit_spec.html', {'spec_name': spec_name})


def _spec_action(post_json, response):
    action = post_json['action']
    if action == 'create':
        spec_name = post_json['spec']
        nodes = post_json['nodes']
        try:
            make_spec(spec_name, nodes)
        except Exception as e:
            response['error'] = 1
            response['message'] = str(e)
            delete_spec([spec_name])
    elif action == 'rebuild':
        specs = post_json['specs']
        try:
            rebuild_spec(specs)
        except OSError as e:
            response['error'] = 1
            response['message'] = str(e)
    elif action == 'delete':
        specs = post_json['specs']
        try:
            delete_spec(specs)
        except OSError as e:
            response['error'] = 1
            response['message'] = str(e)
    else:
        response['error'] = 1
        response['message'] = 'Unknown action: ' + action

    return response


def specs_action(request):
    response = {
        'error': 0,
        'message': '',
    }
    if request.method == 'GET':
        specs = get_all_specs()
        response['specs'] = specs
    elif request.method == 'POST':
        post_json = json.loads(request.body)
        response = _spec_action(post_json, response)
    else:
        response['error'] = 1
        response['message'] = 'Unknown HTTP method: ' + request.method

    return HttpResponse(json.dumps(response), content_type='application/json')


def spec_nodes(request, spec_name):
    response = {
        'error': 0,
    }
    nodes = get_spec_nodes(spec_name)
    response['nodes'] = nodes
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
