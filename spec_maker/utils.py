#!/usr/bin/env python
import os
import fnmatch
import json
import logging
import sys
import subprocess
import shutil
import warnings


SPHINX_TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), 'doc')
OUTPUT_SPEC_PATH = SPHINX_TEMPLATE_PATH + os.sep + '..' + os.sep + 'specs'
RST_DIR = 'rst'
TOCTREE_INDENT = '   '
logger = logging.getLogger(__name__)


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
    return node_ptr['id'] == RST_DIR


def _find_node_in_map(node_map, key):
    return node_map[key]


def _insert_node_into_map(node_map, key, value):
    node_map[key] = value


def _init_and_attach_child(node_ptr, data):
    child_node = _init_node(data)
    _attach_child_to_node(node_ptr, child_node)
    return child_node


def get_dir_tree():
    tree = _init_node(RST_DIR)
    node_ptr = tree
    node_map = {}
    _insert_node_into_map(node_map, RST_DIR, tree)
    for root, dirs, files in os.walk(os.path.join(SPHINX_TEMPLATE_PATH, RST_DIR)):
        logger.debug(root)
        dirs.sort()
        files.sort()
        current_dir = root.split(os.sep)[-1]
        node_ptr = _find_node_in_map(node_map, current_dir)
        assert node_ptr is not None
        for child_name in fnmatch.filter(dirs, '*'):
            child_node = _init_and_attach_child(node_ptr, child_name)
            _insert_node_into_map(node_map, child_name, child_node)
        for child_name in fnmatch.filter(files, '*'):
            _init_and_attach_child(node_ptr, child_name)
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
    tree = _init_node_advance(RST_DIR)
    tree['root'] = spec_path
    node_ptr = tree
    node_map = {
        RST_DIR: tree
    }
    for root, dirs, files in os.walk(os.path.join(spec_path, RST_DIR)):
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
        for child_name in fnmatch.filter(files, '*'):
            child_node = _init_and_attach_child_advance(node_ptr, child_name)
            # For the checked rst item to be easily found in the tree
            _insert_node_into_map(node_map, child_name, child_node)

    for file_name in file_names:
        node_ptr = _find_node_in_map(node_map, file_name)
        _recursive_add_checked_nodes(node_ptr)

    return tree


def _write_header(f, node_id):
    # TODO: Use a dict to get the title
    title = 'Contents' if node_id == RST_DIR else 'AAA'
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


def _make_index_file(index_file_name, node_ptr, has_foot):
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


def _make_index_files(tree):
    node_ptr = tree
    node_stack = []

    _make_index_file('index', node_ptr, has_foot=True)
    _push_folder_nodes_to_stack(node_stack, node_ptr['checked_nodes'])

    while len(node_stack) != 0:
        node_ptr = node_stack.pop()
        _make_index_file(node_ptr['id'], node_ptr, has_foot=False)
        _push_folder_nodes_to_stack(node_stack, node_ptr['checked_nodes'])


def _make_empty_spec(spec_name):
    spec_path = os.path.join(OUTPUT_SPEC_PATH, spec_name)
    try:
        shutil.copytree(SPHINX_TEMPLATE_PATH, spec_path)
    except OSError as e:
        logger.error(e)
        raise
    return spec_path


def _save_nodes(nodes, spec_path):
    with open(os.path.join(spec_path, 'nodes'), 'w') as f:
        f.write(' '.join(nodes) + '\n')


def _filter_text_files(nodes):
    return [f for f in nodes if f.endswith('.rst')]


def _make_latexpdf(spec_path):
    logger.debug(spec_path)
    args = [
        'make',
        'latexpdf',
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


def make_spec(spec_name, nodes):
    try:
        spec_path = _make_empty_spec(spec_name)
    except OSError:
        raise
    _save_nodes(nodes, spec_path)
    file_names = _filter_text_files(nodes)
    tree = _get_dir_tree_advance(file_names, spec_path)
    _make_index_files(tree)
    # logger.debug(tree)
    _make_latexpdf(spec_path)


def get_all_specs():
    return [f for f in os.listdir(OUTPUT_SPEC_PATH)
            if os.path.isdir(os.path.join(OUTPUT_SPEC_PATH, f))]


if __name__ == '__main__':
    formatter = logging.Formatter('[%(levelname)s](%(funcName)s/%(lineno)d): %(message)s')
    console = logging.StreamHandler(stream=sys.stdout)
    console.setLevel(logging.DEBUG)
    console.setFormatter(formatter)
    logger.addHandler(console)
    logger.setLevel(logging.DEBUG)

    tree = get_dir_tree()
    print(json.dumps(tree['children'], indent=4))
