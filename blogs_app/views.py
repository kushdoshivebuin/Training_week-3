from datetime import datetime
from home_app.models import User
from blogs_app.models import Post, BlogComment
from django import forms
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

def login_required(view_func):
    """
    Decorator to ensure that a user is logged in before they can access certain views.
    
    If the user is not authenticated, they are redirected to the login page.
    """
    def _wrapped_view(request, *args, **kwargs):
        # Check if the user is logged in by looking for a 'username' in the session
        if 'username' not in request.session:
            return redirect('login')  # Redirect to the login page if not authenticated
        
        # Call the original view if the user is authenticated
        response = view_func(request, *args, **kwargs)
        
        # Add cache control headers to prevent caching
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate, proxy-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        
        return response
    
    return _wrapped_view


# Create your views here.
@login_required
def blogHome(request):
    """
    View to display the homepage with all blog posts.
    
    Retrieves all blog posts from the database and renders them in the 'home.html' template.
    """
    # Fetch all posts from the database
    allPosts = Post.objects.all()
    
    # Pass the posts and username as context to the template
    context = {
        'allPosts': allPosts,
        'username': request.session.get('username', None)  # Safely get username from session
    }
    
    # Render the template with the context
    return render(request, 'blogs_app/home.html', context)

@login_required
def blog(request, slug):
    """
    View to display a specific blog post based on its slug.
    
    Retrieves a blog post by its slug and renders it in the 'blogpost.html' template. 
    Also retrieves comments for the post, including replies.
    """
    # Retrieve the post with the given slug
    post = Post.objects.filter(slug=slug).first()
    
    # Fetch parent comments (comments without a parent) for the post
    parent_comments = BlogComment.objects.filter(post=post, parent__isnull=True)

    # Fetch replies for each parent comment
    for comment in parent_comments:
        comment.replies_list = BlogComment.objects.filter(parent=comment)

    context = {'post': post, 'comments': parent_comments, 'user': request.user}

    # Render the template with the context
    return render(request, 'blogs_app/blogpost.html', context)


class PostForm(forms.ModelForm):
    """
    Form class for creating or editing a blog post.
    
    This form includes the fields: title, content.
    """
    class Meta:
        model = Post
        fields = ['title', 'content']  

@login_required
def create_blog(request):
    """
    View to create a new blog post.
    
    The user must be logged in to access this view. Upon successful form submission,
    the blog post is saved, and the user is redirected to the blog homepage.
    """
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)  # Handle file uploads with request.FILES
        
        if form.is_valid():
            post = form.save(commit=False)
            
            # Get the logged-in user object
            user = User.objects.get(username=request.session['username'])
            
            # Set the 'author' field to the logged-in user
            post.author = user
            
            # Save the post to the database
            post.save()
            
            # Redirect to the blog home page after saving
            return redirect('blogHome')
    else:
        form = PostForm()

    return render(request, 'blogs_app/create_blog.html', {'form': form})

@login_required
def search(request):
    """
    View to handle search functionality for blog posts.
    
    Retrieves blog posts based on a search query that matches the title, author, or content.
    """
    query = request.GET.get('query', '').strip()
    
    if len(query) > 78:
        allPosts = Post.objects.none()
    else:
        # Filter posts by title, author username, or content
        allPostsTitle = Post.objects.filter(title__icontains=query)
        allPostsAuthor = Post.objects.filter(author__username__icontains=query)
        allPostsContent = Post.objects.filter(content__icontains=query)
        
        # Combine the querysets using union
        allPosts = allPostsTitle.union(allPostsAuthor, allPostsContent)

    # If no posts found, show a warning message
    if allPosts.count() == 0:
        messages.warning(request, "No search results found. Please refine your query.")
        
    params = {'allPosts': allPosts, 'query': query}
    return render(request, 'blogs_app/search.html', params)

@login_required
def edit_post(request, slug):
    """
    View to edit a specific blog post. The form is pre-filled with the current post data.
    
    Only the post's author is authorized to edit the post.
    """
    # Retrieve the post to be edited by slug
    post = get_object_or_404(Post, slug=slug)

    # Ensure only the post's author can edit it
    if post.author.username != request.session.get('username'):
        messages.error(request, "You are not authorized to edit this post.")
        return redirect('blogHome')

    if request.method == 'POST':
        # If the form is submitted, validate and save the changes
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post.updated_at = datetime.now()
            form.save()
            messages.success(request, "Your post has been updated successfully!")
            return redirect('blog', slug=post.slug)  # Redirect to the updated post page
    else:
        # Pre-populate the form with the post's current data
        form = PostForm(instance=post)

    context = {'form': form, 'post': post}
    return render(request, 'blogs_app/edit_post.html', context)


def post_comment(request):
    """
    View to handle posting a comment (or reply) to a blog post.
    
    Handles both parent comments and replies to existing comments.
    """
    if request.method == "POST":
        pc_comment = request.POST.get("comment")
        pc_user = request.session.get("username")
        pc_parentid = request.POST.get("parentid")  # Correctly fetch 'parentid'
        postid = request.POST.get('postid')
        pc_slug = request.POST.get("pc_slug")

        # Check if the user is logged in
        if not pc_user:
            messages.error(request, "You must be logged in to post a comment.")
            return redirect("/login")

        try:
            # Attempt to fetch the post using its id
            post = Post.objects.get(id=postid)
        except Post.DoesNotExist:
            messages.error(request, "The post you are trying to comment on does not exist.")
            return redirect("/blogs/home")

        if not pc_comment:
            messages.error(request, "Comment cannot be empty.")
            return redirect(f"/blogs/{pc_slug}")

        user_instance = User.objects.get(username=pc_user)

        # Check if it's a parent comment or a reply
        if pc_parentid:  # This means it's a reply
            try:
                parent_comment = BlogComment.objects.get(id=pc_parentid)
                comment = BlogComment(comment=pc_comment, user=user_instance, post=post, parent=parent_comment)
                comment.save()
                messages.success(request, "Your reply has been posted successfully")
            except BlogComment.DoesNotExist:
                messages.error(request, "Parent comment does not exist.")
                return redirect(f"/blogs/{pc_slug}")
        else:  # This means it's a parent comment
            comment = BlogComment(comment=pc_comment, user=user_instance, post=post)
            comment.save()
            messages.success(request, "Your comment has been posted successfully")

        return redirect(f"/blogs/{pc_slug}")
    
def page_not_found(request, exception):
    """
    Custom 404 error page.
    
    Render a '404.html' template when a page is not found.
    """
    return render(request, '404.html', status=404)

def delete_post(request, slug):
    """
    View to delete a blog post. Only the post's author can delete it.
    """
    # Get the post object based on the slug
    post = get_object_or_404(Post, slug=slug)

    if post.author.username == request.session.get('username'):
        post.delete()  # Delete the post from the database
    else:
        messages.error(request , "You are not allowed to delete this post!")
    
    return redirect('/blogs/home')

def delete_comment(request, id):
    """
    View to delete a comment. Only the comment's author or the post's author can delete it.
    
    If it's a parent comment, its replies are also deleted.
    """
    # Get the comment by its id
    comment = get_object_or_404(BlogComment, id=id)

    # Get the post associated with the comment
    post = comment.post
    
    # Check if the logged-in user is the author of the post or the comment
    if post.author.username == request.session.get('username') or comment.user.username == request.session.get('username'):
        # If it's a parent comment, delete all its replies as well
        if not comment.parent:  # Check if it's a parent comment
            comment.replies.all().delete()  # Delete all replies

        # Delete the parent comment
        comment.delete()
    else:
        messages.error(request , "You are not authorized to delete this!")

    return redirect('/blogs/home')
