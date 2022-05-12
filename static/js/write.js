let images = [];

$(function(){

    $('#file').change(function(e) {
        $("#file_preview > div:nth-child(1)").html('');
        images = [];
        for (const i of e.target.files) {
            if(i.type.includes('image')) images.push(i);
        }

        //limit 4
        const tmp = [];
        if (images[0]) tmp.push(images[0]);
        if (images[1]) tmp.push(images[1]);
        if (images[2]) tmp.push(images[2]);
        if (images[3]) tmp.push(images[3]);
        images = tmp;

        let elements = '';
        let srcs = [];

        if (images.length == 0) {
            $('#file_input').removeClass('hidden');
            $('#file_input2').addClass('hidden');
            $('#close_file_input').addClass('hidden');
            return;
        }

        for (const v of images) srcs.push(URL.createObjectURL(v));

        if (images.length == 1) elements = `<img src="${srcs[0]}">`;
        else if (images.length == 2) {
            elements = `
                        <div class="grid grid-cols-2 gap-1">
                          <img src="${srcs[0]}" class="h-full">
                          <img src="${srcs[1]}" class="h-full">
                        </div>
                    `;
        } else if (images.length == 3) {
            elements = `
                      <div class="flex flex-col gap-1">
                        <div class="flex justify-center">
                          <img src="${srcs[0]}">
                        </div>
                        <div class="grid grid-cols-2 gap-1">
                          <img src="${srcs[1]}" class="h-full">
                          <img src="${srcs[2]}" class="h-full">
                        </div>
                      </div>
                    `;
        } else if (images.length == 4) {
            elements = `
              <div class="grid grid-cols-2 grid-rows-2 gap-1">
                <img src="${srcs[0]}" class="h-full">
                <img src="${srcs[1]}" class="h-full">
                <img src="${srcs[2]}" class="h-full">
                <img src="${srcs[3]}" class="h-full">
              </div>
            `;
        } else if (images.length > 4) {
            elements = `
              <div class="grid grid-cols-2 grid-rows-2 gap-1">
                <img src="${srcs[0]}" class="h-full">
                <img src="${srcs[1]}" class="h-full">
                <img src="${srcs[2]}" class="h-full">
                <div class="relative" class="h-full">
                  <img src="${srcs[3]}" class="w-full h-full absolute z-0">
                  <div class="absolute w-full h-full z-10 bg-black opacity-20"></div>
                  <span class="absolute text-white text-3xl font-semibold left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-20">+${images.length - 3}</span>
                </div>
              </div>
            `;
        }
        $('#file_preview > div:nth-child(1)').html(elements);
        $('#file_input2').removeClass('hidden');
        $('#close_file_input').removeClass('hidden');
        $('#file_input').addClass('hidden');
    });
})

function post(option = "insert", postId = "") {
    const textArea = $('#writeform > textarea');
    let today = new Date().toISOString();

    if (textArea.val().length == 0) {
        textArea.focus();
        return;
    }

    const form = new FormData();
    form.append("text", textArea.val());
    form.append("date", today);
    form.append("option", option);
    form.append("post_id", postId);

    if (images.length) {
        let i = 0;
        for (const file of images) {
            form.append(`file${i}`, file);
            i++;
        }
    }

    $.ajax({
        type: "POST",
        url: "/posting",
        contentType: false,
        processData: false,
        data: form,
        success: function (res) {
            alert('게시물이 등록되었습니다.')
            window.location.href = '/';
        }
    })
}

const toggleFileInput = () => {
    $('#file_toggle_btn').toggleClass('bg-slate-300');
    $('#file_input_wrap').toggleClass('hidden');
}

const fileInputClose = () => {
    images = [];
    $('#file_preview > div:nth-child(1)').html('');
    $('#file_input').removeClass('hidden');
    $('#file_input2').addClass('hidden');
    $('#close_file_input').addClass('hidden');
}