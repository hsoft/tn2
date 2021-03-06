var tn2_project_details = {
    setup: function() {
        tn2_project_details.bind_image_previews();
    },

    bind_image_previews: function() {
        var preview_images = document.querySelectorAll('img.project-image-preview');
        for (var i=0; i<preview_images.length; i++) {
            preview_images[i].addEventListener('click', function() {
                var full_url = this.getAttribute('data-full-url');
                var fullsize_img = document.querySelector('#full-size-image');
                fullsize_img.setAttribute('src', full_url);
            });
        }
    }
}

document.addEventListener('DOMContentLoaded', tn2_project_details.setup);
