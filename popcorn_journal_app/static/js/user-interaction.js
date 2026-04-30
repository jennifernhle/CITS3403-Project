// JavaScript code for the logic behind user interactions

// User following/unfollowing another user
const followBtn = document.getElementById('follow-button');
if (followBtn) {
  followBtn.addEventListener('click', function() {
    const userId = this.dataset.userId; // Get the user ID from the button's data attribute
    const action = this.dataset.action; // Get the action (follow/unfollow) from the button's data attribute

    fetch(`/follow/${userId}/${action}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        // Update the button text and action based on the new state
        if (data.action === 'follow') {
          followBtn.textContent = 'Unfollow';
          followBtn.dataset.action = 'unfollow';
        } else {
          followBtn.textContent = 'Follow';
          followBtn.dataset.action = 'follow';
        }
        
        // Update the follower count dynamically
        const followerCountElement = document.getElementById('follower-count');
        if (followerCountElement) {
          followerCountElement.textContent = data.follower_count;
        }
      } else {
        alert('An error occurred. Please try again.');
      }
    })
    .catch(error => {
      console.error('Error:', error);
      alert('An error occurred. Please try again.');
    });
  });
}
