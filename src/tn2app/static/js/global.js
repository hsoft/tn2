var tn2_global = {
    setup: function() {
        tn2_global.bind_comment_buttons_enabler();
    },

    bind_comment_buttons_enabler: function() {
        // We want to prevent empty comments from being posted. We don't have user-friendly
        // form validation on that front.
        var commentForm = document.querySelector('form.comment-form');
        commentForm.addEventListener('submit', function(event) {
            var comment = CKEDITOR.instances.id_comment.getData();
            if (!comment) {
                event.preventDefault();
            }
        });
    }
}

document.addEventListener('DOMContentLoaded', tn2_global.setup);

