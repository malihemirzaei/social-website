from django import template


from apps.account.models import User

register = template.Library()


@register.simple_tag(name='follower_cnt')
def count_follower(request):
    user = User.objects.get(id=request.user.id)
    return user.follower.count()


@register.simple_tag(name='following_cnt')
def count_followed(request):
    account = User.objects.get(id=request.user.id)
    return account.followed.count()

