function confirmDeleteContact(id) {
    if (confirm("Are you sure?")) {
        window.location.href = `/delete_contact/` + id;
    }
}
