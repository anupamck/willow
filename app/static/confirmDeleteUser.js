function confirmDeleteUser() {
    if (confirm("Are you sure? DANGER - this will delete all of your user's data. This is IRREVERSIBLE!")) {
        document.getElementById("deleteUserForm").submit();
    }
}
