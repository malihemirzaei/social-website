from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import DetailView, ListView, CreateView, RedirectView, UpdateView
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string

from .helper import get_random_otp, send_otp, check_otp_expiration
from .tokens import account_activation_token
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from apps.account.form import AccountCreationForm, UserUpdateForm

from apps.account.models import User, Following, Friend_Request
from django.contrib import messages, auth


class RegisterView(CreateView):
    form_class = AccountCreationForm
    template_name = 'account/register_user.html'

    def post(self, request, **kwargs):
        if request.method == 'POST':
            form = AccountCreationForm(request.POST, request.FILES or None)
            if form.is_valid():
                user = form.save(commit=False)
                if user.reg_type == 'email':
                    # user.username = form.email
                    user.is_active = False
                    user.save()
                    current_site = get_current_site(request)
                    mail_subject = 'Activate your  account.'
                    message = render_to_string('account/acc_active_email.html', {
                        'user': user,
                        'domain': current_site.domain,
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)).encode().decode(),
                        'token': account_activation_token.make_token(user),
                    })
                    to_email = form.cleaned_data.get('email')
                    email = EmailMessage(
                        mail_subject, message, to=[to_email]
                    )
                    email.send()
                    return HttpResponse('Please confirm your email address to complete the registration')
                else:
                    try:
                        mobile = request.POST.get('phone_number')
                        if User.objects.get(phone_number='mobile'):
                            user = User.objects.get(phone_number='mobile')
                            # send otp
                            otp = get_random_otp()
                            # send_otp(mobile, otp)
                            # save otp
                            print(otp)
                            user.otp = otp
                            user.save()
                            request.session['user_mobile'] = user.mobile
                            return HttpResponseRedirect(reverse('verify'))
                        else:
                            return HttpResponse('phone number is empty')

                    except User.DoesNotExist:
                        # user.username = form['phone_number']
                        mobile = request.POST.get('phone_number')
                        otp = get_random_otp()
                        send_otp(mobile, otp)
                        print(otp)
                        user.otp = otp
                        user.is_active = False
                        user.save()
                        request.session['user_mobile'] = user.phone_number
                        return HttpResponseRedirect(reverse('verify'))

            else:
                form = AccountCreationForm()
            return render(request, 'account/register_user.html', {'form': form})


def verify(request):
    try:
        mobile = request.session.get('user_mobile')
        if mobile == None:
            messages.error('mobile is empty ')
            # return HttpResponseRedirect(reverse('verify'))

        user = User.objects.get(phone_number=mobile)
        if request.method == "POST":

            # check otp expiration
            if not check_otp_expiration(user.phone_number):
                messages.error(request, "OTP is expired, please try again.")
                return HttpResponseRedirect(reverse('register'))

            if user.otp != int(request.POST.get('otp')):
                messages.error(request, "OTP is incorrect.")
                return HttpResponseRedirect(reverse('verify'))

            user.is_active = True
            user.save()
            login(request, user)
            return HttpResponseRedirect(reverse('profile'))

        return render(request, 'account/verify.html', {'mobile': mobile})

    except User.DoesNotExist:
        messages.error(request, "Error accorded, try again.")
        return HttpResponseRedirect(reverse('register'))


class ActivateView(View):
    def get(self, request, uidb64, token):

        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            login(request, user)
            return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
        else:
            return HttpResponse('Activation link is invalid!')


class UserList(ListView):
    """
        show list of users
    """
    model = User
    paginate_by = 4

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class UserDetail(DetailView):
    """
        show detail of users
    """
    model = User

    # req = Friend_Request.from_user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class Search(View):
    """
    The account can search among other users
    """

    def get(self, request):
        search_text = request.GET.get('search_text')
        users = None
        results = User.objects.exclude(id=request.user.id)  # name of the active account is not displayed in the list
        if search_text:
            users = User.objects.filter(email__icontains=search_text)
        return render(request, 'account/search.html', {'users': users, "results": results})


class LogoutView(RedirectView):
    """
    Provides users the ability to logout
    """
    url = reverse_lazy('login')

    def get(self, request, *args, **kwargs):
        auth.logout(request)
        # messages.success(request, 'You are now logged out')
        return super(LogoutView, self).get(request, *args, **kwargs)


class UserName(View):
    """
    To display each account's name in their profile
    """

    def get(self, request):
        username = User.email
        return render(request, 'account/profile.html', {'username': username})


class FollowersList(LoginRequiredMixin, View):
    """
    Each account can see their list of followers
    """

    def get(self, request):
        person = User.objects.get(id=request.user.id)
        users = person.follower.all()
        context = {'users': users, 'username': person.email}
        return render(request, 'account/follower_list.html', context)


class FollowingList(View):
    """
    Each account can see their list of following
    """

    def get(self, request):
        person = User.objects.get(id=request.user.id)
        users = person.followed.all()
        context = {'users': users, 'username': person.email}
        return render(request, 'account/followed_list.html', context)


class UpdateUser(UpdateView):
    model = User
    form_class = UserUpdateForm
    success_url = '/'
    template_name = 'account/edit_user.html'


@login_required
def send_friend_request(request, userID):
    from_user = request.user
    to_user = User.objects.get(id=userID)
    friend_request, created = Friend_Request.objects.get_or_create(from_user=from_user, to_user=to_user)
    if created:
        messages.error(request, "request sent")
        return HttpResponseRedirect(reverse('profile'))  # return HttpResponse('request sent')
    else:
        messages.error(request, "request was already sent")
        return HttpResponseRedirect(reverse('profile'))
        # return HttpResponse('request was already sent')


@login_required
def accept_friend_request(request, requestID):
    friend_request = Friend_Request.objects.get(id=requestID)
    if friend_request.to_user == request.user:
        friend_request.to_user.friends.add(friend_request.from_user)
        friend_request.from_user.friends.add(friend_request.to_user)
        friend_request.delete()
        to_user = friend_request.to_user
        from_user = friend_request.from_user
        # main_user = User.objects.get(id=request.user.id)
        # to_follow = User.objects.get(pk=pk)
        following = Following.objects.filter(user=from_user, followed=to_user)
        followerr = Following.objects.filter(user=to_user, follower=from_user)
        is_following = True if following else False
        is_followerr = True if followerr else False

        if not is_following:
            Following.follow(from_user, to_user)

        if not is_followerr:
            Following.follow_back(to_user, from_user)
        messages.error(request, "request accepted")
        return HttpResponseRedirect(reverse('profile'))
        # return HttpResponse('request accepted')
    else:
        messages.error(request, "request not accepted")
        return HttpResponseRedirect(reverse('profile'))
        # return HttpResponse('request not accepted')


class RequestList(View):

    def get(self, request):
        person = User.objects.get(id=request.user.id)
        users = person.to_user.all()
        context = {'users': users, 'username': person.email}
        return render(request, 'account/requests.html', context)
