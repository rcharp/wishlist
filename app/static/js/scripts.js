function ShowDropdown(id) {
    var dropdown = document.getElementById(id);
    if (dropdown.classList.contains('opacity-0')){
        dropdown.classList.remove('opacity-0');
        dropdown.classList.remove('scale-95');
        dropdown.classList.add('opacity-100');
        dropdown.classList.add('scale-100');

        dropdown.style.display = '';
    }
    else {
        dropdown.classList.remove('opacity-100');
        dropdown.classList.remove('scale-100');
        dropdown.classList.add('opacity-0');
        dropdown.classList.add('scale-95');

        dropdown.style.display = 'none';
    }
}

function Vote(feedback_id, feedback_url) {
    $.ajax({
        url: '{{ url_for("user.update_vote") }}',
        type: 'POST',
        beforeSend: UpdateVote(feedback_id),
        data: {'feedback_id': feedback_id},
        success: function (response) {
        },
        error: function (xhr) {
            window.location.href = feedback_url;
        }
    });
}

function UpdateVote(feedback_id) {
    var votes = document.getElementById(feedback_id + '-votes').innerText;
    var count = parseInt(votes);
    document.getElementById(feedback_id + '-votes').innerText = String(count + 1);
}