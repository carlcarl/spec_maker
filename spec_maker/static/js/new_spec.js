/*jslint browser:true */
/*jslint es5: true */
/*jslint nomen: true */
/*global $, jQuery, alert, console, log, _, Ladda*/

$(function () {
    'use strict';

    $.getJSON(
        'tree.json',
        function (data) {
			console.log('Request spec template completed');
            // console.log(data);
            $('#jstree-block').jstree({
                'core': {
                    'data': [
                        data,
                    ],
                    // 'themes': {
                    //     'name': 'default',
                    //     'responsive': true
                    // }
                },
                'plugins': ['checkbox'],
                'checkbox': {
                    'keep_selected_style': false,
                },
            });
        }
    );

    $.getJSON(
        'specs/',
        function (data) {
			console.log('Request spec list completed');
			var i, len, specTemplate, $specBox;
			$specBox = $('#spec-box');
			if (data.specs === 'undefined') {
				alert('Response format is wrong!');
				return -1;
			}
            // console.log(data);
			for (i = 0, len = data.specs.length; i < len; i += 1) {
				specTemplate = _.template(
					$('#spec-template').html(),
					{
						'projectName': data.specs[i]
					}
				);
				$specBox.append(specTemplate);
			}
        }
    );

	$('#spec-modal-import').click(function () {
		var url, specName;
		specName = $('input[name="specOptions"]:checked').val();
		url = encodeURI('specs/' + specName);
		console.log('Request spec template: ' + specName);
		$.getJSON(
			url,
			function (data) {
				console.log('Request the specified spec nodes completed');
				console.log(data);
				var i, len;
				if (data.nodes === 'undefined') {
					alert('Response format is wrong!');
					return -1;
				}
				for (i = 0, len = data.nodes.length; i < len; i += 1) {
					// TODO: Check node exists
					$('#jstree-block').jstree(
						'check_node',
						'#' + data.nodes[i]
					);
				}
				$('#spec-name').val(specName);
			}
		);
	});

	$('#import-tree').click(function (evt) {
		evt.preventDefault();
		$('#specModal').modal();
	});

    $('#submit-tree').click(function (evt) {
        evt.preventDefault();

        var checkedList, specName, postStr, i, len, count, ladda;

        specName = $('#spec-name').val();
        console.log('You want to create spec: ' + specName);
        if (specName === '') {
            alert('Project name is empty!');
            return false;
        }
        postStr = '';
        checkedList = $('#jstree-block').jstree(
            'get_checked',
            null,
            true
        );

        count = 0;
        for (i = 0, len = checkedList.length; i < len; i += 1) {
			if (count !== 0) {
				postStr += ' ';
			}
			postStr += checkedList[i];
			count += 1;
        }
        console.log('post str: ' + postStr);

		ladda = Ladda.create(this);
		ladda.start();
		console.log('Submit spec tree');
        $.post(
            'specs/',
            {
                spec_name: specName,
                node_str: postStr,
            },
            function (data) {
				console.log('Submit spec tree completed');
				ladda.stop();
                if (data.error === undefined) {
                    alert('The response format is wrong!');
                    return -1;
                }
                if (data.error === 0) {
                    alert('The spec is created successfully!');
                } else {
                    alert('The spec is failed!');
                }
            }
        );
        return false;
    });
});
// vim: set tabstop=4 noexpandtab shiftwidth=4 softtabstop=4:
