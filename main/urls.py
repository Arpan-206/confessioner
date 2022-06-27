from django.urls import path
from . import views

urlpatterns = [
	path('', view=views.index, name='index'),
	path('register/', view=views.register, name='register'),
	path('logout/', view=views.logout_view, name='logout'),
	path('login/', view=views.login_view, name='login'),
    path('community/<int:id>', view=views.community_view, name='community'),
    path('mod/<int:id>', view=views.comm_mod, name='mod'),
    path('mod/add/<int:id>', view=views.comm_mod_add, name='mod_add'),
    path('mod/remove/<int:id>', view=views.comm_mod_remove, name='mod_remove'),
    path('join/', view=views.join_comm, name='join'),
    path('create_community/', view=views.create_community, name='create_community'),
    path('comment/<int:id>', view=views.comment, name='comment'),
    path('communities/', view=views.communities, name='communities'),
	path('confess/', view=views.confess, name='confess'),
    path('confession/<int:id>', view=views.confession, name='confession'),
    path('like/<int:id>', view=views.toggle_like, name="toggle_like"),
	path('tos/',view=views.tos, name='tos'),
	path('privacy/',view=views.privacy, name='privacy')
]