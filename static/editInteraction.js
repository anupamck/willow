function editInteraction(id, date, title, notes, person_id, contact_name) {
    // set the values of the popup window form fields
    document.getElementById("date").value = date;
    document.getElementById("title").value = title;
    document.getElementById("notes").value = notes;
    document.getElementById("interaction-id").value = id;
    document.getElementById("person-id").value = person_id;
    document.getElementById("contact-name").value = contact_name;
  
    // Get the modal's shell
    const modal = document.getElementsByClassName("modal-shell")[0];

    // display the popup window
    modal.style.display = "block";

    // Get the <span> element that closes the modal
    const closeButton = document.getElementsByClassName("close")[0];

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
  