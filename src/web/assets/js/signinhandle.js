console.log("Caching sessionId");
localStorage['sessionId'] = "%sessionid%";
console.log("Reaching cached session id");
var sesid = localStorage.getItem('sessionId');
console.log("Generating package for request /home page");
function getPage(page) {
  console.log("Requesting provided page POST: " + page);
  console.log("-Generating request");
  return fetch(page, {
    method: 'POST',
    body: JSON.stringify({
      sessionid: sesid,
    }),
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
    },
  })
    .then(response => {
      if (!response.ok) {
        throw new Error(`Error! status: ${response.status}`);
      }
      return response.json();
    })
    .catch(error => {
      console.log('error: ', error);
      alert("An error occurred while requesting the page! The problem is caused by the server.");
      window.location.replace("/");
    });
}

getPage("/home").then(data => {
  console.log("Server responded to request");
  console.log("Loading raw html");
  var showhtml = data.html;
  console.log("Opening page source file");
  document.open();
  console.log("Writing raw html");
  document.write(showhtml);
  console.log("Packing raw html and preparing for display");
  document.close();
  console.log("Displaying html");
});