alert("Poisoned app.js loaded\nyou got hacked");

document.addEventListener("DOMContentLoaded", () => {
    const banner = document.createElement("div");

    banner.innerText = "⚠ Cache Poisoning Successful From untrusted beeceptor";
    banner.style.padding = "10px";
    banner.style.background = "red";
    banner.style.color = "white";

    document.body.prepend(banner);
});
