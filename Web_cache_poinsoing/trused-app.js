console.log("Legitimate app.js loaded");

document.addEventListener("DOMContentLoaded", () => {
    const banner = document.createElement("div");

    banner.innerText = "Loaded from trusted CDN from trusted beeceptor";
    banner.style.padding = "10px";
    banner.style.border = "1px solid green";

    document.body.prepend(banner);
});
