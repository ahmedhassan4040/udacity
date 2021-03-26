window.parseISOString = function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};

/**
 * Delete The Venue
 */
function deleteVenue(id) {
  fetch(`/venues/${id}`, {
    method: 'DELETE'
  }).then(res => res.json())
    .then(res => {
      if (res.isDeleted)
        window.location.href = "/"
      else
        location.reload();//Reoload For Display Error Message
    })
}