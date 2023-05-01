function confirmDeleteInteraction(interactionId, personId, contactName) {
    if (confirm("Are you sure?")) {
        window.location.href = `/delete_interaction/${interactionId}/${personId}/${contactName}`;
    }
}
