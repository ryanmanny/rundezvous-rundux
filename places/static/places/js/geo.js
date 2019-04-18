function update_location() {
    const timeout = 30000;  // 30 seconds

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            $.post({
                url: window.update_location_url,
                data: {
                    lat: position.coords.latitude,
                    long: position.coords.longitude
                },
                success: function(data) {
                    // alert(`Location updated ${data}`);
                }
            })
        });
    } else {
        console.log("GPS not available");
    }
    setTimeout(update_location, timeout);
}
