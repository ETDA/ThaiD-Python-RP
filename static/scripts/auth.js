var alertPlaceholder = document.getElementById('liveAlertPlaceholder')
function alert(message, type) {
    var wrapper = document.createElement('div')
    wrapper.innerHTML = '<div class="alert alert-' + type + ' alert-dismissible" role="alert">' + message + '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>'
    alertPlaceholder.append(wrapper)
}

document.addEventListener('DOMContentLoaded', function () {
    var requestButton = document.getElementById('requestid');
    var revorkButton = document.getElementById('revoke');

    requestButton.addEventListener('click', function () {
        const url = '@Configuration["ThaID:ASEndPoint"]/TokenInspect';
        const bearerToken = '@Model.AccessToken';
        const headers = new Headers({
            'Authorization': `Bearer ${bearerToken}`
        });
        fetch(url, {
            method: 'GET',
            headers: headers
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                alert(JSON.stringify(data), 'success')

                console.log(data);
            })
            .catch(error => {
                alert('There has been a problem with your fetch operation:', 'danger')
                console.error('There has been a problem with your fetch operation:', error);
            });
    });

    revorkButton.addEventListener('click', function () {
        const url = '@Configuration["ThaID:ASEndPoint"]/TokenRevoke';
        const bearerToken = '@Model.AccessToken';
        const headers = new Headers({
            'Authorization': `Bearer ${bearerToken}`
        });
        fetch(url, {
            method: 'GET',
            headers: headers
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                alert(JSON.stringify(data), 'warning')
            })
            .catch(error => {
                alert('There has been a problem with your fetch operation:', 'danger')
                console.error('There has been a problem with your fetch operation:', error);
            });
    });
});