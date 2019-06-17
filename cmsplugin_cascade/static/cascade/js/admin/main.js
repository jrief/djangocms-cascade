function modal_catalog(ajx) {

    var Modal = CMS.Modal;
    var modal_clips = new Modal({
        width: 100,
        height: 100,
        resizable: true,
        minimizable: true,
        maximizable: true
    });

    modal_clips.open({

        html: Object.values(ajx),
        title: 'clip',

        width: '40%',
        height: '95%',
        left: '0px'

    });
    modal_clips.ui.modal.css("left", "0px");
    modal_clips.ui.modal.css("top", "48px");
    modal_clips.ui.modal.css("margin", "0px");
    modal_clips.ui.modal.css("z-index", "140");
}


function ajax_cascade_main(url) {

    var paramater;

    var tokenf = 'csrf';

    var postd = '{ "csrfmiddlewaretoken": "' + CMS.config.csrf + '" }';

    CMS.API.Helpers.csrf(tokenf);

    alert(sessionStorage.getItem('folder_current_id'));
    if (sessionStorage.getItem('folder_current_id')) {
        url = url + sessionStorage.getItem('folder_current_id');
    } else {
        url = url + 1;
    };


    var data = {

        placeholder_id: 1,

        csrfmiddlewaretoken: CMS.config.csrf,
        target_language: CMS.config.request.language
    };


    $.ajax({
            type: 'POST',
            url: url,
            post: postd,
            data: data,
            success: function(response) {
                response;
                modal_catalog(response)
            }

        }

    );

}


$(".cms-show-clipslib").on("click", function(e) {
    ajax_cascade_main('/clipslib/');
});
