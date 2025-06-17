document.addEventListener("DOMContentLoaded", function () {

    function initializeImageContainers() {
        const imageContainers = document.querySelectorAll('.post-image-container');
        
        imageContainers.forEach(container => {
            const img = container.querySelector('.post-image');
            const backdrop = container.querySelector('.post-image-backdrop');
            
            if (img && backdrop) {
                img.onload = function() {
                    backdrop.style.backgroundImage = `url(${img.src})`;
                    
                    
                    const canvas = document.createElement('canvas');
                    const context = canvas.getContext('2d');
                    canvas.width = 1;
                    canvas.height = 1;
                    context.drawImage(img, 0, 0, 1, 1);
                    const [r, g, b] = context.getImageData(0, 0, 1, 1).data;
                    
                  
                    const darkenFactor = 0.3;
                    const backdropColor = `rgb(${r * darkenFactor}, ${g * darkenFactor}, ${b * darkenFactor})`;
                    container.style.backgroundColor = backdropColor;
                };
            }
        });
    }


    initializeImageContainers();

    const editCategoriesButton = document.getElementById("editCategoriesButton");
    if (editCategoriesButton) {
        editCategoriesButton.addEventListener("click", toggleEditCategories);
    }

    document.querySelectorAll('.category-button').forEach(button => {
        initializeCategoryButton(button);
    });

    document.querySelectorAll('.pure-menu-link').forEach(link => {
        link.addEventListener('click', function(event) {
            event.preventDefault();
            const category = this.getAttribute('data-category') || 'home';
            window.location.href = `/?category=${category}`; 
        });
    });
});


function toggleEditCategories() {
    const editSection = document.getElementById('editCategoriesSection');
    const categoryButtons = document.querySelectorAll('.category-button'); 

    if (editSection.classList.contains('show')) {
        editSection.style.maxHeight = '0';
        editSection.style.opacity = '0';
        categoryButtons.forEach(button => button.classList.remove('shake')); 

        setTimeout(() => {
            editSection.style.display = 'none';
            editSection.classList.remove('show');
        }, 500); 
    } else {
        editSection.style.display = 'block';
        setTimeout(() => {
            editSection.style.maxHeight = editSection.scrollHeight + "px";
            editSection.style.opacity = '1';
            editSection.classList.add('show');
            categoryButtons.forEach(button => button.classList.add('shake'));
        }, 10); 
    }
}

function initializeCategoryButton(button) {
    const category = button.getAttribute('data-category');
    const isAdded = !!document.getElementById(`category-${category}`);
    updateButtonState(button, isAdded);
    button.addEventListener('click', () => handleCategoryToggle(button));
}

function handleCategoryToggle(button) {
    const category = button.getAttribute('data-category');
    const isCurrentlyAdded = button.innerHTML.trim().startsWith('-');
    
    if (isCurrentlyAdded) {
        removeCategory(button, category);
    } else {
        addCategory(button, category);
    }
}

function addCategory(button, category) {
    if (document.getElementById(`category-${category}`)) {
        return;
    }

    updateButtonState(button, true);

    const newSidebarItem = createSidebarItem(category);
    const sidebar = document.querySelector('.sidebar ul');
    const homeLink = document.getElementById('homeLink').parentElement;
    sidebar.insertBefore(newSidebarItem, homeLink.nextSibling);
    
    requestAnimationFrame(() => {
        newSidebarItem.style.opacity = '1';
    });

    saveCategoryChanges();
}

function removeCategory(button, category) {
    const sidebarItem = document.getElementById(`category-${category}`);
    
    if (sidebarItem) {
        const listItem = sidebarItem.parentElement;
        listItem.style.opacity = '0';
        setTimeout(() => {
            listItem.remove();
            updateButtonState(button, false);
            saveCategoryChanges();
        }, 300);
    }
}

document.querySelectorAll('.pure-menu-link').forEach(link => {
    link.addEventListener('click', function(event) {
        event.preventDefault();
        const category = this.getAttribute('data-category') || 'home';
        window.location.href = `/?category=${category}`; 
    });
});
function updateButtonState(button, isAdded) {
    const category = button.getAttribute('data-category');
    const displayName = category.charAt(0).toUpperCase() + category.slice(1);
    button.innerHTML = `${isAdded ? '- ' : '+ '}${displayName}`;
}

function createSidebarItem(category) {
    const newSidebarItem = document.createElement('li');
    newSidebarItem.classList.add('pure-menu-item');
    const displayName = category.charAt(0).toUpperCase() + category.slice(1);
    newSidebarItem.innerHTML = `<a href="javascript:void(0);" class="pure-menu-link" data-category="${category}" id="category-${category}">${displayName}</a>`;
    newSidebarItem.style.opacity = '0';
    newSidebarItem.style.transition = 'opacity 0.3s ease-in-out';
    return newSidebarItem;
}

function saveCategoryChanges() {
    const selectedCategories = Array.from(document.querySelectorAll('.sidebar > ul > li > .pure-menu-link[data-category]'))
        .filter(link => link.id !== 'homeLink')
        .map(link => link.getAttribute('data-category'));

    fetch('/api/user/categories/', {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ categories: selectedCategories })
    })
    .catch(error => console.error('Error saving categories:', error));
}

function deletepost(pid){
    cf = confirm("Are you sure you want to delete this post?")
    if(cf){
        console.log(`Deleting Post: ${pid}`)
        url = '/api/post/' + pid
        fetch(url,{method:'DELETE'})
        .then(response => response.json())
        .then(data => {
                        if(data.code == 200){
                            alert("delete successful")
                            window.location.href = '/myprofile'
                        } else {
                            console.error('Error Deleting posts:')
                        }
        })
        .catch(error => console.error('Error Deleting posts:', error))
    }
}

// Handle voting on post
const postUpvoteButtons = document.querySelectorAll('.upvote-button[data-pid]');
const postDownvoteButtons = document.querySelectorAll('.downvote-button[data-pid]');

postUpvoteButtons.forEach(button => {
    button.addEventListener('click', function(event) {
        event.preventDefault();
        const pid = this.getAttribute('data-pid');
        votePost(pid, 'upvote', this);
        console.log("upvote triggered", pid);
    });
});

postDownvoteButtons.forEach(button => {
    button.addEventListener('click', function(event) {
        event.preventDefault();
        const pid = this.getAttribute('data-pid');
        votePost(pid, 'downvote', this);
        console.log("downvote triggered", pid);
    });
});

function votePost(pid, voteType, buttonElement) {
    if (!pid) {
        console.error("Post ID is missing!");
        return;
    }

    fetch(`/api/post/${pid}/vote`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                'vote': voteType
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Update the upvote and downvote elements using the unique ID
            const upvoteElement = document.getElementById(`post-upvotes-${pid}`);
            const downvoteElement = document.getElementById(`post-downvotes-${pid}`);

            if (upvoteElement && downvoteElement) {
                upvoteElement.innerText = "👍 " + data.upvotes +" Upvote";
                downvoteElement.innerText ="👎 " + data.downvotes+" Downvote";
            } else {
                console.error("Upvote or downvote element not found for post", pid);
            }
            console.log("data", data);
        })
        .catch(error => {
            console.error('Error voting on post:', error);
            alert("An error occurred while voting.");
        });
}


// function voteReply(cid, voteType, buttonElement) {
//     fetch(`/api/reply/${cid}/vote`, {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json',
//             },
//             body: JSON.stringify({
//                 'vote': voteType
//             })
//         })
//         .then(response => response.json())
//         .then(data => {
//             if (data.upvotes !== undefined && data.downvotes !== undefined) {
//                 const commentDiv = buttonElement.closest('.comment');
//                 commentDiv.querySelector('.reply-upvotes').innerText = data.upvotes;
//                 commentDiv.querySelector('.reply-downvotes').innerText = data.downvotes;
//             } else {
//                 alert(data.message || "Failed to vote.");
//             }
//         })
//         .catch(error => {
//             console.error('Error voting on reply:', error);
//             alert("An error occurred while voting.");
//         });
// }