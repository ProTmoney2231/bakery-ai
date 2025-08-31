(function() {
  // Create an iframe
  const iframe = document.createElement("iframe");
  iframe.src = "http://127.0.0.1:8000/widget/multi.html"; // your widget 
file
  iframe.style.position = "fixed";
  iframe.style.bottom = "20px";
  iframe.style.right = "20px";
  iframe.style.width = "300px";
  iframe.style.height = "400px";
  iframe.style.border = "none";
  iframe.style.borderRadius = "12px";
  iframe.style.boxShadow = "0 4px 12px rgba(0,0,0,0.2)";
  iframe.style.zIndex = "9999";

  // Add it to the page
  document.body.appendChild(iframe);
})();

