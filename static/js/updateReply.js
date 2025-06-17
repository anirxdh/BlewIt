document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("updateReplyForm");
    const url = form.getAttribute('action');
    const retAddr = document.getElementById("cancel").getAttribute('href');
    console.log(url);
    if(form){
        form.addEventListener("submit",function(event){
            event.preventDefault();
            var formdata = new FormData(form);

            console.log(formdata);
            fetch(url, {
                method: 'PUT', // specify the request method
                body: formdata
              })
                .then(response => {
                  if (!response.ok) {
                    throw new Error('Network response was not ok');
                  }
                  return response.json();
                })
                .then(data => {
                  console.log('Success:', data);
                  window.location.href = retAddr
                })
                .catch(error => {
                  console.error('Error:', error);
                });
        });
    }
});