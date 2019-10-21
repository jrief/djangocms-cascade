function inIframe() {
    try {
        return window.self !== window.top;
    } catch (e) {
        return true;
    }
}

if (inIframe()) {
    var CMS = window.parent.CMS;
} else {
    var CMS = window.CMS;
}

function LocalStorage_or_AppendFolderRender(element, url, timestamp) {
    if (inIframe()) {
        var paramater;
        $(".btn").removeClass("active");
        $(this).addClass("active");

        var idFolder = url.substring(url.lastIndexOf("/") + 1);
        var timestamp_storage_folder = "timestamp_storage_" + idFolder;
        timestamp_storage = sessionStorage.getItem(timestamp_storage_folder);
        sessionStorage.setItem("folder_current_id", idFolder);

        if (sessionStorage.getItem(timestamp_storage_folder) === timestamp.toString() && sessionStorage.getItem("HTML_FOLDER_CLIPS_" + id_folder !== null)) {
            data_html = sessionStorage.getItem("HTML_FOLDER_CLIPS_" + idFolder);
            $(".clips-wrapper").html(data_html);
        } else {
            var token = "{ 'csrfmiddlewaretoken': '" + CMS.config.csrf + "' }";
           // CMS.API.Helpers.csrf(tokenf);
            var data = {
                placeholder_id: 1,
                csrfmiddlewaretoken: CMS.config.csrf,
                target_language: CMS.config.request.language
            };

            $.ajax({
                type: "POST",
                url: "/cascade_libclips_folder/" + idFolder + "/",
                post: token,
                data: data,
                success: function(response) {
                    sessionStorage.setItem(timestamp_storage_folder, timestamp);
                    sessionStorage.setItem("HTML_FOLDER_CLIPS_" + idFolder, response);
                    $(".clips-wrapper").html(response);
                }
            });
        }
        e = e || window.event;
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();
    }
}

function ajaxCopyToClipboard(event, that, url, paramater) {
    var data_post = JSON.parse($(that).attr("data-post"));
    var csrf = data_post.csrfmiddlewaretoken;
    var paramater;
    var token = "{ 'csrfmiddlewaretoken': '" + csrf + "' }";
    var data = {
        paramater: paramater,
        placeholder_id: 1,
        csrfmiddlewaretoken: csrf,
        target_language: "en"
    };
    $.ajax({
        type: "POST",
        url: url,
        post: token,
        data: data,
        success: function(response) {},
    }).done(function(response) {
        if (inIframe()) {
            CMS.API.Clipboard._enableTriggers();
            stat = $.extend({}, data, response.data);
            CMS.API.StructureBoard.invalidateState("MOVE", stat);
            CMS.API.Clipboard.ui.pluginsList.html(response.data.html);
            CMS.API.Clipboard.ui.triggers.trigger("click.cms.clipboard");
            CMS.API.StructureBoard._loadedStructure = false;
            CMS.API.StructureBoard.show();
            //CMS.API.Helpers.reloadBrowser();
        } else {
            $("#modal_dialog").removeClass("d-none")
            $("#modal_dialog").modal("show");
        }
    });
}
