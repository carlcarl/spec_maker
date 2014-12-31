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
});
