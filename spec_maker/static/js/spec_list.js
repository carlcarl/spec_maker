/*jslint browser:true */
/*jslint es5: true */
/*jslint nomen: true */
/*global $, jQuery, alert, console, log, _, Ladda*/

$(function () {
    'use strict';

    $('#spec-select-all').on('change', function () {
        var checked, i, len, $specSelect;
        checked = $('#spec-select-all').prop('checked');
        $specSelect = $('input[name="spec-select"]');
        for (i = 0, len = $specSelect.length; i < len; i += 1) {
            $specSelect[i].checked = checked;
        }
    });

    $('#filter-field').on('keyup', function () {
        var mSearch, filterField;
        mSearch = $("#m-search");
        filterField = $('#filter-field').val();
        if (!filterField) {
            mSearch.html('');
        } else {
            mSearch.html('.search-row:not([data-index*="' + filterField + '"]) {display: none;}');

        }
    });


    function getSelectedNodesAndAjax(action, ajaxCallback) {
        var data, specs, $specSelectChecked, i, len, ladda;
        $specSelectChecked = $('input[name="spec-select"]').filter(':checked');
        specs = [];
        for (i = 0, len = $specSelectChecked.length; i < len; i += 1) {
            specs.push($specSelectChecked[i].value);
        }
        if (specs.length === 0) {
            alert('Choose one of the following items');
            return;
        }
        data = {
            action: action,
            specs: specs
        };
        console.log(data);

        if (action === 'rebuild') {
            $('#delete').prop('disabled', true);
        } else if (action === 'delete') {
            $('#rebuild').prop('disabled', true);
        }
        ladda = Ladda.create($('#' + action)[0]);
        ladda.start();

        $.ajax({
            url: '/specs/',
            type: 'POST',
            contentType: 'application/json; charset=utf-8',
            data: JSON.stringify(data),
            dataType: 'json',
            success: ajaxCallback,
            complete: function (jqXHR, textStatus) {
                console.log(jqXHR);
                console.log(textStatus);
                if (action === 'rebuild') {
                    $('#delete').prop('disabled', false);
                } else if (action === 'delete') {
                    $('#rebuild').prop('disabled', false);
                }
                ladda.stop();
            },
        });
    }


    $('#rebuild').click(function () {
        getSelectedNodesAndAjax('rebuild', function (result) {
            console.log('Rebuild spec trees completed');
            if (result.error === undefined) {
                alert('The response format is wrong!');
                return -1;
            }
            if (result.error === 0) {
                alert('The specs are rebuilt successfully!');
            } else {
                alert('The spec rebuild is failed!');
            }
        });
    });


    $('#delete').click(function () {
        getSelectedNodesAndAjax('delete', function (result) {
            console.log('Delete specs completed');
            if (result.error === undefined) {
                alert('The response format is wrong!');
                return -1;
            }
            if (result.error === 0) {
                alert('The specs are deleted successfully!');
            } else {
                alert('The specs deletion is failed: ' + result.message);
            }
            location.reload();
        });
    });
});
