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
        var names = ['pattern_name', 'pattern_url'];
        $.each(names, function(index, value) {
            $('*[name="' + value + '"]').prop('disabled', !enabled);
        });
    },

    update_pattern_select: function(selected_creator_id) {
        var $pattern_selector = $(tn2_project_edit.pattern_selector());
        var $creator_selector = $(tn2_project_edit.creator_selector());
        var pattern_id = $pattern_selector.val();
        $pattern_selector.html('');
        $pattern_selector.change();
        $pattern_selector.prop('disabled', true);
        tn2_project_edit.enable_freeform_pattern_fields(selected_creator_id == 0);
        if (selected_creator_id > 0) {
            $.ajax({
                url: '/ajax/patterns/' + selected_creator_id + '/',
                dataType: 'json',
            }).done(function (data) {
                var $selected_option = null;
                $pattern_selector.prop('disabled', false);
                $.each(data.objects, function (index, value) {
                    var $option = $('<option/>')
                        .prop('value', value[0])
                        .attr('data-target', value[2])
                        .attr('data-domain', value[3])
                        .attr('data-category', value[4])
                        .text(value[1]);
                    if ((index == 0) || (value[0] == pattern_id)) {
                        $selected_option = $option;
                    }
                    $pattern_selector.append($option);
                });
                $selected_option.prop('selected', true);
                $pattern_selector.change();
                tn2_project_edit.update_category_selector($selected_option);
            });
        } else {
            var $option = $('<option/>')
                .prop('value', 0)
                .text("Patron non répertorié");
            $pattern_selector.append($option);
            $pattern_selector.change();
        }
    },

    update_category_selector: function($selected_opt) {
        /* We only want to do this category-fiddling-on-pattern-selection on **new** projects.
         * We don't want to mess with an existing project's categories, which were already set
         * before.
         */
        console.log(document.querySelector('form.newproject'));
        if (!document.querySelector('form.newproject')) {
            return;
        }
        var target = $selected_opt.attr('data-target');
        var domain = $selected_opt.attr('data-domain');
        var category = $selected_opt.attr('data-category');
        $('select[name="target"]').val(target);
        $('select[name="domain"]').val(domain);
        $('select[name="category"]').val(category);
    },

    bind_pattern_selectors: function() {
        var pattern_selector = tn2_project_edit.pattern_selector();
        var creator_selector = tn2_project_edit.creator_selector();
        $(creator_selector).select2();
        $(creator_selector).on('select2:select', function(e) {
            tn2_project_edit.update_pattern_select(e.params.data.id);
        });
        $(pattern_selector).select2();
        $(pattern_selector).on('select2:select', function (e) {
            var $opt = $(e.params.data.element);
            tn2_project_edit.update_category_selector($opt);
        });
        tn2_project_edit.update_pattern_select(0);
    }
}

document.addEventListener('DOMContentLoaded', tn2_project_edit.setup);

