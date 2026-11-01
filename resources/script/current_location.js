(function () {
  const locationBtn = document.getElementById("getLocation");
  const locationStatus = document.getElementById("status");
  const latInput = document.getElementById("latitude");
  const lngInput = document.getElementById("longitude");
  const addressInput = document.getElementById("address");
  const locationError = document.getElementById("error");

  function setStatus(message, isError = false) {
    locationStatus.textContent = message;
    locationStatus.style.color = isError ? "red" : "green";
  }

  function clearCoordinates() {
    latInput.value = "";
    lngInput.value = "";
  }

  function handleLocationError(err) {
    clearCoordinates();
    switch (err.code) {
      case err.PERMISSION_DENIED:
        setStatus("Location permission denied. Please type your address below.", true);
        break;
      case err.POSITION_UNAVAILABLE:
        setStatus("Location unavailable. Please type your address below.", true);
        break;
      case err.TIMEOUT:
        setStatus("Location request timed out. Please try again or type your address.", true);
        break;
      default:
        setStatus("Could not get location. Please type your address below.", true);
    }
    addressInput.focus();
  }

  function getLocation() {
    if (!("geolocation" in navigator)) {
      setStatus("Your browser does not support location. Please type your address.", true);
      addressInput.focus();
      return;
    }

    locationError.textContent = "";
    locationBtn.disabled = true;
    setStatus("Getting your location...");
    locationStatus.style.color = "";

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude, accuracy } = position.coords;

        latInput.value = latitude.toFixed(6);
        lngInput.value = longitude.toFixed(6);

        setStatus(`Location captured ✔ (accuracy: about ${Math.round(accuracy)} m)`);
        locationBtn.disabled = false;
        locationBtn.textContent = "📍 Update my location";
      },
      (err) => {
        handleLocationError(err);
        locationBtn.disabled = false;
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0
      }
    );
  }

  locationBtn.addEventListener("click", getLocation);
})();