#!/usr/bin/env python

import os
import fnmatch
import logging
import sys
import subprocess
import shutil
import warnings


SPHINX_TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), '..', 'doc')
OUTPUT_SPEC_PATH = os.path.join(os.path.dirname(__file__), 'specs')
SRC_DIR = 'src'
TOCTREE_INDENT = '   '
logger = logging.getLogger(__name__)


def get_git_commit_id(project_root):
    args = [
        'cat',
        '.git/refs/heads/master'

    ]
    p = subprocess.Popen(
        args,
        cwd=project_root,
        stdout=subprocess.PIPE
    )
    return p.communicate()[0]


def deprecation(message):
    warnings.warn(message, DeprecationWarning, stacklevel=2)


def get_spec_nodes(spec_name):
    path = os.path.join(OUTPUT_SPEC_PATH, spec_name, 'nodes')
    with open(path, 'r') as f:
        node_str = f.readline().rstrip('\n')
        nodes = node_str.split(' ')
    return nodes


def write_file(location, f):
    logger.debug('Upload file: ' + f.name)
    file_path = os.path.join(location, f.name)
    try:
        with open(file_path, "w") as dest:
            for chunk in f.chunks():
                dest.write(chunk)
    except:
        raise


def _init_node(data):
    state = {
        'opened': False,
        'selected': False,
    }
    node = {
        'children': [],
        'state': state,
        'id': data,
        'text': data,
    }
    return node


def _set_node_id_and_text(node, data):
    node['id'] = data
    node['text'] = data


def _attach_child_to_node(node_ptr, child_node):
    node_ptr['children'].append(child_node)


def _is_top_level_in_tree(node_ptr):
    return node_ptr['id'] == SRC_DIR


def _find_node_in_map(node_map, key):
    return node_map[key]


def _insert_node_into_map(node_map, key, value):
    node_map[key] = value


def _init_and_attach_child(node_ptr, data):
    child_node = _init_node(data)
    _attach_child_to_node(node_ptr, child_node)
    return child_node


def get_spec_template_tree():
    tree = _init_node(SRC_DIR)
    node_ptr = tree
    node_map = {}
    _insert_node_into_map(node_map, SRC_DIR, tree)
    for root, dirs, files in os.walk(os.path.join(SPHINX_TEMPLATE_PATH, SRC_DIR)):
        logger.debug(root)
        current_dir = root.split(os.sep)[-1]

        if current_dir == 'images':
            continue

        iNodes = dirs + files
        iNodes.sort()
        node_ptr = _find_node_in_map(node_map, current_dir)
        assert node_ptr is not None

        for child_name in iNodes:
            if os.path.isdir(root + os.sep + child_name) and child_name != 'images':
                child_node = _init_and_attach_child(node_ptr, child_name)
                _insert_node_into_map(node_map, child_name, child_node)
            if child_name.endswith('.md'):
                # Use rst instead of md here
                # So we receive file name endwith rst
                # and can be directly used for making pdf later
                _child_name = child_name.replace('.md', '.rst')
                _init_and_attach_child(node_ptr, _child_name)

    return tree


def _init_node_advance(data):
    node = _init_node(data)
    # check if the node is inserted into checked_nodes
    node['checked_ids'] = set()
    node['checked_nodes'] = []
    node['parent'] = node
    return node


def _init_and_attach_child_advance(node_ptr, data):
    child_node = _init_node_advance(data)
    _attach_child_to_node(node_ptr, child_node)
    child_node['parent'] = node_ptr
    return child_node


def _recursive_add_checked_nodes(node):
    node_ptr = node
    while node_ptr['parent'] != node_ptr \
            and node_ptr['id'] not in node_ptr['parent']['checked_ids']:
        node_ptr['parent']['checked_ids'].add(node_ptr['id'])
        node_ptr['parent']['checked_nodes'].append(node_ptr)
        node_ptr = node_ptr['parent']


def _get_dir_tree_advance(file_names, spec_path):
    tree = _init_node_advance(SRC_DIR)
    tree['root'] = spec_path
    node_ptr = tree
    node_map = {
        SRC_DIR: tree
    }
    for root, dirs, files in os.walk(os.path.join(spec_path, SRC_DIR)):
        logger.debug(root)
        dirs.sort()
        files.sort()
        current_dir = root.split(os.sep)[-1]
        node_ptr = _find_node_in_map(node_map, current_dir)
        assert node_ptr is not None
        for child_name in fnmatch.filter(dirs, '*'):
            child_node = _init_and_attach_child_advance(node_ptr, child_name)
            child_node['root'] = root
            _insert_node_into_map(node_map, child_name, child_node)
        for child_name in fnmatch.filter(files, '*.rst'):
            child_node = _init_and_attach_child_advance(node_ptr, child_name)
            # For the checked rst item to be easily found in the tree
            _insert_node_into_map(node_map, child_name, child_node)

    for file_name in file_names:
        node_ptr = _find_node_in_map(node_map, file_name)
        _recursive_add_checked_nodes(node_ptr)

    return tree


def _write_header(f, node_id):
    # TODO: Use a dict to get the title
    title = 'Contents' if node_id == SRC_DIR else 'AAA'
    f.write(title + '\n')
    for i in range(len(title)):
        f.write('=')
    f.write('\n\n.. toctree::\n' + TOCTREE_INDENT + ':maxdepth: 2\n\n')


def _write_content(f, node_dir, nodes):
    for node in nodes:
        included_index_file_path = os.path.join(node_dir, node['id'])
        if not included_index_file_path.endswith('.rst'):
            included_index_file_path += '.rst'
        f.write(TOCTREE_INDENT + included_index_file_path + '\n')


def _write_footer(f):
    footer = '''

==================
Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
'''
    f.write(footer)


def _push_folder_nodes_to_stack(node_stack, nodes):
    for node in nodes:
        # We don't need to make index files on leaf nodes
        if not node['id'].endswith('.rst'):
            node_stack.append(node)


def _create_index_file(index_file_name, node_ptr, has_foot):
    node_root = node_ptr['root']
    node_id = node_ptr['id']
    logger.debug('id: ' + node_id + ', ' + 'root: ' + node_root)
    index_file_path = os.path.join(node_root, index_file_name + '.rst')
    logger.debug('index file path: ' + index_file_path)
    with open(index_file_path, 'w') as f:
        _write_header(f, node_id)
        _write_content(f, node_id, node_ptr['checked_nodes'])
        if has_foot:
            _write_footer(f)


def _create_index_files(tree):
    node_ptr = tree
    node_stack = []

    _create_index_file('index', node_ptr, has_foot=True)
    _push_folder_nodes_to_stack(node_stack, node_ptr['checked_nodes'])

    while len(node_stack) != 0:
        node_ptr = node_stack.pop()
        _create_index_file(node_ptr['id'], node_ptr, has_foot=False)
        _push_folder_nodes_to_stack(node_stack, node_ptr['checked_nodes'])


def _make_empty_spec(spec_name):
    spec_path = os.path.join(OUTPUT_SPEC_PATH, spec_name)
    if os.path.exists(spec_path):
        shutil.rmtree(spec_path)
        logger.warning('{0} already exists, remove it'.format(spec_path))
    try:
        shutil.copytree(SPHINX_TEMPLATE_PATH, spec_path)
    except OSError as e:
        logger.error(e)
        raise
    return spec_path


def _save_nodes_to_file(nodes, spec_path):
    with open(os.path.join(spec_path, 'nodes'), 'w') as f:
        f.write(' '.join(nodes) + '\n')


def _customize_conf_py(spec_path, spec_name):
    args = [
        'sed',
        '-i',
        '-e',
        '/project_name =/ s/= .*/= u"{0}"/'.format(spec_name),
        'conf.py',
    ]
    p = subprocess.Popen(
        args,
        cwd=spec_path,
        stdout=subprocess.PIPE
    )
    p.communicate()
    status = p.returncode
    logger.debug('Customize conf.py project_name: ' + str(status))
    if status != 0:
        raise Exception('Customize conf.py project_name: failed')

    args = [
        'sed',
        '-i',
        '-e',
        '/project_file_name =/ s/= .*/= "{0}"/'.format(spec_name),
        'conf.py',
    ]
    p = subprocess.Popen(
        args,
        cwd=spec_path,
        stdout=subprocess.PIPE
    )
    p.communicate()
    status = p.returncode
    logger.debug('Customize conf.py project_file_name: ' + str(status))
    if status != 0:
        raise Exception('Customize conf.py project_file_name: failed')


def _filter_text_files(nodes):
    return [f for f in nodes if f.endswith('.rst')]


def _make_latexpdf(spec_path):
    args = [
        'make',
        'latexpdf',
    ]
    p = subprocess.Popen(
        args,
        cwd=spec_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    (output, e) = p.communicate()
    status = p.returncode
    logger.debug('cmd: ' + ' '.join(args))
    logger.debug('status: ' + str(status) + ', output: ' + output + ', error: ' + e)
    return status


def _make_html(spec_path):
    args = [
        'make',
        'html',
    ]
    p = subprocess.Popen(
        args,
        cwd=spec_path,
        stdout=subprocess.PIPE
    )
    output = p.communicate()[0]
    status = p.returncode
    logger.debug('cmd: ' + ' '.join(args))
    logger.debug('status: ' + str(status) + ', output: ' + output)
    return status


def _change_markdown_to_rst(spec_path):
    for root, dirs, files in os.walk(os.path.join(spec_path, SRC_DIR)):
        for child_name in fnmatch.filter(files, '*.md'):
            logger.debug(child_name)
            target_name = child_name.replace('.md', '.rst')
            pandoc_cmd = [
                'pandoc',
                '--from=markdown',
                '--to=rst',
            ]
            output_file = '--output=' + target_name
            pandoc_cmd.append(output_file)
            pandoc_cmd.append(child_name)
            p = subprocess.Popen(
                pandoc_cmd,
                cwd=root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            (output, e) = p.communicate()
            status = p.returncode
            logger.debug('status: ' + str(status) + ', output: ' + output + ', error: ' + e)


def _copy_spec_to_media_dir(spec_path, spec_name):
    from django.conf import settings
    src_pdf_path = os.path.join(spec_path, spec_path, 'build', 'latex', spec_name + '.pdf')
    spec_dir_path = os.path.join(settings.MEDIA_ROOT, 'specs', spec_name)
    if not os.path.exists(spec_dir_path):
        os.mkdir(spec_dir_path)
    target_pdf_path = os.path.join(spec_dir_path, spec_name + '.pdf')

    try:
        shutil.copyfile(src_pdf_path, target_pdf_path)
    except IOError:
        logger.error('Copy {0} to {1} failed'.format(src_pdf_path, target_pdf_path))
        raise

    src_html_path = os.path.join(spec_path, spec_path, 'build', 'html')
    target_html_path = os.path.join(spec_dir_path, 'html')

    if os.path.exists(target_html_path):
        shutil.rmtree(target_html_path)
        logger.warning('{0} already exists, remove it'.format(target_html_path))
    try:
        shutil.copytree(src_html_path, target_html_path)
    except shutil.Error:
        logger.error('Copy {0} to {1} failed'.format(src_html_path, target_html_path))
        raise


def make_spec(spec_name, nodes):
    try:
        spec_path = _make_empty_spec(spec_name)
    except OSError:
        raise

    _save_nodes_to_file(nodes, spec_path)

    try:
        _customize_conf_py(spec_path, spec_name)
    except Exception:
        raise

    file_names = _filter_text_files(nodes)
    _change_markdown_to_rst(spec_path)
    tree = _get_dir_tree_advance(file_names, spec_path)
    _create_index_files(tree)
    # logger.debug(tree)
    _make_latexpdf(spec_path)
    _make_html(spec_path)

    try:
        _copy_spec_to_media_dir(spec_path, spec_name)
    except (IOError, shutil.Error):
        logger.error('Copy {0} failed'.format(spec_name))
        raise


def get_all_specs():
    return [f for f in os.listdir(OUTPUT_SPEC_PATH)
            if os.path.isdir(os.path.join(OUTPUT_SPEC_PATH, f))]


def rebuild_spec(spec_names):
    for spec_name in spec_names:
        spec_path = os.path.join(OUTPUT_SPEC_PATH, spec_name)
        _make_latexpdf(spec_path)
        _make_html(spec_path)
        try:
            _copy_spec_to_media_dir(spec_path, spec_name)
        except (IOError, shutil.Error):
            logger.error('Copy {0} failed'.format(spec_name))
            raise


def _delete_spec_from_media_dir(spec_name):
    from django.conf import settings
    shutil.rmtree(os.path.join(settings.MEDIA_ROOT, 'specs', spec_name))


def delete_spec(spec_names):
    for spec_name in spec_names:
        spec_path = os.path.join(OUTPUT_SPEC_PATH, spec_name)
        shutil.rmtree(spec_path)
        _delete_spec_from_media_dir(spec_name)


if __name__ == '__main__':
    formatter = logging.Formatter('[%(levelname)s](%(funcName)s/%(lineno)d): %(message)s')
    console = logging.StreamHandler(stream=sys.stdout)
    console.setLevel(logging.DEBUG)
    console.setFormatter(formatter)
    logger.addHandler(console)
    logger.setLevel(logging.DEBUG)

    # tree = get_spec_template_tree()
    # import json
    # print(json.dumps(tree['children'], indent=4))
    _change_markdown_to_rst('./specs/123')
