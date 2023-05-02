function editContact(id, name, frequency) {
    // set the values of the popup window form fields
    document.getElementById("name").value = name;
    document.getElementById("frequency").value = frequency;
    document.getElementById("contact-id").value = id;
  
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
  