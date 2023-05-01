function confirmDelete(id, method) {
    if (confirm("Are you sure you want to delete?")) {
        window.location.href = `/${method}/` + id;
    }
}
