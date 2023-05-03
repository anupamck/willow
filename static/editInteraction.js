function editInteraction(id, date, title, notes, person_id, contact_name) {
    // set the values of the popup window form fields
    document.getElementById("date-edit").value = date;
    document.getElementById("title-edit").value = decodeHtml(title);
    document.getElementById("notes-edit").value = decodeHtml(notes);
    document.getElementById("interaction-id-edit").value = id;
    document.getElementById("person-id-edit").value = person_id;
    document.getElementById("contact-name-edit").value = contact_name;
  
    // Get the modal's shell
    const modal = document.getElementById("modal-shell-edit");

    // display the popup window
    modal.style.display = "block";

    // Get the <span> element that closes the modal
    const closeButton = document.getElementById("close-edit");

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
  