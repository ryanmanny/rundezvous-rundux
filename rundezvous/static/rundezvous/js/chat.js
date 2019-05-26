// TODO: Remove this in favor of Django Channels
function ajax_form(selector, callback)
{
    let form = $(selector);
    form.submit(function (event) {
        event.preventDefault();
        $.ajax({
            type: form.attr('method'),
            url: form.attr('action'),
            data: form.serialize(),
            success: function (data) {
                if (callback !== undefined) {
                    // TODO: I don't think this check is JavaScriptic
                    callback(data);
                }
            }
        });
        form.trigger('reset');
    });
}

function load_message(id)
{
    $.ajax({
        url: '/chat/message/' + id,
        type: 'GET',
        success: function (data) {
            $('#messages-list').append(data)
        }
    });
}

function check_for_messages(timeout)
{
    // TODO: Use long polling, channels / RabbitMQ, etc. something besides polling
    if (timeout === undefined)
        timeout = 1000;  // One second by default

    // Eventually do this asynchronously
    last_message_id = $('.message').last().data('message-id');

    $.ajax({
        url: '/chat/chatroom/new_messages/' + last_message_id,
        type: 'GET',
        success: function (data) {
            for (let message_id in data.message_ids) {
                load_message(data.message_ids[message_id]);
            }
        }
    });

    setTimeout(check_for_messages, timeout);
}
