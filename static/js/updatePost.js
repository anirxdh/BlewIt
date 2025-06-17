document.addEventListener("DOMContentLoaded", function () {
    const chekbox = document.getElementById("changeImage");
    const form = document.getElementById("updatePostForm");
    chekbox.checked = false;
    const url = form.getAttribute('action');
    console.log(url);
    if(form){
        form.addEventListener("submit",function(event){
            event.preventDefault();
            var formdata = new FormData(form);
            var isChange = formdata.get('changeImage') ? true : false;
            formdata.append('isChange', isChange);

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
                  window.location.href = '/myprofile'
                })
                .catch(error => {
                  console.error('Error:', error);
                });
        });
    }
});


function toggleFileDisplay(){
    const fc=document.getElementById("filecontainer");
    const fileInput = document.getElementById("file");
    if(fc){
        fileInput.value = "";
        if(fc.style.display==='none'){
            fc.style.display = 'block';
        }else{
            fc.style.display = 'none';
        }
    }
}
