document.addEventListener("DOMContentLoaded", function() {
    const urlParams = new URLSearchParams(window.location.search);
    const pid = urlParams.get('pid');
    const dataform = document.getElementById("data");

    const current_user = dataform.getAttribute("data-currentuser");
    console.log(current_user);

    dataform.remove();
    if (!pid) {
        alert("No post ID provided.");
        window.location.href = "/";
    }

    // Handle new comment submission
    const addCommentForm = document.getElementById("add-comment-form");
    addCommentForm.addEventListener("submit", function(event) {
        event.preventDefault();
        const content = document.getElementById("new-comment").value.trim();
        if (!content) {
            alert("Comment cannot be empty.");
            return;
        }

        fetch(`/api/reply/`, {
                method: "POST",
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    'content': content,
                    'post_id': pid
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.cid) {
                    // Add the new comment to the comments list
                    addCommentToList(data);
                    document.getElementById("new-comment").value = "";
                } else {
                    alert(data.message || "Failed to add comment.");
                }
            })
            .catch(error => {
                console.error('Error adding comment:', error);
                alert("An error occurred while adding the comment.");
            });
    });

    function addCommentToList(reply) {
        const commentsList = document.getElementById("comments-list");
        const commentDiv = document.createElement('div');
        commentDiv.className = 'comment';
        commentDiv.setAttribute('data-cid', reply.cid);
        if(current_user === reply.author_name){
            commentDiv.innerHTML = `
                <div class="comment-header">
                    <img src="/static/images/userdefaultimage.png" width="40" height="40" alt="User Profile Picture" class="profile-pic">
                    <p class="user-name">
                        <a href="/profile/${reply.author_name}" class="user-link">${reply.author_name}</a>
                    </p>
                    <p class="comment-time">${new Date(reply.created_at).toLocaleString()}</p>
                </div>
                <div class="comment-content">
                    <p class="comment-text">${reply.content}</p>
                    <div class="comment-actions">
                        <a href="#" class="pure-button pure-button-small upvote-button" data-cid="${reply.cid}">Upvote</a>
                        <a href="#" class="pure-button pure-button-small downvote-button" data-cid="${reply.cid}">Downvote</a>
                        <button class="pure-button pure-button-small" onclick="editreply(${reply.cid},${pid})">Edit</button>
                        <button class="pure-button pure-button-small" onclick="deletereply(${reply.cid},${pid})">Delete</button>
                        <span class="reply-upvotes">${reply.upvotes}</span> Upvotes
                        <span class="reply-downvotes">${reply.downvotes}</span> Downvotes
                    </div>
                </div>
            `;
            } else {
                commentDiv.innerHTML = `
                <div class="comment-header">
                    <img src="/static/images/userdefaultimage.png" width="40" height="40" alt="User Profile Picture" class="profile-pic">
                    <p class="user-name">
                        <a href="/profile/${reply.author_name}" class="user-link">${reply.author_name}</a>
                    </p>
                    <p class="comment-time">${new Date(reply.created_at).toLocaleString()}</p>
                </div>
                <div class="comment-content">
                    <p class="comment-text">${reply.content}</p>
                    <div class="comment-actions">
                        <a href="#" class="pure-button pure-button-small upvote-button" data-cid="${reply.cid}">Upvote</a>
                        <a href="#" class="pure-button pure-button-small downvote-button" data-cid="${reply.cid}">Downvote</a>
                        <span class="reply-upvotes">${reply.upvotes}</span> Upvotes
                        <span class="reply-downvotes">${reply.downvotes}</span> Downvotes
                    </div>
                </div>
                `;
        }
        commentsList.prepend(commentDiv);

        // Add event listeners to the new upvote/downvote buttons
        commentDiv.querySelector('.upvote-button').addEventListener('click', function(event) {
            event.preventDefault();
            const cid = this.getAttribute('data-cid');
            voteReply(cid, 'upvote', this);
        });
        commentDiv.querySelector('.downvote-button').addEventListener('click', function(event) {
            event.preventDefault();
            const cid = this.getAttribute('data-cid');
            voteReply(cid, 'downvote', this);
        });
    }

    // Handle filter options
    const filterSelect = document.getElementById("filter-select");
    filterSelect.addEventListener("change", function() {
        const filter = this.value;
        fetchReplies(pid, filter);
    });

    function fetchReplies(pid, filter = 'all') {
        let url = `/api/reply?pid=${pid}`;
        if (filter === 'upvotes') {
            url += '&sort=upvotes';
        } else if (filter === 'downvotes') {
            url += '&sort=downvotes';
        } else if (filter === 'newest') {
            url += '&sort=newest';
        } else if (filter === 'oldest') {
            url += '&sort=oldest';
        }

        fetch(url)
            .then(response => response.json())
            .then(replies => {
                if (Array.isArray(replies)) {
                    updateCommentsList(replies);
                } else {
                    console.error('Error fetching replies:', replies.message);
                }
            })
            .catch(error => console.error('Error fetching replies:', error));
    }

    function updateCommentsList(replies) {
        const commentsList = document.getElementById("comments-list");
        commentsList.innerHTML = '';
        replies.forEach(reply => {
            const commentDiv = document.createElement('div');
            commentDiv.className = 'comment';
            commentDiv.setAttribute('data-cid', reply.cid);
            if(current_user === reply.author_name){
            commentDiv.innerHTML = `
                <div class="comment-header">
                    <img src="/static/images/userdefaultimage.png" width="40" height="40" alt="User Profile Picture" class="profile-pic">
                    <p class="user-name">
                        <a href="/profile/${reply.author_name}" class="user-link">${reply.author_name}</a>
                    </p>
                    <p class="comment-time">${new Date(reply.created_at).toLocaleString()}</p>
                </div>
                <div class="comment-content">
                    <p class="comment-text">${reply.content}</p>
                    <div class="comment-actions">
                        <a href="#" class="pure-button pure-button-small upvote-button" data-cid="${reply.cid}">Upvote</a>
                        <a href="#" class="pure-button pure-button-small downvote-button" data-cid="${reply.cid}">Downvote</a>
                        <button class="pure-button pure-button-small" onclick="editreply(${reply.cid},${pid})">Edit</button>
                        <button class="pure-button pure-button-small" onclick="deletereply(${reply.cid},${pid})">Delete</button>
                        <span class="reply-upvotes">${reply.upvotes}</span> Upvotes
                        <span class="reply-downvotes">${reply.downvotes}</span> Downvotes
                    </div>
                </div>
            `;
            } else {
                commentDiv.innerHTML = `
                <div class="comment-header">
                    <img src="/static/images/userdefaultimage.png" width="40" height="40" alt="User Profile Picture" class="profile-pic">
                    <p class="user-name">
                        <a href="/profile/${reply.author_name}" class="user-link">${reply.author_name}</a>
                    </p>
                    <p class="comment-time">${new Date(reply.created_at).toLocaleString()}</p>
                </div>
                <div class="comment-content">
                    <p class="comment-text">${reply.content}</p>
                    <div class="comment-actions">
                        <a href="#" class="pure-button pure-button-small upvote-button" data-cid="${reply.cid}">Upvote</a>
                        <a href="#" class="pure-button pure-button-small downvote-button" data-cid="${reply.cid}">Downvote</a>
                        <span class="reply-upvotes">${reply.upvotes}</span> Upvotes
                        <span class="reply-downvotes">${reply.downvotes}</span> Downvotes
                    </div>
                </div>
            `;
            }
            commentsList.appendChild(commentDiv);
            // Add event listeners for upvote/downvote buttons
            commentDiv.querySelector('.upvote-button').addEventListener('click', function(event) {
                event.preventDefault();
                const cid = this.getAttribute('data-cid');
                voteReply(cid, 'upvote', this);
            });
            commentDiv.querySelector('.downvote-button').addEventListener('click', function(event) {
                event.preventDefault();
                const cid = this.getAttribute('data-cid');
                voteReply(cid, 'downvote', this);
            });
        });
    }

    // Initial fetch of replies
    fetchReplies(pid);

    // Handle voting on post
    const postUpvoteButton = document.querySelector('.upvote-button[data-pid]');
    const postDownvoteButton = document.querySelector('.downvote-button[data-pid]');

    if (postUpvoteButton && postDownvoteButton) {
        postUpvoteButton.addEventListener('click', function(event) {
            event.preventDefault();
            const pid = this.getAttribute('data-pid');
            votePost(pid, 'upvote', this);
        });

        postDownvoteButton.addEventListener('click', function(event) {
            event.preventDefault();
            const pid = this.getAttribute('data-pid');
            votePost(pid, 'downvote', this);
        });
    }

    function votePost(pid, voteType, buttonElement) {
        fetch(`/api/post/${pid}/vote`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    'vote': voteType
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.upvotes !== undefined && data.downvotes !== undefined) {
                    document.getElementById('post-upvotes').innerText = data.upvotes;
                    document.getElementById('post-downvotes').innerText = data.downvotes;
                } else {
                    alert(data.message || "Failed to vote.");
                }
            })
            .catch(error => {
                console.error('Error voting on post:', error);
                alert("An error occurred while voting.");
            });
    }

    function voteReply(cid, voteType, buttonElement) {
        fetch(`/api/reply/${cid}/vote`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    'vote': voteType
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.upvotes !== undefined && data.downvotes !== undefined) {
                    const commentDiv = buttonElement.closest('.comment');
                    commentDiv.querySelector('.reply-upvotes').innerText = data.upvotes;
                    commentDiv.querySelector('.reply-downvotes').innerText = data.downvotes;
                } else {
                    alert(data.message || "Failed to vote.");
                }
            })
            .catch(error => {
                console.error('Error voting on reply:', error);
                alert("An error occurred while voting.");
            });
    }

    // Toggle Sidebar Menu (if applicable)
    const hamburger = document.querySelector('.hamburger');
    if (hamburger) {
        hamburger.addEventListener('click', toggleMenu);
    }

    function toggleMenu() {
        const sidebar = document.querySelector('.sidebar');
        sidebar.classList.toggle('sidebar-active');
    }
});


function deletereply(cid,post_id){
    cf = confirm("Are you sure you want to delete this reply?")
    if(cf){
        console.log(`Deleting Reply: ${cid}`)
        url = '/api/reply/' + cid
        fetch(url,{method:'DELETE'})
        .then(response => response.json())
        .then(data => {
                        if(data.code == 200){
                            alert("delete successful")
                            window.location.href = `/viewpost?pid=${post_id}`
                        } else {
                            console.error('Error Deleting Reply:')
                        }
        })
        .catch(error => console.error('Error Deleting Reply:', error))
    }
}
function editreply(cid,post_id){
    window.location.href = `/editreply/${cid}?pid=${post_id}`;
}