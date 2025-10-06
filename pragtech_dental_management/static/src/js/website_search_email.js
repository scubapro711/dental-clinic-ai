/** @odoo-module **/

import { registry } from "@web/core/registry";
import { session } from "@web/session";

$(document).ready(function () {
    $('#search_patient_btn').on('click', function () {
        const email = $('#email').val().trim();
        if (!email) {
            alert("Please enter an email.");
            return;
        }

        $.ajax({
            url: '/search_patient_by_email',
            type: 'POST',
            data: JSON.stringify({ jsonrpc: "2.0", method: "call", params: { email: email } }),
            contentType: 'application/json',
            success: function (result) {
                if (result.result && result.result.name) {
                    $('#patient_name').val(result.result.name);
                    $('#patient_id').val(result.result.id);
                } else {
                    alert('Patient not found with this email.');
                    $('#patient_name').val('');
                }
            },
            error: function () {
                alert('Error occurred while searching patient.');
            }
        });
    });
});