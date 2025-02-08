from django.db import models
from home_app.models import User
from datetime import datetime
from django.utils.text import slugify

# Define the Post model for blog posts
class Post(models.Model):
    id = models.AutoField(primary_key=True)  # Auto-incremented field for each post
    title = models.CharField(max_length=255)  # Title of the post
    content = models.TextField()  # Content of the post (can be large text)
    
    # Establish a ForeignKey relationship with the User model
    # This means each post is associated with a single user (author).
    # If the user is deleted, their posts will be deleted too.
    author = models.ForeignKey(User, on_delete=models.CASCADE)  
    slug = models.SlugField(default="", null=False) # A unique slug for the post, typically used in URLs
    created_at = models.DateTimeField(default=datetime.now)  # Timestamp of when the post is created
    updated_at = models.DateTimeField(default=datetime.now)

    def __str__(self):
        """
        String representation of the Post model.
        Returns the title and the author's name for display.
        """
        return self.title + ' by ' + str(self.author)  # Show the post title and the author's name
    
    def save(self, *args, **kwargs):
        # Automatically generate the slug from the title before saving
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Ensure the slug is unique by checking for duplicates
        while Post.objects.filter(slug=self.slug).exists():
            self.slug = f"{self.slug}-{Post.objects.filter(slug=self.slug).count() + 1}"
        
        super(Post, self).save(*args, **kwargs)

class BlogComment(models.Model) :
    id = models.AutoField(primary_key=True)
    comment=models.TextField()
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    post=models.ForeignKey(Post, on_delete=models.CASCADE)
    parent=models.ForeignKey('self', related_name="replies", on_delete=models.CASCADE, null=True)
    created_at=models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.comment[0:10] + "... by " + self.user.username 