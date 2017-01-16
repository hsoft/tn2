function hasClass(el, className) {
  if (el.classList)
    return el.classList.contains(className)
  else
    return !!el.className.match(new RegExp('(\\s|^)' + className + '(\\s|$)'))
}

function addClass(el, className) {
  if (el.classList)
    el.classList.add(className)
  else if (!hasClass(el, className)) el.className += " " + className
}

function removeClass(el, className) {
  if (el.classList)
    el.classList.remove(className)
  else if (hasClass(el, className)) {
    var reg = new RegExp('(\\s|^)' + className + '(\\s|$)')
    el.className=el.className.replace(reg, ' ')
  }
}

var tn2_global = {
    setup: function() {
        tn2_global.bind_comment_buttons_enabler();
    },

    bind_comment_buttons_enabler: function() {
        // We want to prevent empty comments from being posted. We don't have user-friendly
        // form validation on that front.
        var commentForm = document.querySelector('form.comment-form');
        if (commentForm == null) {
            return;
        }
        commentForm.addEventListener('submit', function(event) {
            var comment = CKEDITOR.instances.id_comment.getData();
            if (!comment) {
                event.preventDefault();
            }
        });
    }
}

document.addEventListener('DOMContentLoaded', tn2_global.setup);

