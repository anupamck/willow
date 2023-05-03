function addInteraction(person_id, contact_name) {
    // retrieve values from hidden form fields
    document.getElementById("person-id-add").value = person_id;
    document.getElementById("contact-name-add").value = contact_name;

    // Get the modal's shell
    const modal = document.getElementById("modal-shell-add");

    // display the popup window
    modal.style.display = "block";

    // Get the <span> element that closes the modal
    const closeButton = document.getElementById("close-add");

    // When the user clicks on <span> (x), close the modal
    closeButton.onclick = function() {
    modal.style.display = "none";
    }

    // When the user clicks anywhere outside of the modal, close it
    window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
    }
  }
  