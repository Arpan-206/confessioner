
import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import (HttpResponseBadRequest,
                         HttpResponseForbidden, HttpResponseNotAllowed,
                         HttpResponseNotFound, HttpResponseRedirect,
                         JsonResponse)
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .models import *

# Create your views here.


def index(request):
    return render(request, 'main/index.html')


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if not request.user.is_anonymous:
        return HttpResponseRedirect(reverse('index'))
    if request.method == 'GET':
        return render(request, 'main/register.html', {'title': 'Register'})
    elif request.method == 'POST':
        email = request.POST["email"]
        username = request.POST["username"]
        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirm"]
        if password != confirmation:
            return render(request, "main/register.html", {
                "message": "Passwords must match."
            })

        try:
            if request.POST["tos-switch"] != 'on':
                return render(request, "main/register.html", {
                    "message": "You didn't agree to our terms of service and privacy policy."
                })
        except:
            return render(request, "main/register.html", {
                "message": "You didn't agree to our terms of service and privacy policy."
            })

        if username == '':
            return render(request, "main/register.html", {
                "message": "Username missing."
            })
        elif password == '':
            return render(request, "main/register.html", {
                "message": "Password missing."
            })
        elif confirmation == '':
            return render(request, "main/register.html", {
                "message": "Confirm Password missing."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "main/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))


def login_view(request):
    if not request.user.is_anonymous:
        return HttpResponseRedirect(reverse('index'))
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]

        if username == '':
            return render(request, "main/login.html", {
                "message": "Username missing."
            })
        elif password == '':
            return render(request, "main/login.html", {
                "message": "Password missing."
            })

        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "main/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "main/login.html")


@login_required
def confess(request):
    users_comms = Member.objects.filter(user=request.user)
    if request.method == "GET":
        return render(request, 'main/confess.html', {'communities': users_comms})
    elif request.method == "POST":
        title = request.POST["title"]
        confession = request.POST["confession"]
        community_name = request.POST["community"]
        community = Community.objects.filter(name=community_name)[0]
        confession_obj = Confession.objects.create(
            title=title, content=confession, community=community)
        return HttpResponseRedirect(reverse('confession', kwargs={"id": confession_obj.id}))


@login_required
def confession(request, id):
    try:
        confession = Confession.objects.filter(id=id)[0]
        user_member = Member.objects.filter(
            user=request.user, community=confession.community)
        if len(user_member) == 0:
            return HttpResponseForbidden("You are not a member of this community.")
        conf_dict = {}
        if confession.title != '':
            conf_dict["title"] = confession.title
        conf_dict['confession_content'] = confession.content
        conf_dict['created'] = confession.created_at
        conf_dict['id'] = str(id)
        likes = len(Like.objects.filter(confession=confession))
        my_like = Like.objects.filter(
            user=request.user, confession=confession)
        if len(my_like) == 1:
            is_liked = True
        else:
            is_liked = False
        conf_dict['is_liked'] = is_liked
        conf_dict['likes'] = likes
        comments = Comment.objects.filter(confession=confession)
        conf_dict['comments'] = comments
        conf_dict['approved'] = confession.approved
        return render(request, "main/confession.html", conf_dict)
    except IndexError:
        return HttpResponseNotFound("Confession Not found")


@login_required
def toggle_like(request, id):
    if request.method != "GET":
        return HttpResponseBadRequest("Method not allowed")
    user = request.user
    like_obj = Like.objects.filter(
        user=user, confession=Confession.objects.filter(id=id)[0])
    if len(like_obj) == 1:
        like_obj.delete()
        likes = len(Like.objects.filter(
            confession=Confession.objects.filter(id=id)[0]))
        return JsonResponse({'message': 'Like removed successfully', 'op_code': 2, 'likes': likes})
    elif len(like_obj) == 0:
        lbj = Like.objects.create(
            user=user, confession=Confession.objects.filter(id=id)[0])
        likes = len(Like.objects.filter(
            confession=Confession.objects.filter(id=id)[0]))
        return JsonResponse({'message': 'Like added successfully', 'op_code': 1, 'likes': likes})


@login_required
def communities(request):
    if request.method != "GET":
        return HttpResponseNotAllowed("Method not allowed")
    member_obj = Member.objects.filter(user=request.user)
    return render(request, "main/communities.html", {"member_obj": member_obj})


@login_required
@csrf_exempt
def comment(request, id):
    if request.method != "POST":
        return HttpResponseNotAllowed("Method not allowed")
    user = request.user
    content_dict = json.loads(request.body)
    content = content_dict["content"]
    if content.strip() == '':
        return JsonResponse({"message": "Nothing to do.", "op_code": -2})
    confession_obj = Confession.objects.filter(id=id)[0]
    user_mem = Member.objects.filter(
        user=user, community=confession_obj.community)
    if len(user_mem) == 0:
        return JsonResponse({"message": "You are not a part of this community.", "op_code": -1})
    comment_obj = Comment.objects.create(
        content=content, author=user, anonymous=content_dict["anonymous"], confession_id=id)
    return JsonResponse({"message": "Comment added!", "op_code": 1})

@login_required
@csrf_exempt
def create_community(request):
    if request.method != "POST":
        return HttpResponseNotAllowed("Method not allowed")

    try:
        content_dict = json.loads(request.body)
        name = content_dict["name"]
        description = content_dict["description"]
        if name.strip() == '':
            return JsonResponse({"message": "Nothing to do.", "op_code": -2})
        community_obj = Community.objects.create(name=name, description=description, owner=request.user)
        member_obj = Member.objects.create(user=request.user, community=community_obj, is_mod=True)

        return JsonResponse({"message": f"Community created with code {community_obj.join_code}", "op_code": 1, "community": community_obj.name, "community_id": community_obj.id, "join_code": community_obj.join_code})
    except:
        return JsonResponse({"message": "Something went wrong.", "op_code": -1})

@login_required
def community_view(request, id):
    community_obj = Community.objects.filter(id=id)[0]
    community_member = Member.objects.filter(
        community=community_obj, user=request.user)
    if len(community_member) == 0:
        return HttpResponseNotAllowed("You are not a member of this community.")
    confessions = Confession.objects.filter(
        community=community_obj).order_by('-created_at')
    vetted_confessions = []
    for confession in confessions:
        if confession.approved:
            vetted_confessions.append(confession)
    return render(request, "main/community.html", {"community": community_obj, "confessions": vetted_confessions, "members": len(community_member)})


@login_required
@csrf_exempt
def join_comm(request):
    if request.method == "GET":
        return render(request, "main/join.html", {'joining': True})
    elif request.method == "POST":
        code = json.loads(request.body)['code'].strip()
        comm_objs = Community.objects.filter(join_code=code)
        if len(comm_objs) != 1:
            return JsonResponse({"message": "Community with that code not found!", "op_code": -4})
        community = comm_objs[0]
        mem_objs = Member.objects.filter(
            community=community, user=request.user)
        if len(mem_objs) != 0:
            return JsonResponse({"message": "You are already a member", "op_code": -3})
        pending_req = JoinRequest.objects.filter(
            user=request.user, community=community)
        if len(pending_req) != 0:
            return JsonResponse({"message": "You already have a pending request to this community.", "op_code": -2})

        join_req = JoinRequest.objects.create(
            user=request.user, community=community)
        return JsonResponse({'message': 'Request sent successfully.', 'op_code': 1})

@login_required
def comm_mod(request, id):
    if request.method != "GET":
        return HttpResponseNotAllowed("Method not allowed")

    community_obj = Community.objects.filter(id=id)
    if len(community_obj) != 1:
        return HttpResponseNotFound("Community not found")
    community_obj = community_obj[0]
    member_usr = Member.objects.filter(user=request.user, community=community_obj)
    if len(member_usr) != 1:
        return HttpResponseNotFound("You are not a member of this community")
    member_usr = member_usr[0]
    if not member_usr.is_mod:
        return HttpResponseNotAllowed("You are not a moderator")
    members = Member.objects.filter(community=community_obj)
    join_requests = JoinRequest.objects.filter(community=community_obj) 
    return render(request, "main/community_mod.html", {"community": community_obj, "members": members, "join_requests": join_requests})

@login_required
@csrf_exempt
def comm_mod_add(request, id):
    if request.method != "POST":
        return HttpResponseNotAllowed("Method not allowed")
    community_obj = Community.objects.filter(id=id)[0]
    if request.user != community_obj.owner:
        return HttpResponseForbidden("You are not the owner of this community")
    member_obj = Member.objects.filter(user=request.user, community=community_obj)
    if len(member_obj) != 1:
        return JsonResponse({"message": "You are not a member of this community", "op_code": -1})
    member_obj = member_obj[0]
    if not member_obj.is_mod:
        return JsonResponse({"message": "You are not a moderator", "op_code": -2})
    username = json.loads(request.body)['username']
    user_obj = User.objects.filter(username=username)[0]
    member_obj = Member.objects.filter(user=user_obj, community=community_obj)
    if len(member_obj) != 1:
        return JsonResponse({"message": "User is not a member of this community", "op_code": -3})
    member_obj = member_obj[0]
    member_obj.is_mod = True
    member_obj.save()
    return JsonResponse({"message": "User promoted successfully", "op_code": 1})

@login_required
@csrf_exempt
def comm_mod_remove(request, id):
    if request.method != "POST":
        return HttpResponseNotAllowed("Method not allowed")
    community_obj = Community.objects.filter(id=id)[0]
    member_obj = Member.objects.filter(user=request.user, community=community_obj)
    if request.user != community_obj.owner:
        return HttpResponseForbidden("You are not the owner of this community")
    if len(member_obj) != 1:
        return JsonResponse({"message": "You are not a member of this community", "op_code": -1})
    member_obj = member_obj[0]
    if not member_obj.is_mod:
        return JsonResponse({"message": "You are not a moderator", "op_code": -2})
    username = json.loads(request.body)['username']
    user_obj = User.objects.filter(username=username)[0]
    member_obj = Member.objects.filter(user=user_obj, community=community_obj)
    if len(member_obj) != 1:
        return JsonResponse({"message": "User is not a member of this community", "op_code": -3})
    member_obj = member_obj[0]
    member_obj.is_mod = False
    member_obj.save()
    return JsonResponse({"message": "User removed successfully", "op_code": 1})

def tos(request):
    return render(request, "main/tos.html")


def privacy(request):
    return render(request, "main/privacy.html")
