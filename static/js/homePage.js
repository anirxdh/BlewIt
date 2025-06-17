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


    document.querySelectorAll('.pure-menu-link').forEach(link => {
        link.addEventListener('click', function(event) {
            event.preventDefault();
            const category = this.getAttribute('data-category') || 'home';
            window.location.href = `/?category=${category}`; 
        });
    });

    document.querySelectorAll('.pure-menu-link').forEach(link => {
        link.addEventListener('click', function(event) {
            event.preventDefault();
            const category = this.getAttribute('data-category') || 'home';
            window.location.href = `/?category=${category}`; 
        });
    });

 
    const editCategoriesButton = document.getElementById("editCategoriesButton");
    if (editCategoriesButton) {
        editCategoriesButton.addEventListener("click", toggleEditCategories);
    }

    document.querySelectorAll('.category-button').forEach(button => {
        initializeCategoryButton(button);
    });


    document.querySelectorAll('.upvote, .downvote').forEach(button => {
        button.addEventListener('click', function() {
            const pid = this.getAttribute('data-pid');
            const voteType = this.classList.contains('upvote') ? 'upvote' : 'downvote';
            votePost(pid, voteType);
        });
    });


    const hamburger = document.getElementById('hamburger');
    if (hamburger) {
        hamburger.addEventListener('click', function() {
            document.body.classList.toggle('sidebar-active');
        });
    }


    initializeFilterSystem();
});


function initializeFilterSystem() {

    const filterContainer = document.querySelector('.filter-button').parentElement;
    const oldFilterButton = document.querySelector('.filter-button');
    

    const filterHTML = `
        <div class="filter-dropdown">
            <button class="filter-button">Filter</button>
            <div class="filter-menu">
                <div class="filter-option" data-sort="newest">
                    <i>🕒</i> Newest First
                </div>
                <div class="filter-option" data-sort="oldest">
                    <i>📅</i> Oldest First
                </div>
                <div class="filter-option" data-sort="most-upvotes">
                    <i>👍</i> Most Upvotes
                </div>
                <div class="filter-option" data-sort="most-downvotes">
                    <i>👎</i> Most Downvotes
                </div>
            </div>
        </div>
    `;
    
    oldFilterButton.remove();
    filterContainer.insertAdjacentHTML('beforeend', filterHTML);


    const filterButton = document.querySelector('.filter-button');
    const filterMenu = document.querySelector('.filter-menu');
    const filterOptions = document.querySelectorAll('.filter-option');


    filterButton.addEventListener('click', (e) => {
        e.stopPropagation();
        filterMenu.classList.toggle('show');
    });


    document.addEventListener('click', (e) => {
        if (!e.target.closest('.filter-dropdown')) {
            filterMenu.classList.remove('show');
        }
    });

    filterOptions.forEach(option => {
        option.addEventListener('click', () => {

            filterOptions.forEach(opt => opt.classList.remove('active'));

            option.classList.add('active');
            
            const sortType = option.getAttribute('data-sort');
            sortPosts(sortType);
            
      
            filterMenu.classList.remove('show');
        });
    });
}

function sortPosts(sortType) {
    const postSection = document.getElementById('postSection');
    const posts = Array.from(postSection.getElementsByClassName('post-container'));
    
    posts.sort((a, b) => {
        switch(sortType) {
            case 'newest':
                return getPostDate(b) - getPostDate(a);
            case 'oldest':
                return getPostDate(a) - getPostDate(b);
            case 'most-upvotes':
                return getUpvotes(b) - getUpvotes(a);
            case 'most-downvotes':
                return getDownvotes(b) - getDownvotes(a);
            default:
                return 0;
        }
    });
    

    postSection.innerHTML = '';
    posts.forEach(post => postSection.appendChild(post));
}

function getPostDate(post) {
    const dateText = post.querySelector('.post-meta').textContent;
    return new Date(dateText.split(' - ')[1]);
}

function getUpvotes(post) {
    const upvoteText = post.querySelector('.upvote').textContent;
    return parseInt(upvoteText.match(/\d+/)[0]);
}

function getDownvotes(post) {
    const downvoteText = post.querySelector('.downvote').textContent;
    return parseInt(downvoteText.match(/\d+/)[0]);
}


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

// Post Voting
function votePost(pid, voteType) {
    fetch(`/api/post/${pid}/vote`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ vote: voteType })
    })
    .then(response => response.json())
    .then(data => {
        if (data.upvotes !== undefined && data.downvotes !== undefined) {
            document.querySelector(`.upvote[data-pid="${pid}"]`).textContent = `👍 ${data.upvotes} Upvote`;
            document.querySelector(`.downvote[data-pid="${pid}"]`).textContent = `👎 ${data.downvotes} Downvote`;
        }
    })
    .catch(error => console.error('Error voting:', error));
}