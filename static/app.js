function confirmDelete(event, url) {
  event.preventDefault();
  Swal.fire({
    title: "Are you sure?",
    text: "You won't be able to revert this!",
    icon: "warning",
    showConfirmButton: true,
    showCancelButton: true,
    confirmButtonColor: "#d33",
    cancelButtonColor: "#6e7881",
    confirmButtonText: "Yes, delete it!",
  }).then((result) => {
    if (result.isConfirmed) {
      window.location.href = url;
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  const flashDataEl = document.getElementById("flash-data");
  if (!flashDataEl) return;

  const flashMessages = JSON.parse(flashDataEl.textContent || "[]");

  const iconMap = {
    danger: "error",
    warning: "warning",
    success: "success",
    info: "info",
    message: "info",
  };

  if (Array.isArray(flashMessages) && flashMessages.length > 0) {
    flashMessages.forEach(([category, message]) => {
      const iconType = iconMap[category] || "info";
      Swal.fire({
        toast: true,
        position: "top-end",
        icon: iconType,
        title: message,
        showConfirmButton: false,
        timer: 3500,
        timerProgressBar: true,
        didOpen: (toast) => {
          toast.addEventListener("mouseenter", Swal.stopTimer);
          toast.addEventListener("mouseleave", Swal.resumeTimer);
        },
      });
    });
  }
});
