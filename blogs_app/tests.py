from django.test import TestCase
import pytest
from datetime import datetime
from blogs_app.models import Post, BlogComment
from home_app.models import User, Contact
from django.utils.text import slugify
from django.urls import reverse

# Create your tests here.
# Test cases for the models.py file
@pytest.mark.django_db
def test_create_post() :

    user = User.objects.create(username = "testuser", email = "testuser@gmail.com")
    post = Post.objects.create(title = "Test Post", content = "This is a test content.", author = user)

    assert post.title == "Test Post"
    assert post.content == "This is a test content."
    assert post.author == user
    assert post.created_at is not None
    assert isinstance(post.created_at, datetime)
    assert post.updated_at is not None
    assert isinstance(post.updated_at, datetime)

@pytest.mark.django_db
def test_slug_generation() :
    user = User.objects.create(username = "testuser", email = "testuser@gmail.com")
    post = Post.objects.create(title = "Test slug post", content = "This is content for slug test.", author = user)

    assert post.slug == slugify(post.title)

@pytest.mark.django_db
def test_unique_slug() :
    user = User.objects.create(username = "testuser", email = "testuser@gmail.com")

    post1 = Post.objects.create(title = "Test Post", content = "This is content for post1", author = user)
    post2 = Post.objects.create(title = "Test Post", content = "This is content for post2", author = user)

    assert post1.slug != post2.slug

@pytest.mark.django_db
def test_post_str_method() :
    user = User.objects.create(username = "testuser", email = "testuser@gmail.com")
    post = Post.objects.create(title = "Test Post", content = "This is content for test.", author = user)

    assert str(post) == "Test Post by testuser"

@pytest.mark.django_db
def test_create_blog_comment() :
    user = User.objects.create(username = "testuser", email = "testuser@gmail.com")
    post = Post.objects.create(title = "Test Post", content = "This is content for test.", author = user)

    comment = BlogComment.objects.create(comment = "This is a comment.", user = user, post = post)

    assert comment.comment == "This is a comment."
    assert comment.user == user
    assert comment.post == post
    assert comment.id is not None
    assert comment.created_at is not None
    assert isinstance(comment.created_at, datetime)

@pytest.mark.django_db
def test_comment_reply() :
    user = User.objects.create(username = "testuser", email = "testuser@gmail.com")
    post = Post.objects.create(title = "Test Post", content = "This is content for test.", author = user)

    parent_comment = BlogComment.objects.create(comment = "This is a parent comment.", user = user, post = post)
    child_comment1 = BlogComment.objects.create(comment = "This is a child comment 1.", user = user, post = post, parent = parent_comment)
    child_comment2 = BlogComment.objects.create(comment = "This is a child comment 2.", user = user, post = post, parent = parent_comment)

    assert child_comment1.parent == parent_comment
    assert child_comment2.parent == parent_comment
    assert parent_comment.replies.count() == 2

@pytest.mark.django_db
def test_blog_comment_str_method() :
    user = User.objects.create(username = "testuser", email = "testuser@gmail.com")
    post = Post.objects.create(title = "Test Post", content = "This is a test content.", author = user)

    comment = BlogComment.objects.create(comment = "This is a test comment.", user = user, post = post)
    assert str(comment) == "This is a ... by testuser"

# Test cases for views.py file
@pytest.mark.django_db
def test_login_required_for_blog_home(client) :
    response = client.get(reverse('blogHome'))
    assert response.status_code == 302

@pytest.mark.django_db
def test_login_required_for_create_blog(client) :
    response = client.get(reverse('create_blog'))
    assert response.status_code == 302

@pytest.mark.django_db
def test_login_required_for_edit_blog(client) :
    post = Post.objects.create(title = "Test Post", content = "This is test content.", author = User.objects.create(username = "testuser"))
    response = client.get(reverse('edit_post', kwargs={'slug':post.slug}))
    assert response.status_code == 302

@pytest.mark.django_db
def test_blog_home_view(client):
    # Create a user and post
    user = User.objects.create(username="testuser", password="password")
    post1 = Post.objects.create(title="Test Post 1", content="Test Content 1", author=user)
    post2 = Post.objects.create(title="Test Post 2", content="Test Content 2", author=user)

    # Manually log in by setting the session
    session = client.session
    session['username'] = user.username
    session.save()

    # Send the GET request to the blog home
    response = client.get(reverse('blogHome'))
    print(response)

    # Ensure the correct template is used
    assert response.status_code == 200
    assert 'blogs_app/home.html' in [template.name for template in response.templates]

    # Ensure all posts are in the context
    assert post1 in response.context['allPosts']
    assert post2 in response.context['allPosts']


@pytest.mark.django_db
def test_blog_home_view_redirect_when_not_logged_in(client):
    response = client.get(reverse('blogHome'))

    assert response.status_code == 302
    assert response.url == '/login'

@pytest.mark.django_db
def test_create_blog_view(client) :
    user = User.objects.create(username = "testuser", password = "testpassword")

    session = client.session
    session['username'] = user.username
    session.save()

    response = client.get(reverse('create_blog'))

    assert response.status_code == 200
    assert 'blogs_app/create_blog.html' in [template.name for template in response.templates]

    data = {'title' : 'New Test Post', 'content' : 'Test content for new post'}
    response = client.post(reverse('create_blog'), data)

    assert response.status_code == 302
    assert Post.objects.filter(title = 'New Test Post').exists()

@pytest.mark.django_db
def test_edit_post_view(client):
    user = User.objects.create(username="testuser", password = "testpassword")

    post = Post.objects.create(title="Original title", content="Original content", author=user)

    session = client.session
    session['username'] = user.username
    session.save()

    slug = post.slug  

    response = client.get(reverse('edit_post', kwargs={'slug': slug}))

    assert response.status_code == 200
    assert 'blogs_app/edit_post.html' in [template.name for template in response.templates]

    updated_data = {'title': 'Updated title', 'content': 'Updated Content'}

    response = client.post(reverse('edit_post', kwargs={'slug': slug}), updated_data)

    post.refresh_from_db()

    assert post.title == "Updated title"
    assert post.content == "Updated Content"  

    assert response.status_code == 302
    assert response.url == reverse('blog', kwargs={'slug': post.slug})

@pytest.mark.django_db
def test_post_comment_view(client) :
    user = User.objects.create(username = "testuser", password = "testpassword")
    post = Post.objects.create(title = "Test Post", content = "Test Content", author = user)

    session = client.session
    session['username'] = user.username
    session.save()

    data = {'comment' : 'This is a test comment.', 'postid' : post.id, 'pc_slug' : post.slug}
    response = client.post(reverse('post_comment'), data)
    
    assert response.status_code == 302
    assert BlogComment.objects.filter(comment = "This is a test comment.").exists()

    parent_comment = BlogComment.objects.first()
    data = {'comment' : 'This is a reply', 'postid' : post.id, 'parentid' : parent_comment.id, 'pc_slug' : post.slug}
    response = client.post(reverse('post_comment'), data)

    assert response.status_code == 302
    assert BlogComment.objects.filter(comment = "This is a reply").exists()

@pytest.mark.django_db
def test_delete_post_view(client) :
    user = User.objects.create(username = "testuser", password = "testpassword")
    post = Post.objects.create(title = "Test Post", content = "Test Content", author = user)

    session = client.session
    session['username'] = user.username
    session.save()

    response = client.get(reverse('delete_post', kwargs={'slug':post.slug}))

    assert response.status_code == 302
    assert not Post.objects.filter(id = post.id).exists()

@pytest.mark.django_db
def test_delete_comment_view(client) :
    user = User.objects.create(username = "testuser", password = "testpassword")
    post = Post.objects.create(title = "Test Post", content = "Test content", author = user)
    comment = BlogComment.objects.create(comment = "Test comment", user = user, post = post)

    session = client.session
    session['username'] = user.username
    session.save()

    response = client.get(reverse('delete_comment', kwargs = {'id' : comment.id}))

    assert response.status_code == 302

    assert not BlogComment.objects.filter(id = comment.id).exists()

@pytest.mark.django_db
def test_search_view(client) :
    user = User.objects.create(username = "testuser", password = "testpassword")
    post1 = Post.objects.create(title = "Test Post 1", content = "Test Content 1", author = user)
    post2 = Post.objects.create(title = "Test Post 2", content = "Test Content 2", author = user)
    
    session = client.session
    session['username'] = user.username
    session.save()

    response = client.get(reverse('search'), {'query' : 'Test Post 1'})

    assert response.status_code == 200
    assert post1 in response.context['allPosts']
    assert post2 not in response.context['allPosts']

    response = client.get(reverse('search'), {'query' : 'Non-existent Post'})
    assert "No search results found. Please refine your query." in [msg.message for msg in response.context['messages']]