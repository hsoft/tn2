var tn2_project_edit = {
    setup: function() {
        tn2_project_edit.bind_pattern_selectors();
    },

    pattern_selector: function() {
        return document.querySelector('select[name="pattern"]');
    },

    creator_selector: function() {
        var pattern_selector = tn2_project_edit.pattern_selector();
        var creator_select_id = pattern_selector.getAttribute('data-prefix-id');
        return document.querySelector('select#' + creator_select_id);
    },

    enable_freeform_pattern_fields: function(enabled) {
        var names = ['category', 'pattern_name', 'pattern_url'];
        $.each(names, function(index, value) {
            $('*[name="' + value + '"]').prop('disabled', !enabled);
        });
    },

    update_pattern_select: function() {
        var $pattern_selector = $(tn2_project_edit.pattern_selector());
        var $creator_selector = $(tn2_project_edit.creator_selector());
        var creator_id = $creator_selector.val();
        var pattern_id = $pattern_selector.val();
        $pattern_selector.html('');
        $pattern_selector.change();
        $pattern_selector.prop('disabled', true);
        tn2_project_edit.enable_freeform_pattern_fields(creator_id == 0);
        if (creator_id > 0) {
            $.ajax({
                url: '/ajax/patterns/' + creator_id + '/',
                dataType: 'json',
            }).done(function (data) {
                $.each(data.objects, function (index, value) {
                    var $option = $('<option/>')
                        .prop('value', value[0])
                        .text(value[1]);
                    $pattern_selector.append($option);
                });
                $pattern_selector.change();
                $pattern_selector.prop('disabled', false);
                $pattern_selector.val(pattern_id);
            });
        } else {
            var $option = $('<option/>')
                .prop('value', 0)
                .text("Patron non répertorié");
            $pattern_selector.append($option);
            $pattern_selector.change();
        }
    },

    bind_pattern_selectors: function() {
        var pattern_selector = tn2_project_edit.pattern_selector();
        var creator_selector = tn2_project_edit.creator_selector();
        $(creator_selector).select2();
        $(creator_selector).on('select2:select', tn2_project_edit.update_pattern_select);
        $(pattern_selector).select2();
        tn2_project_edit.update_pattern_select();
    }
}

document.addEventListener('DOMContentLoaded', tn2_project_edit.setup);

