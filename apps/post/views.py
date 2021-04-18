from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import CreateView, DetailView, UpdateView, ListView

from .forms import PostForm
from .models import Post, Like, Comment
from ..account.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages


class MyPostList(View):
    def get(self, request):
        """
        :param request: request to show user's posts
        :return: title list of user's posts
        """
        user = request.user
        my_post_list = Post.objects.filter(account_id=user)
        context = {'my_post_list': my_post_list}
        return render(request, 'post/my_post_list.html', context)
        # return render(request, 'account/profile.html', context)


class PostDetail(DetailView):
    """
    show detail of post.
    """
    model = Post
    template_name = 'post/post_detail.html'
    context_object_name = 'post'


class AddPostView(LoginRequiredMixin, CreateView):
    """
    add new post
    """
    form_class = PostForm
    template_name = 'post/add_new_post.html'
    success_url = '/profile/'

    def post(self, request, **kwargs):
        form = PostForm(request.POST, request.FILES or None)
        if form.is_valid():
            post = Post(**form.cleaned_data, account_id=request.user)
            if post.image or post.content:
                post.save()
                messages.success(request, "Post saved!")
            else:
                messages.error(request, "Enter image or text!")
            return redirect('profile')
        return render(request, 'post/add_new_post.html')


def success(request):
    return HttpResponse('successfully uploaded')


def like(request, pk):
    """

    Like other users' posts
    """
    main_user = request.user
    to_like = Post.objects.get(pk=pk)
    if Like.objects.filter(post_id_id=to_like.id, user_id_id=main_user.id):
        return redirect('post_detail', pk=pk)
    else:
        like = Like(post_id_id=to_like.id, user_id_id=main_user.id)
        like.save()
        return redirect('post_detail', pk=pk)


class AddComment(View):
    """

Leave a comment for other users' posts
    """

    def post(self, request, pk):
        user_obj = request.user
        to_comment = Post.objects.get(pk=pk)
        note = request.POST.get("note")
        # is_comment = request.POST.get("comment_btn")
        if note:
            comment = Comment.objects.create(note=note, post_id_id=to_comment.id, user_id_id=user_obj.id)
            comment.save()
        return redirect('post_detail', pk=pk)


class CommentList(ListView):
    model = Comment




class FollowingPost(View):
    """
    Each user can see other users' posts in their profile
    """

    def get(self, request):
        posts = []
        person = request.user
        following = person.followed.all()
        if following:
            for f in following:
                f1 = User.objects.get(email=f)
                for post in f1.post_set.all():
                    posts.append(post)
            context = {'posts': posts, 'username': person.email}
            return render(request, 'account/user-profile.html', context)
            # return render(request, 'post/following_post.html', context)
        else:
            # return render(request, 'post/following_post.html')
            return render(request, 'account/user-profile.html')


class UpdatePost(UpdateView):
    model = Post
    template_name = 'post/edit_post.html'
    fields = ['title', 'content', 'image']
    success_url = '/post/'


def post_delete(request, pk):
    post = Post.objects.get(pk=pk)
    post.delete()
    return redirect('post_detail', pk=pk)


def comment_delete(request, pk):
    instance = get_object_or_404(Comment, pk=pk)
    pk = instance.post_id.pk
    instance.delete()  # or save edits
    # messages.success(request, "Successfully Deleted")
    return redirect('post_detail', pk=pk)
