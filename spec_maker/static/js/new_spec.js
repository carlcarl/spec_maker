/*jslint browser:true */
/*jslint es5: true */
/*jslint nomen: true */
/*global $, jQuery, alert, console, log, _, Ladda*/

$(function () {
    'use strict';

	// When ladda start and doesn't call stop in some situations,
	// buttons will be in disabled even we refresh the page,
	// so just call stopAll at beginning as a workaround
	Ladda.stopAll();

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
			for (i = 0, len = data.specs.length; i < len; i += 1) {
				specTemplate = _.template(
					$('#spec-template').html()
				)({
					'projectName': data.specs[i]
				});
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
				var i, len, unfoundElements, treeNode, nodeId,
					messageTemplate;
				if (data.nodes === 'undefined') {
					alert('Response format is wrong!');
					return -1;
				}
				unfoundElements = [];
				for (i = 0, len = data.nodes.length; i < len; i += 1) {
					nodeId = '#' + data.nodes[i];
					treeNode = $('#jstree-block').jstree(
						'get_node',
						nodeId
					);
					if (!treeNode) {
						unfoundElements.push('#' + data.nodes[i]);
					}
					$('#jstree-block').jstree(
						'check_node',
						nodeId
					);
				}
				if (unfoundElements.length) {
					messageTemplate = _.template(
						$('#message-template').html()
					)({
						'alertClass': 'alert-danger',
						'message': unfoundElements.join(' and ') + ' not found!'
					});
					$('#message-box').html(messageTemplate);
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

        var checkedList, specName, ladda, data;

        specName = $('#spec-name').val();
        console.log('You want to create spec: ' + specName);
        if (specName === '') {
            alert('Project name is empty!');
            return false;
        }
        checkedList = $('#jstree-block').jstree(
            'get_checked',
            null,
            true
        );

		data = {
			action: 'create',
			spec: specName,
			nodes: checkedList,
		};

		ladda = Ladda.create(this);
		ladda.start();
		console.log('Submit spec tree');
		$.ajax({
			url: '/specs/',
			type: 'POST',
			contentType: 'application/json; charset=utf-8',
			data: JSON.stringify(data),
			dataType: 'json',
			success: function (result) {
				console.log('Submit spec tree completed');
                if (result.error === undefined) {
                    alert('The response format is wrong!');
                    return -1;
                }
                if (result.error === 0) {
                    alert('The spec is created successfully!');
                } else {
                    alert('The spec is failed!');
                }
			},
			complete: function (jqXHR, textStatus) {
				console.log(jqXHR);
				console.log(textStatus);
				ladda.stop();
			},
		});
        return false;
    });
});
// vim: set tabstop=4 noexpandtab shiftwidth=4 softtabstop=4:
