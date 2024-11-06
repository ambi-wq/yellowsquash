from django.urls import path
from django.conf.urls import url

from apps.group.views import CreateGroup, ListCategories, GetGroupDetails, MyGroups, JoinedGroups, LeaveGroup, \
    CreateGroupPost, PendingApprovalGroupPost, ApprovalGroupPost, JoinGroup, ApproveJoinGroup, PendingApprovalGroup, \
    LikeGroupPost, InviteToGroup, PendingInviteGroup, ApproveInviteGroup, SearchGroups, SearchUsers, MyPosts, \
    GroupPosts, GetGroupsForCategories, GetGroupMembers, EditGroup, RemovePost, RemoveGroup, DiscoverGroups, \
    ExpertGroups, ForYouPosts, CreateGroupComment, GetPostComments, RemoveMemberGroup

urlpatterns = [
    path('list-group-categories/', ListCategories.as_view(), name="Categories list"),

    path('my-groups/', MyGroups.as_view(),name="My Group list, Created By Requested User"),
    path('joined-groups/', JoinedGroups.as_view(),name="Group list, Joined By Requested User"),

    path('create-group/', CreateGroup.as_view(), name="Create Group"),
    path('group-details/<id>', GetGroupDetails.as_view(), name="Get Group"),
    path('leave-group/', LeaveGroup.as_view(), name="Leave Group"),

    path('invite-to-group/', InviteToGroup.as_view(), name="Invite People To Group"), #fetch all users and invite? where to invite? screens?
    # path('home-posts/', ListGroups.as_view(), name="Homepage Posts"), #Paging Support, {noOfPages: Infinite maybe? or limit on dates, pageSize: 5, items: []}
    path('pending-invite-group/', PendingInviteGroup.as_view(), name="Invite People To Group"),
    # fetch all users and invite? where to invite? screens?

    path('accept-invite-group/', ApproveInviteGroup.as_view(), name="Invite People To Group"),


    # path('group-posts/', ListGroups.as_view(), name="Group list"), #Paging Support, {noOfPages: 2, pageSize: 5, items: []}
    # path('upload-post-media/', ListGroups.as_view(), name="Upload Post media"), #Seperate call? image array
    # comments, moedration at admin side

    path('create-group-post/', CreateGroupPost.as_view(), name="Create Group Post"),
    path('pending-approval-group-post/', PendingApprovalGroupPost.as_view(), name="Pending Approval for Group Post"),
    path('approval-group-post/', ApprovalGroupPost.as_view(), name="Manage Approval for Group Post"),
    path('like-group-post/', LikeGroupPost.as_view(), name="Like Group Post"),

    path('join-group/', JoinGroup.as_view(), name="Join Group"),
    path('pending-approval-group/', PendingApprovalGroup.as_view(), name="Pending Group Approval"),
    path('approval-join-group/', ApproveJoinGroup.as_view(), name="Approve Group"),
    path('search-group/<text>', SearchGroups.as_view(), name="Search Groups"),
    path('search-user/<text>', SearchUsers.as_view(), name="Search Users"),
    path('my-posts/<group>', MyPosts.as_view(), name="My Posts"),
    path('group-posts/<group>/<page_no>/<page_size>', GroupPosts.as_view(), name="Groups Posts"),
    path('group-for-categories/', GetGroupsForCategories.as_view(), name="Group for Categories"),
    path('group-members/<group_id>/<top_members>/<top_admins>/<top_invites>', GetGroupMembers.as_view(), name="Group Members"),
    path('edit-group/', EditGroup.as_view(), name="Edit Group"),
    path('remove-group-post/', RemovePost.as_view(), name="Remove Group Post"),
    path('remove-group/', RemoveGroup.as_view(), name="Remove Group"),
    path('remove-member-group/', RemoveMemberGroup.as_view(), name="Remove Member Group"),


    path('discover-groups/<top>', DiscoverGroups.as_view(), name="Discover Group"),
    path('expert-groups/<top>', ExpertGroups.as_view(), name="Expert Groups"),
    path('for-you-posts/<page_no>/<page_size>/<max>', ForYouPosts.as_view(), name="Groups Posts"),
    path('create-post-comment/', CreateGroupComment.as_view(), name="Add Comment on Group Post"),
    path('get-post-comments/<post>', GetPostComments.as_view(), name="Get post comments"),

]
