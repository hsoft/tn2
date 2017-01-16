var tn2_apropos = {
    setup: function() {
        tn2_apropos.bind_box_switchers();
    },

    bind_box_switchers: function() {
        var switchers = document.querySelectorAll('a[data-boxid]');
        console.log(switchers);
        for (var i=0; i<switchers.length; i++) {
            switchers[i].addEventListener('click', function() {
                var container = document.getElementById('box-container');
                var allBoxes = container.querySelectorAll('div.box');
                var boxId = this.getAttribute('data-boxid');
                var box = document.getElementById(boxId);
                for (var j=0; j<allBoxes.length; j++) {
                    addClass(allBoxes[j], 'hidden');
                }
                removeClass(box, 'hidden');

                var ul = this.parentElement.parentElement;
                var allLi = ul.querySelectorAll('li');
                for (var j=0; j<allLi.length; j++) {
                    removeClass(allLi[j], 'active');
                }
                addClass(this.parentElement, 'active');
            });
        }
    }
}

document.addEventListener('DOMContentLoaded', tn2_apropos.setup);

