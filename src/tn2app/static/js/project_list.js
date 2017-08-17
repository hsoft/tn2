var tn2_project_list = {
    setup: function() {
        tn2_project_list.bind_pattern_selectors();
    },

    bind_pattern_selectors: function() {
        var creator_selector = document.querySelector('select[name="pattern_creator"]');
        var pattern_selector = document.querySelector('select[name="pattern"]');
        $selectors = $(creator_selector);
        if (pattern_selector) {
            $selectors = $selectors.add(pattern_selector);
        }
        $selectors.select2();
        $selectors.on('select2:select', function(e) {
            var url = $(this).data('get-url') + e.params.data.id;
            location.href = url;
        });
    }
}

document.addEventListener('DOMContentLoaded', tn2_project_list.setup);


