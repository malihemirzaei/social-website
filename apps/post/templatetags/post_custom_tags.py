from urllib import request

from django import template
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from ..models import Post
from ...account.models import Friend_Request, User

register = template.Library()


@register.simple_tag(name='p_cnt')
def count_post(id):
    "count posts of user"
    return Post.objects.filter(account_id=id).count()


@register.simple_tag(name='l_cnt')
def count_like(pk):
    "count likes of post"
    post = Post.objects.get(pk=pk)
    return post.like_set.count()


@register.inclusion_tag('post/post_comments.html')
# @register.inclusion_tag('post/comment_list.html')
def show_comments(pk, user):
    "show comment of post"
    post = Post.objects.get(pk=pk)
    comments = post.comment_set.all()
    # paginator = Paginator(comments, 3)
    return {'comments': comments, 'user': user, 'post': post}

# @register.inclusion_tag('post/post_comments.html')
# # @register.inclusion_tag('post/comment_list.html')
# def show_comments(pk, user,request):
#     "show comment of post"
#     post = Post.objects.get(pk=pk)
#     comments = post.comment_set.all()
#     page = request.GET.get('page', 1)
#
#     paginator = Paginator(comments, 10)
#     try:
#         comments = paginator.page(page)
#     except PageNotAnInteger:
#         comments = paginator.page(1)
#     except EmptyPage:
#         comments = paginator.page(paginator.num_pages)
#     return {'comments': comments, 'user': user, 'post': post}



@register.inclusion_tag('post/following_post.html')
def show_posts(user):
    posts = []
    # fc=[]
    # person = User.objects.get(id=pk)
    following = user.followed.all()
    if following:
        for f in following:

            f1 = User.objects.get(email=f)
            for post in f1.post_set.all():
                posts.append(post)

        return {'posts': posts}

    # else:
    #     # return render(request, 'post/following_post.html')
    #     return render(request, 'account/user-profile.html')


# @register.inclusion_tag('account/following.html')
# def following_list(user):
#     # person = User.objects.get(id=pk)
#     users = user.followed.all()
#     return {'users': users}


@register.inclusion_tag('post/user_post.html')
def user_post(user):
    "show post of user"
    posts = user.post_set.all()
    return {'posts': posts}

# @register.inclusion_tag('account/user_detail.html')
# def check_request(pk):
#     "show comment of post"
#     req = Friend_Request.objects.get(from_user_id=pk)
#     # comments = post.comment_set.all()
#     return {'comments': comments}
