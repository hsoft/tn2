var tn2_groups = {
    setup: function() {
        tn2_groups.bind_open_url_on_select();
    },

    bind_open_url_on_select: function() {
        var selects = document.querySelectorAll('select.open-url-on-select');
        for (var i=0; i<selects.length; i++) {
            selects[i].addEventListener('change', function() {
                var url = this.options[this.selectedIndex].getAttribute('data-url');
                if (url) {
                    window.location.href = url;
                }
            });
        }
    }
}

document.addEventListener('DOMContentLoaded', tn2_groups.setup);

