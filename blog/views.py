from re import I
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from .models import Post
from .forms import CommentForm
from django.views import View
from django.http import HttpResponseRedirect
from django.urls import reverse

all_posts = Post.objects.all().order_by("-date")


# Create your views here.

class StartingPageView(ListView):
    model = Post
    template_name = "blog/index.html"
    ordering = ["-date"]
    context_object_name = "posts"

    def get_queryset(self):
        query_set = super().get_queryset()
        data = query_set[:3]
        return data


# def starting_page(request):
#     latest_posts = Post.objects.all().order_by("-date")[:3]

#     return render(request, "blog/index.html", {
#         "posts": latest_posts
#     })


class AllPostsView(ListView):
    model = Post
    template_name = "blog/all-posts.html"
    context_object_name = "all_posts"
    ordering = ["-date"]


# def posts(request):
#     return render(request, "blog/all-posts.html", {
#         "all_posts": all_posts
#     })


class PostDetailView(View):
    def get(self, request, slug):
        post = Post.objects.get(slug=slug)
        context = {
            "post": post,
            "post_tags": post.tag.all(),
            "comment_form": CommentForm(),
            "comments": post.comments.all().order_by("-id")
        }
        return render(request, "blog/post-detail.html", context)

    def post(self, request, slug):
        post = Post.objects.get(slug=slug)
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.save()
            return HttpResponseRedirect(reverse("post-detail-page", args=[slug]))

        context = {
            "post": post,
            "post_tags": post.tag.all(),
            "comment_form": comment_form,
            "comments": post.comments.all().order_by("-id")
        }

        return render(request, "blog/post-detail.html", context)

    # def get_context_data(self, **kwargs):
    #     context= super().get_context_data(**kwargs)
    #     context["post_tags"]= self.object.tag.all()
    #     context["comment_form"]= CommentForm()
    #     return context

# def post_details(request, slug):
#     identified_post = get_object_or_404(Post, slug=slug)
#     return render(request, "blog/post-detail.html", {
#         "post": identified_post,
#         "post_tags": identified_post.tag.all()
#     })


class ReadLaterView(View):
    def get(self, request):
        stored_posts = request.session.get("stored_posts")
        context={}
        
        if stored_posts is None or len(stored_posts) == 0:
            context["posts"]= []
            context["has_posts"]= False
        else:
            posts= Post.objects.filter(id__in= stored_posts)
            context["posts"]= posts
            context["has_posts"]= True
            
            
        return render(request, "blog/stored-posts.html", context)
    
    def post(self, request):
        stored_posts = request.session.get("stored_posts")
        post_id = int(request.POST["post_id"])
        if stored_posts is None:
            stored_posts = []

        if post_id not in stored_posts:
            stored_posts.append(post_id)
            request.session["stored_posts"]= stored_posts
            
        return HttpResponseRedirect("/")
